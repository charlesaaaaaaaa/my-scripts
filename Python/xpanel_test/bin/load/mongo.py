import datetime
import multiprocessing
import random
import string
import threading
import time
import pymongo
import collections
import bin.other_opt
from bin import *


class LoadMg:
    def __init__(self):
        host, port, user, passwd = [], [], [], []
        conf = bin.other_opt.getconf().getXpanelInfo()
        host_port = conf['mongodb_host_port'].replace(', ', ',').split(',')
        user_pass = conf['mongodb_user_pass'].replace(', ', ',').split(',')
        self.field_list = ['txt', 'num', 'thread']
        for i in range(len(host_port)):
            hp, up = host_port[i].split(':'), user_pass[i].split('@')
            host.append(hp[0])
            port.append(hp[1])
            user.append(up[0])
            passwd.append(up[1])
        self.host, self.port, self.user, self.passwd = host, port, user, passwd

    def conn_mongo(self, tb='testtb', db='testdb', host_num=0):
        myclient = pymongo.MongoClient('mongodb://%s:%s/' % (self.host[host_num], self.port[host_num]))
        mydb = myclient[db]
        mytb = mydb[tb]
        return mytb

    def drop_create_table(self, tb='testtb', db='testdb', host_num=0):
        try:
            myclient = pymongo.MongoClient('mongodb://%s:%s/' % (self.host[host_num], self.port[host_num]))
            mydb = myclient[db]
            collections_list = mydb.list_collection_names()
            if tb in collections_list:
                print('删除已存在的集合 [%s]' % tb)
                mydb.drop_collection(tb)
            mydb.create_collection(tb)
            return 1
        except Exception as err:
            print(str(err))
            return 0

    def show_cur_datasize(self, tb='testtb', db='testdb', compare=0):
        # 展示源和目标的数据量
        source_datasize = self.conn_mongo(tb=tb, db=db, host_num=0).count_documents({})
        target_datasize = self.conn_mongo(tb=tb, db=db, host_num=1).count_documents({})
        print('当前表：[%s.%s]\t源mongodb数据量为: [%s]\t目标mongodb数据量为: [%s]' % (db, tb, source_datasize, target_datasize))
        if compare == 1:
            return source_datasize, target_datasize

    def compare_datasize(self, tb='testtb', db='testdb', process=10, skip_compare_size=0):
        source_datasize, target_datasize = 0, -1
        compare_times = 0
        # 先调用前面的那个统计数据量的方法来对比数据量是否一致
        old_target_size = 0
        same_target_times = 0
        start_time = time.time()
        while source_datasize != target_datasize and compare_times <= 10000:
            source_datasize, target_datasize = self.show_cur_datasize(tb=tb, db=db, compare=1)
            compare_times += 1
            if target_datasize > source_datasize:
                print('目标表[%s.%s]数据量[%s]超过源表数据量[%s], 本次查询失败' % (db, tb, target_datasize, source_datasize))
                if skip_compare_size == 0:
                    return ['mongodb', 0]
                else:
                    break
            if target_datasize == old_target_size:
                same_target_times += 1
            else:
                same_target_times = 0
            old_target_size = target_datasize
            if same_target_times >= 20:
                print('循环查询目标表[%s.%s]超过20次无变化，本次查询失败' % (db, tb))
                if skip_compare_size == 0:
                    return ['mongodb', 0]
                else:
                    break
            time.sleep(10)
        end_time = time.time()
        print('本次检查源表与目标表数据量完成，共花费[%s]秒' % (end_time - start_time))
        # 数据量一致的时候调用find函数，第一个空的{}表示查看所有数据， 第二个{}里面是看其字段名，为1就是要查看，为0就是不要查看
        second_dict = {'_id': 0}
        # second_dict就是find方法的第二个字典，这边是根据self.field_list这个列表生成的，默认_id这个字段是不显示的
        for i in self.field_list:
            second_dict.update({i: 1})
        # for field in ['txt', 'num', 'thread']:
        # 获取source和target所有数据，并以num和thread列以升序排序
        source_data = self.conn_mongo(tb=tb, db=db, host_num=0).find({}, second_dict).sort([('num', 1), ('thread', 1)]).allow_disk_use(True)
        target_data = self.conn_mongo(tb=tb, db=db, host_num=1).find({}, second_dict).sort([('num', 1), ('thread', 1)]).allow_disk_use(True)
        source_data_list, target_data_list = [], []
        for txt in source_data:
            source_data_list.append(txt)
        for txt in target_data:
            target_data_list.append(txt)
        target_data, source_data = {}, {}
        # 当目标表数据量大于源表数据量时，就去检查其重复的数据，一般情况下是重复插入的概率比较大
        # 如果没有重复的数据再去对比是否存在于源表中，这个时候才可能是cdc插入了源表不存在的数据
        if len(target_data_list) > len(source_data_list):
            print('开始检查目标表是否存在重复的数据')
            rep_times = 0
            for i in range(len(target_data_list)):
                # 因为是在获取时就排好序的，所以直接用当前的数据和上一条数据对比是否相同就行
                if target_data_list[i] == target_data_list[i - 1]:
                    print(target_data_list[i], target_data_list[i - 1])
                    rep_times += 1
            print('目标表共重复了【%s】次' % rep_times)
            if rep_times > 0:
                return ['mongodb', 0]

        # 根据前面生成的源和目标表的数据列表进行多进程检查，检查目标集合的每一条数据是否都存在于源集合上
        def compare_threads(process_num, total_process, shared_int):
            # process_num 要从1开始，不能从0开始
            # 通过当前的thread号和总thread数量来确定本次这个thread负责的范围是多少
            succ_res = 1
            total_len = len(target_data_list)
            each_thread_size = int(total_len / total_process)
            extra_thread_size = total_len % total_process
            if extra_thread_size > 0:
                if process_num < extra_thread_size:
                    start_row = (process_num - 1) * each_thread_size + process_num
                    end_row = process_num * each_thread_size + process_num + 1
                else:
                    start_row = (process_num - 1) * each_thread_size + total_process
                    end_row = process_num * each_thread_size + total_process + 1
                if process_num == total_process:
                    end_row = total_len
            else:
                start_row = (process_num - 1) * each_thread_size
                end_row = process_num * each_thread_size
            print('process_%s: 检查[%s - %s]行数据' % (process_num, start_row, end_row))
            time.sleep(1)
            # 这里把目标表和源表要检测的范围给到另外的列表里面，这样列表的数量不会太多从而获取元素的时间过长
            cur_source_list, cur_target_list = [], []
            start_time = time.time()
            for i in range(start_row, end_row):
                cur_target_list.append(target_data_list[i])
                cur_source_list.append(source_data_list[i])
            end_time = time.time()
            spend_time = end_time - start_time
            print('process_%s init花了%ss' % (process_num, spend_time))
            time.sleep(5)
            for i in range(len(cur_target_list)):
                print('\r检查第[%s]条，[%s]' % (i, cur_target_list[i]), end='')
                if cur_target_list[i] != cur_source_list[i]:
                    succ_res = 0
                    print('\nERROR: target%s 不存在于source表里\n' % target_data_list[i])
            end_time2 = time.time()
            spend_time2 = end_time2 - end_time
            res_txt = 'process_%s compare花了%ss' % (process_num, spend_time2)
            if succ_res == 1:
                res_txt += ', 成功'
            else:
                res_txt += ', 失败'
            shared_int.value += succ_res

        tl = []
        succ_times = multiprocessing.Manager().Value('i', 0)
        for num in range(process):
            process_num = num + 1
            # t = threading.Thread(target=compare_threads, args=(thread_num, threads,))
            t = multiprocessing.Process(target=compare_threads, args=(process_num, process, succ_times))
            tl.append(t)
            t.start()
        for t in tl:
            t.join()
        if succ_times == process:
            return ['mongodb', 1]
        else:
            return ['mongodb', 0]

    def find_all(self, tb='testtb', db='testdb'):
        second_dict = {'_id': 0}
        for i in self.field_list:
            second_dict.update({i: 1})
        # 获取source和target所有数据，并以num和thread列以升序排序
        source_data = self.conn_mongo(tb=tb, db=db, host_num=0).find({}, second_dict).sort([('num', 1), ('thread', 1)])
        target_data = self.conn_mongo(tb=tb, db=db, host_num=1).find({}, second_dict).sort([('num', 1), ('thread', 1)])
        source_list, target_list = [], []
        for i in source_data:
            source_list.append(i)
        for i in target_data:
            target_list.append(i)
        for i in range(len(source_list)):
            if source_list[i] != target_list[i]:
                print('第[%s]条\nsource【%s】\ntarget【%s】' % (i, source_list[i], target_list[i]))

    def gen_data(self, num, thread_num):
        # 随机产生一个从小到大且不重复的数字列表，数量随机
        insert_type = sorted(set(random.choices(range(1, 8), k=7)))

        def text():
            txt = ''.join(random.choices(string.ascii_letters, k=random.randint(25, 50)))
            return txt

        def float_type():
            float_num = random.uniform(0, 10000)
            return float_num

        def time_type():
            cur_time = datetime.datetime.now()
            return cur_time

        def generate_mac(separator=":"):
            # 生成6个字节的十六进制数（0x00 ~ 0xFF）
            mac_bytes = [random.randint(0x00, 0xff) for _ in range(6)]
            # 将字节格式化为2位十六进制字符串，并用分隔符连接
            mac = separator.join(f"{byte:02x}" for byte in mac_bytes)
            return mac

        def generate_ipv(sep=".", ipv=4):
            # ipv = [4] or [6]
            # 生成[ipv]个256的str字符
            net_bytes = [str(random.randint(0, 256)) for _ in range(ipv)]
            # 通过join转化成ipv[ipv]地址
            net = sep.join(net_bytes)
            return net

        insert_dict = {}
        # 通过最开始随机生成的数字列表来确定要生成的是什么类型的数据
        for i in insert_type:
            if i == 1:
                insert_dict.update({"txt": text()})
            elif i == 2:
                insert_dict.update({"float": float_type()})
            elif i == 3:
                insert_dict.update({"cur_time": time_type()})
            elif i == 4:
                insert_dict.update({"mac": generate_mac()})
            elif i == 5:
                insert_dict.update({"ipv4": generate_ipv(ipv=4)})
            elif i == 6:
                insert_dict.update({"ipv6": generate_ipv(ipv=6)})
            elif i == 7:
                insert_dict.update({"ip": {"ipv4": generate_ipv(ipv=4), "ipv6": generate_ipv(ipv=6)}})
        insert_dict.update({"num": num, "thread": thread_num})
        return insert_dict

    def multi_load(self, thread=1, each_thread_size=10000, tb='testtb', db='testdb', host_num=1, drop=1):
        # 因为mongo如果在指定db时如果db不存在就会创建对应的db，故这个方法不用创建db，直接创建集合就行
        print('\n开始操作mongodb库表并灌数据：%s:%s' % (db, tb))

        def single_thread(tread_num):
            if each_thread_size > 100:
                data = []
                cur_size = 1
                while cur_size <= each_thread_size:
                    data.append(self.gen_data(cur_size, tread_num))
                    cur_size += 1
                    if cur_size % 100 == 0:
                        self.conn_mongo(tb=tb, db=db).insert_many(data)
                        data = []
                if data:
                    self.conn_mongo(tb=tb, db=db).insert_many(data)
            else:
                data = []
                for i in range(1, each_thread_size + 1):
                    data.append(self.gen_data(i, tread_num))
                self.conn_mongo(tb=tb, db=db).insert_many(data)

        tl = []
        try:
            if drop == 1:
                for i in range(len(self.host)):
                    print('先创建集合%s.%s, mongodb://%s:%s/' % (db, tb, self.host[i], self.port[i]))
                    self.drop_create_table(tb=tb, db=db, host_num=i)
                    print('创建成功')
                self.show_cur_datasize(tb=tb, db=db)
            print('开始灌数据')
            for i in range(thread):
                print('thread_%s 开始中>>>' % i)
                t = threading.Thread(target=single_thread, args=(i, ))
                tl.append(t)
                t.start()
            for i in tl:
                i.join()
            print('完成')
            self.show_cur_datasize(tb=tb, db=db)
            return 1
        except Exception as err:
            print(str(err))
            return 0

    def get_first_id(self):
        conn = self.conn_mongo()
        res = conn.find_one()['_id']
        return res
