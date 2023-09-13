import multiprocessing

from bin.connection import *
from bin.getconf import *


# from threading import Thread
# import sys

def create_table():
    db = readcnf().getKunlunInfo()['db']
    sql = "create table user_ops(" \
          "id serial primary key, " \
          "when timestamp not null, " \
          "user_id bigint not null, " \
          "ops bigint, " \
          "type char(32) not null, " \
          "target bigint not null, " \
          "target_type bigint not null, " \
          "url varchar(256) not null," \
          "tags text) partition by hash(id);"
    connPg().pgNotReturn(db, sql)
    for i in range(16):
        table_num = i + 1
        sql = 'create table user_ops_%s partition of user_ops for values with ' \
              '(MODULUS %s, REMAINDER %s);' % (table_num, '16', i)
        connPg().pgNotReturn(db, sql)


class load():
    def __init__(self):
        # self.db = readcnf().getKunlunInfo()['db']
        self.localTime = time.localtime()
        self.conf = readcnf().getTestInfo()
        self.first_page = ['zettadb', 'kunlunbase', 'baidu', 'qq', 'sohu', 'tieba', 'bilibili']
        self.second_page = ['doc', 'front_page', 'products', 'support', 'downloads', 'news', 'partners', 'join_us',
                            'contact_us']
        self.third_page = ['wiki', 'ticket', 'user']
        self.big_mon = [1, 3, 5, 7, 8, 10, 12]
        self.small_mon = [4, 6, 9, 11]
        self.typeList = ['click', 'dbl_click', 'hover', 'rclick', 'sel', 'copy']
        self.target_count = random.randint(10000, 10900)
        self.target_type_count = random.randint(1000, 1100)

    def create_rul(self):
        first_page = self.first_page
        second_page = self.second_page
        third_page = self.third_page
        url = 'www.'
        url_level = random.randint(1, 3)
        for i in range(1, url_level + 1):
            if i == 1:
                url += random.choice(first_page) + '.com'
            elif i == 2:
                url += '/' + random.choice(second_page)
            elif i == 3:
                url += '/' + random.choice(third_page)
            # else:
            #     tmp = ''
            #     len = random.randint(5, 25)
            #     for i in range(len):
            #         tmp += random.choice('qwertyuioplkjhgfdsazxcvbnmMNBVCXZASDFGHJKLPOIUYTREWQ1234567890._-')
            #     url += '/' + tmp
        return url

    def time_stamp(self, mon):
        t = self.localTime
        month = t.tm_mon - mon
        day, year = 0, t.tm_year
        if t.tm_mon <= mon:
            month = t.tm_mon + (12 - mon)
            year = t.tm_year - 1
        if month in self.big_mon:
            day = random.randint(1, 31)
        elif month in self.small_mon:
            day = random.randint(1, 30)
        elif month == 2:
            day = random.randint(1, 28)
        if mon == 0:
            day = random.randint(1, t.tm_mday)
        hour = random.randint(0, 23)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        timeStamp = '%s-%s-%s %s:%s:%s' % (year, month, day, hour, minute, second)
        return timeStamp

    def create_tags(self):
        tagList = ["games", "video", "视频", "流媒体", "tv_show", "movies", "funny", "搞笑", "日常", "相亲"]
        # tag_num = random.randint(1, 5)
        # tags = ''
        # tmpList = []
        # for i in range(tag_num):
        #     randCho = random.choice(tagList)
        #     while randCho in tmpList:
        #         randCho = random.choice(tagList)
        #     tmpList.append(randCho)
        #     if i == 0:
        #         tags = randCho
        #     else:
        #         tags += ', ' + randCho
        tags = random.choice(tagList)
        return tags

    def user_data(self, user_id, mon):
        sql = 'insert into user_ops(timestamp, user_id, ops, type, target, target_type, url, tags) values'
        typeList = self.typeList
        target_times = random.randint(50, 200)
        target_type_times = random.randint(5, 20)
        target_list = []
        target_type_list = []
        for i in range(target_type_times):
            target_type_tmp = random.randint(1, self.target_type_count)
            target_type_list.append(target_type_tmp)
        for i in range(target_times):
            target = random.randint(1, self.target_count)
            target_list.append(target)
            target_type = random.choice(target_type_list)
            timestamp = self.time_stamp(mon)
            ops = random.randint(1, 5)
            type = random.choice(typeList)
            url = self.create_rul()
            tags = self.create_tags()
            tmpData = "('%s', %d, %d, '%s', %d, %d, '%s', '%s')" % (
            timestamp, user_id, ops, type, target, target_type, url, tags)
            if i == 0:
                sql += tmpData
            else:
                sql += ',' + tmpData

        return sql

    def datas(self):
        conf = self.conf
        # db = self.db
        processes = int(conf['processes'])
        user_count = random.randint(10000000, 10100000)
        writeLog('当前随机构造 %s 个用户' % user_count)
        each_thread_count = int(user_count / processes)
        extra_each_thread = user_count % processes
        start_num = 0
        end_num = 0
        user_batch = int(conf['user_batch'])
        process_position_dict = {}
        for i in range(processes):
            process_num = i + 1
            process_name = 'process_%s' % process_num
            if process_num == 1:
                if extra_each_thread >= process_num:
                    end_num = start_num + each_thread_count + 1
                else:
                    end_num = start_num + each_thread_count
            else:
                if extra_each_thread >= process_num:
                    start_num = end_num
                    end_num = start_num + each_thread_count + 1
                else:
                    start_num = end_num
                    end_num = start_num + each_thread_count
            tmpDict = {process_name: [start_num, end_num]}
            process_position_dict.update(tmpDict)

        # def loadData(threadsName, signal_thread_list, mon):
        #     writeLog('开始 %s , 共构造 %s 个用户' % (threadsName, signal_thread_list[1] - signal_thread_list[0]))
        #     for i in range(signal_thread_list[0], signal_thread_list[1]):
        #         sql = self.user_data(i, mon)
        #         #writeLog('%s user_id: %s' % (threadsName, i))
        #         #connPg().pgNotReturn(db, sql)
        #     writeLog('%s 构造完成' % threadsName)
        # l = []
        # for thead_name in thread_position_dict:
        #     # 此时的i就是线程的名字
        #     mon = random.randint(0, 3)
        #     signal_thread_list = thread_position_dict[thead_name]
        #     p = Thread(target=loadData, args=[thead_name, signal_thread_list, mon])
        #     l.append(p)
        #     p.start()

        def loadData(threadsName, signal_thread_list, mon, lock):
            lock.acquire()
            writeLog('开始 %s , 共构造 %s 个用户' % (threadsName, signal_thread_list[1] - signal_thread_list[0]))
            cur_batchNum = 0
            cur_tran = "BEGIN;"
            for i in range(signal_thread_list[0], signal_thread_list[1]):
                cur_batchNum += 1
                sql = self.user_data(i, mon)
                if cur_batchNum == 1:
                    cur_tran = "BEGIN;"
                    cur_tran += sql
                elif cur_batchNum == user_batch or i == signal_thread_list[1] - 1:
                    cur_tran += sql
                    cur_tran += "COMMIT;"
                    cur_batchNum = 0
                    # connPg().pgNotReturn(db, sql)
                else:
                    cur_tran += sql
                    # writeLog('%s user_id: %s' % (threadsName, i))
            writeLog('%s 构造完成' % threadsName)

        l = []
        for process_name in process_position_dict:
            # 此时的i就是进程的名字
            lock = multiprocessing.Lock()
            mon = random.randint(0, 3)
            signal_thread_list = process_position_dict[process_name]
            p = multiprocessing.Process(target=loadData, args=(process_name, signal_thread_list, mon, lock,))
            l.append(p)
            p.start()
