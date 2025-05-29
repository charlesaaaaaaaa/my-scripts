import multiprocessing
from base.other.connect import *
from base.other.info import *
from base.other.sys_opt import *
from base.other import getconf
import time
import threading


class TranSfer:
    def __init__(self, comp_list):
        # comp_list = info.node_info().show_all_running_computer() 这个方法里面的任意二级列表，也就是要指定运行的计算节点信息
        self.comp_list = comp_list
        self.func_location = './case/util/transfer_function.sql'
        self.create_location = './case/util/transfer_create.sql'

    def prepare(self, partition_shards_list=None, only_create_table=None, partition_num=0):
        # partition_shards_list = info.node_info().show_all_running_shard_id()
        # only_create_table 指定任意数都会只创建表，不指定参数则会创建1000条用户数据
        comp = self.comp_list
        func_location = self.func_location
        create_location = self.create_location
        show_topic('创建db/表/函数', 2)
        sql1 = 'drop database if exists test;'
        sql = 'create database test;'
        con = Pg(host=comp[0], port=comp[1], user=comp[2], pwd=comp[3], db='postgres')
        con.ddl_sql(sql=sql1)
        con.ddl_sql(sql=sql)
        con.close()
        if not partition_shards_list and partition_num == 0:
            create_comm = 'psql postgres://%s:%s@%s:%s/test -f %s' % (comp[2], comp[3], comp[0], comp[1], create_location)
            print('%s\n%s' % (sql, create_comm))
            subprocess.run(create_comm, shell=True)
        else:
            if partition_shards_list:
                partition_num = 2 * len(partition_shards_list)
            type_sql_list = ["create type res_t as enum('0', '1');",
                             "create type status_t as enum('using', 'delete', 'freeze', 'unfreeze', 'create', 'notexist');"]
            create_list = [['CREATE TABLE history(id bigserial primary key, tsf_id int not null, b_tsf_id int not null, amount int not null, '
                            'res res_t not null, opt_date timestamp not null, tips text) partition by hash (id);', 'history'],
                           ["create table test_user(id serial primary key, name text not null, password text not null, status status_t not null, "
                            "update_times int not null) partition by hash (id);", "test_user"],
                           ["create table amount(id serial primary key, u_id int not null, u_amount int not null) partition by hash (id);", "amount"],
                           ["create table opt_history(id serial primary key, u_id int not null, opt text not null, opt_date timestamp not null, "
                            "opt_res res_t not null) partition by hash (id);", "opt_history"]]
            insert_list = ["insert into test_user(name, password, status, update_times) value('root', 'root', 'using', 0);",
                           "insert into opt_history(u_id, opt, opt_date, opt_res) value(1, 'create', current_timestamp(), '1');"]
            con = Pg(host=comp[0], port=comp[1], user=comp[2], pwd=comp[3], db='test')
            show_topic('创建type')
            for i in type_sql_list:
                print(i)
                con.ddl_sql(sql=i)
            show_topic('创建分区表')
            for i in create_list:
                print(i[0])
                con.ddl_sql(sql=i[0])
                part_num = 0
                for shard_id in partition_shards_list:
                    for num in range(2):
                        sql = 'create table %s_%s partition of %s for values with (MODULUS %s, REMAINDER %s) with (shard = %s);' \
                              '' % (i[1], part_num, i[1], partition_num, part_num, shard_id[0])
                        print(sql)
                        part_num += 1
                        con.ddl_sql(sql=sql)
            for i in insert_list:
                print(i)
                con.ddl_sql(sql=i)
        function_comm = 'psql postgres://%s:%s@%s:%s/test -f %s' % (comp[2], comp[3], comp[0], comp[1], func_location)
        print(function_comm)
        subprocess.run(function_comm, shell=True)

        if only_create_table == None:
            show_topic('增加1000用户数', 2)

            for i in range(2, 1001):
                sql = "select * from change_user_status(%s, 'using')" % i
                con = Pg(host=comp[0], port=comp[1], user=comp[2], pwd=comp[3], db='test')
                # print('\r增加用户%s' % i, end='')
                try:
                    res = con.sql_with_result(sql=sql)
                    if res == 0:
                        print('user[%s]创建失败' % i)
                except Exception as err:
                    print(err)
                    con.sql_with_result(sql=sql)

    def loadwork(self, threads_num, sleep_time=-1, work_times=0):
        # sleep_time 就是每个sql语句的之前的休眠时间，不指定就0到30s之间随机选择，指定为0则不休眠
        # work_times 就是连续执行多少个sql才进行sleep, 默认为0， 为0时则在0到1000之间随机选择，每次休眠时都会随机选择一次
        comp = self.comp_list
        write_log.w2File().print_log('开始[%s]进程转账负载' % threads_num)
        # 这个文件可以认为是一个标志位，存在则继续灌，不存在则该方法停止
        loadword_flag = './log/tmp_loadwork.log'
        with open(loadword_flag, mode='w') as f:
            f.write('running...')
            f.close()

        def run_case():
            w_times = 0
            w_work_times = work_times
            con = Pg(host=comp[0], port=comp[1], user=comp[2], pwd=comp[3], db='test')
            while True:
                start_flag = os.path.exists(loadword_flag)
                if str(start_flag) == 'False':
                    break
                if work_times == 0:
                    if w_times == 0:
                        w_work_times = random.randint(1, 1000)
                w_times += 1
                # 本次测试主要是有两种情况，[0]是用户修改，目前权重是千分之一；其它值是转账操作
                random1 = random.randint(1, 1002)
                # 当前操作的用户id从2开始到1020，实际上只到1000，多出的20个id如果不是创建用户的话则结果必定是失败的
                user1 = random.randint(1, 1110)
                if user1 > 1010:
                    user1 = 1
                try:
                    if random1 > 1000 and user1 != 1:
                        # 修改用户状态操作
                        random_list = ['using', 'delete', 'freeze', 'unfreeze']
                        weight = [0.75, 0.05, 0.1, 0.1]
                        status = random.choices(population=random_list, weights=weight, k=1)
                        sql = "select * from change_user_status(%s, '%s')" % (user1, status[0])
                        # print(sql)
                        con.ddl_sql(sql=sql)
                    else:
                        # 用户转账操作
                        user2 = random.randint(2, 1001)
                        if user1 == 1:
                            amount = random.randint(1000000, 100000000)
                        else:
                            amount = random.randint(1, 9999)
                        while user2 == user1:
                            user2 = random.randint(2, 1001)
                        sql = 'CALL transfer_case(%s, %s, %s)' % (user1, amount, user2)
                        con.ddl_sql(sql=sql)
                except Exception as err:
                    amount = random.randint(1000, 10000)
                    # 如果错误是钱不够导致则有80%的概率充值任意金额
                    if err == '转账者钱不够':
                        random3 = random.randint(1, 100)
                        if random3 < 20:
                            sql = 'CALL transfer_case(%s, %s, %s)' % (0, amount, user1)
                            con.ddl_sql(sql=sql)

                def sleep_act():
                    if sleep_time == -1:
                        slt = random.randint(0, 30)
                        if slt != 0:
                            time.sleep(slt)
                    elif sleep_time > 0:
                        time.sleep(sleep_time)

                if w_times == w_work_times:
                    sleep_act()

        for i in range(threads_num):
            p = multiprocessing.Process(target=run_case)
            p.start()

    def diff_res(self, comp_list_slave, tb_history=None, tb_test_user=None, tb_amount=None, tb_opt_history=None):
        # 这里要指定一个备计算节点
        # 另外四个参数默认是None，每个表在该备计算节点里面对应的db和表名， 如tb_history=['test': 'history_a']
        # # 不指定的情况下则代表这个备和主的表和db都是相同未改变的
        comp1 = self.comp_list
        comp2 = comp_list_slave
        show_topic('检查一致性', 2)

        def get_tmpres(comp_list, db, sql):
            pg = connect.Pg(host=comp_list[0], port=comp_list[1], user=comp_list[2], pwd=comp_list[3], db=db)
            res = pg.sql_with_result(sql=sql)
            return res

        def check_rows(tb_name, slave_info):
            try:
                tmp_res1 = 1
                print('对比主节点[test.%s]表， 备节点[%s.%s]表' % (tb_name, slave_info[0], slave_info[1]), end='')
                # 不是test_user的表只检查备表的[id=1到最大id值]这个范围里面的行是否一致
                if tb_name != 'test_user':
                    sql = 'select max(id) from %s;' % slave_info[1]
                    max_id = get_tmpres(comp_list=comp2, db=slave_info[0], sql=sql)[0][0]
                    print(', max_id = %s' % max_id)
                    sql = 'select * from %s where id <= %s order by id;' % (slave_info[1], max_id)
                    master_res = get_tmpres(comp_list=comp1, db='test', sql=sql)
                    slave_res = get_tmpres(comp_list=comp2, db=slave_info[0], sql=sql)
                    master_cur_index, slave_cur_index = 0, 0
                    # 开始对里面的值一个个的对比
                    for i in range(len(master_res)):
                        master_cur_res = master_res[master_cur_index]
                        slave_cur_res = slave_res[slave_cur_index]
                        if int(master_cur_res[0]) > int(slave_cur_res[0]):
                            show_topic('当前主节点[%s]表缺少id=%s的数据' % (tb_name, slave_cur_res[0]), 3)
                            slave_cur_index += 1
                            continue
                        elif int(master_cur_res[0]) < int(slave_cur_res[0]):
                            show_topic('当前备节点[%s]表缺少id=%s的数据' % (tb_name, master_cur_res[0]), 3)
                            master_cur_index += 1
                            continue
                        else:
                            # 这边就直接对比结果了，没什么好说的
                            if master_cur_res != slave_cur_res:
                                show_topic('当前主备的[%s]表id=%s的行结果不一致' % (tb_name, id), 3)
                                tmp_res1 = 0
                        master_cur_index += 1
                        slave_cur_index += 1
                else:
                    sql = 'select id from %s;' % slave_info[1]
                    id_tuple = get_tmpres(comp_list=comp2, db=slave_info[0], sql=sql)
                    diff_list = []
                    print('%s, %s' % (tb_name, slave_info))
                    for uid in id_tuple:
                        tmp_res_list = []
                        for tmp_info in ['test', tb_name], slave_info:
                            sql = 'select * from %s where id = %s' % (tmp_info[1], uid[0])
                            tmp_res = get_tmpres(comp_list=comp1, db=tmp_info[0], sql=sql)[0]
                            tmp_res_list.append(tmp_res)
                        if tmp_res_list[0][-1] == tmp_res_list[1][-1]:
                            if tmp_res_list[0] != tmp_res_list[1]:
                                diff_list.append(tmp_res_list[0][0])
                    if diff_list:
                        show_topic('当前主备的[test_user]表有以下行与预期结果不一致' % diff_list, 3)
                        tmp_res1 = 0
                    else:
                        show_topic('本次检查表[%s]数据一致' % tb_name)
            except Exception as err:
                print(str(err))
                return 0
            return tmp_res1

        if not tb_amount:
            tb_amount = ['test', 'amount']
        if not tb_history:
            tb_history = ['test', 'history']
        if not tb_test_user:
            tb_test_user = ['test', 'test_user']
        if not tb_opt_history:
            tb_opt_history = ['test', 'opt_history']
        table_info_list = [['amount', tb_amount], ['history', tb_history], ['test_user', tb_test_user], ['opt_history', tb_opt_history]]
        real_res = 1
        for tb_info in table_info_list:
            try:
                tmp_res2 = check_rows(tb_info[0], tb_info[1])
                if tmp_res2 == 0:
                    real_res = 0
            except Exception as err:
                print(err)
                return 0
        return real_res


class StorageState:

    def show_cluster_general_job_log(self):
        show_topic('查看 [cluster_general_job_log] 结果', 2)
        sql = 'select status from  cluster_general_job_log  order by id desc limit 1;'
        res = info.node_info().get_res(sql)[0][0]
        while res == 'ongoing':
            res = info.node_info().get_res(sql)[0][0]
            time.sleep(3)
        print('%s: [%s]' % (sql, res))
        if res == 'done':
            res = 1
        else:
            res = 0
        return res

    def show_variables(self, storage_node_info, sql):
        res_list = []
        for i in storage_node_info:
            res = My(host=i[0], port=i[1], user=i[2], pwd=i[3], db='mysql').sql_with_result(sql)[0][1]
            res_list.append(res)
        return res_list

    def show_read_only(self, cluster_id_list=None, enable_write_cluster_list=None):
        # cluster_id_list, 就是把所有要检查的cluster_id放到一个列表里面, 默认不指定的情况下就是获取所有正在运行的cluster_id
        # enable_write_cluster_list, 就是指定那个cluster_id是有可写节点的，默认不指定的情况下是所有cluster_id的shard都有一个可写节点
        # 当未指定cluster_id_list时，则生成一个所有正在运行的cluster_id的列表
        node_result = 1
        ewcl = enable_write_cluster_list
        if cluster_id_list == None:
            cluster_id_list = []
            cluster_id_tuple = node_info().show_all_running_cluster_id()
            for cluster_id in cluster_id_tuple:
                #cluster_id_list.append("cluster_%s" % cluster_id[0])
                cluster_id_list.append(cluster_id[0])
        if enable_write_cluster_list == None:
            ewcl = cluster_id_list
        write_log.w2File().print_log('检查cluster_id: %s, 其中可写的cluster为: %s' % (cluster_id_list, ewcl))
        cluster_dict = {}
        # 获取所选择的cluster_id的存储节点信息
        for cluster_id in cluster_id_list:
            #cluster = cluster_id.split('_')[1]
            cluster_sql = "select distinct(shard_id) from shard_nodes where db_cluster_id = %s;" % cluster_id
            shard_ids = info.node_info().get_res(cluster_sql)[0]
            shard_list = []
            for shard_id in shard_ids:
                shard_sql = 'select hostaddr, port, user_name, passwd, member_state from shard_nodes where shard_id = %s;' % shard_id
                nodes_info = info.node_info().get_res(sql=shard_sql)
                shard_dict = {shard_id: nodes_info}
                shard_list.append(shard_dict)
            tmp_dict = {cluster_id: shard_list}
            cluster_dict.update(tmp_dict)
        cluster_res_dict = {}
        # 开始对获取的信息进行判断
        for cluster_id_dict in cluster_dict:
            # cluster_id_dict_tmp = cluster_dict[cluster_id_dict]
            write_log.w2File().print_log("## cluster_%s:" % cluster_id_dict)
            cluster_res_list = []
            shard_res_dict = {}
            for shard_id_dict in cluster_dict[cluster_id_dict]:
                #write_log.w2File().print_log(shard_id_dict)
                enable_write_times = 0
                shard_res_list = []
                node_res_dict = {}
                for shard_id in shard_id_dict:
                    if cluster_id_dict in ewcl:
                        enable_write_times += 1
                    print("* shard_%s:" % shard_id)
                    for node in shard_id_dict[shard_id]:
                        #print(shard_id_dict[shard_id], shard_id)
                        #print("cluster_dict = %s\ncluster_id_dict = %s\nshard_id_dict=%s\n cluster_id_dict_tmp=%s" % (
                        #    cluster_dict, cluster_id_dict, shard_id_dict, cluster_id_dict_tmp
                        #))
                        #print(node)
                        member_state = node[4]
                        node_ip_host = "%s:%s" % (node[0], node[1])
                        node_res_list = []
                        my1 = connect.My(host=node[0], port=node[1], user=node[2], pwd=node[3], db='mysql')
                        my2 = connect.My(host=node[0], port=node[1], user=node[2], pwd=node[3], db='mysql')
                        sql1 = "show global variables like 'super_read_only'"
                        sql2 = "show global variables like 'read_only'"
                        res1 = str(my1.sql_with_result(sql1)[0][1])
                        res2 = str(my2.sql_with_result(sql2)[0][1])
                        node_res_list.append('super_read_only = [%s], read_only = [%s], %s' % (res1, res2, member_state))
                        node_res_dict.update({node_ip_host: node_res_list})
                        if member_state == 'source':
                            enable_write_times -= 1
                            if res1 == res2 == 'OFF' and enable_write_times >= 0:
                                pass
                            elif res1 == res2 == 'ON' and enable_write_times <= 0:
                                pass
                            else:
                                print(res1, res2, member_state, enable_write_times)
                                node_result -= 1
                        else:
                            if res1 == res2 == 'ON':
                                pass
                            else:
                                print(res1, res2, member_state, enable_write_times)
                                node_result -= 1
                        write_log.w2File().print_log("** %s -- %s" % (node_ip_host, node_res_list))
                shard_res_list.append(node_res_dict)
                shard_res_dict.update({'shard_%s' % shard_id_dict: node_res_dict})
            cluster_res_list.append(shard_res_dict)
            cluster_res_dict.update({'cluster_%s' % cluster_id_dict: cluster_res_list})
        if node_result != 1:
            print("当前主备关系不正常 %s" % node_result)
            node_result = 0
        return node_result
        # storage_node_info = node_info().show_all_running_storage()
        # super_readonly_sql = 'show variables like "super_read_only";'
        # readonly_sql = 'show variables like "read_only";'
        # super_readonly_dict = {"super_read_only": self.show_variables(storage_node_info, super_readonly_sql)}
        # readonly_dict = {"read_only": self.show_variables(storage_node_info, readonly_sql)}
        # # print(super_readonly_dict.values(), readonly_dict.values())
        # if str(super_readonly_dict.values()) == str(readonly_dict.values()):
        #     for i in range(len(storage_node_info)):
        #         show_res = '[%s:%s] super_read_only=[%s] read_only=[%s]' % (storage_node_info[i][0], storage_node_info[i][1],
        #                                                                           super_readonly_dict["super_read_only"][i], readonly_dict["read_only"][i])
        #         if super_readonly_dict["super_read_only"][i] == 'ON':
        #             show_res = 'shard备' + show_res
        #         else:
        #             show_res = 'shard主' + show_res
        #         print(show_res)
        # else:
        #     storage_node_list = []
        #     for i in storage_node_info:
        #         storage_node_list.append([i[0], i[1]])
        #     storage_node_dict = {"storage_node": storage_node_list}
        #     print('当前主备关系不正常')
        #     print(storage_node_dict)
        #     print(super_readonly_dict)
        #     print(readonly_dict)
        #     return 0
        # return 1

    def show_shard_master_tables(self, shard_id_list, database):
        res_list = []
        for shard_id in shard_id_list:
            sql = "SELECT table_name FROM information_schema.tables WHERE table_schema = '%s' " \
                  "ORDER BY table_name;" % database
            master = info.node_info().show_specify_shard_master_node(shard_id=shard_id)
            my = connect.My(host=master[0], port=master[1], user=master[2], pwd=master[3], db=database)
            res = my.sql_with_result(sql)
            print(res)
            res_list.append(res)
        return 1

class ServerState:
    def smoke_test(self, server_node_dict):
        sql_list = ["SET client_min_messages TO 'warning';", "drop table if exists t1111;",
                    "RESET client_min_messages;", "create table t1111(id int primary key, info text, wt int);",
                    "insert into t1111(id,info,wt) values(1, 'record1', 1);",
                    "insert into t1111(id,info,wt) values(2, 'record2', 2);", "update t1111 set wt = 12 where id = 1;",
                    "select * from t1111;", "delete from t1111 where id = 1;", "select * from t1111;",
                    "prepare q1(int) as select*from t1111 where id=$1; execute q1(2);",
                    "prepare q1(int) as select*from t1111 where id=$1; begin; execute q1(1); prepare q2(text,int, "
                    "int) as update t1111 set info=$1 , wt=$2 where id=$3; execute q2('Rec1',2,1); commit;",
                    "prepare q2(text,int, int) as update t1111 set info=$1, wt=$2 where id=$3; execute q2('Rec2',3,2);",
                    "drop table t1111;"]
        select_res_list = [[(1, 'record1', 12), (2, 'record2', 2)], [(2, 'record2', 2)], [(2, 'record2', 2)]]
        for i in server_node_dict:
            print('当前测试的计算节点是 [%s:%s]' % (i[0], i[1]))
            num = 0
            for sql in sql_list:
                print(sql)
                if 'select' in sql and 'begin' not in sql:
                    res = Pg(host=i[0], port=i[1], user=i[2], pwd=i[3], db='postgres').sql_with_result(sql)
                    print(res)
                    if res == select_res_list[num]:
                        num += 1
                    else:
                        print("数据有误, 正确数据应为[%s]" % select_res_list[num])
                        return 0
                else:
                    pg = Pg(host=i[0], port=i[1], user=i[2], pwd=i[3], db='postgres')
                    pg.ddl_sql(sql)
                    pg.close()
        return 1

    def server_smoke_test(self, serial_num=None):
        # serial_num就是第几个正在运行的计算节点信息, 不填写的话就是测试所有的
        if serial_num == None:
            server_node_dict = node_info().show_all_running_computer()
        else:
            server_node_dict = []
            server_node = node_info().show_all_running_computer()[serial_num]
            server_node_dict.append(server_node)
        try:
            self.smoke_test(server_node_dict)
            return 1
        except Exception as err:
            print(err)
            return 0

    def server_partition_table(self, server_list, src_shard_id='all', dst_shard_id='all', steps='partition_table_all', tb_name='transfer_account'):
        # step = [select] | ['only_create_table'] | ['table_all'] | ['only_create_partition_table'] | ['partition_table_all']
        # default = ['partition_table_all']
        days = random.randint(8, 15)
        pg = connect.Pg(host=server_list[0], port=server_list[1], user=server_list[2], pwd=server_list[3],
                        db='postgres')

        def insert_act():
            for i in range(days):
                this_year_month = time.strftime("%Y-%m-", time.localtime())
                random_day = str(random.randint(1, 28))
                date = this_year_month + random_day
                small_value, big_value = i * 100 + 1, (i + 1) * 100
                sql = "insert into %s select generate_series(%s, %s),('%s');" % (tb_name, small_value, big_value, date)
                print(sql)
                pg.ddl_sql(sql)

        def select_act():
            select_sql = 'select sum(money) as moneytotal from %s;' % tb_name
            print('%s:%s: %s' % (server_list[0], server_list[1], select_sql))
            res = pg.sql_with_result(select_sql)[0][0]
            right_res = days * 100000
            if res != right_res and steps != 'select':
                print("结果不正确，测试失败", 2)
                return 0
            elif steps == 'select':
                return res

        try:
            if steps != 'select':
                res = set_timeout()
                if res == 0:
                    return res
                sql = 'drop table if exists %s;' % tb_name
                print(sql)
                pg.ddl_sql(sql)

            if steps == 'only_create_table' or steps == 'table_all':
                show_topic('创建一个常规表%s' % tb_name, 3)
                sql = 'create table %s(id int primary key,tradedate varchar(255), money int default 1000);' % tb_name
                print(sql)
                pg.ddl_sql(sql)
                if steps == 'only_create_table':
                    return 1
                insert_act()
                select_act()
            elif steps == 'only_create_partition_table' or steps == 'partition_table_all':
                show_topic('创建一个分区表%s' % tb_name, 3)
                sql = 'create table %s (id int primary key,tradedate varchar(255), money int default 1000)' \
                    ' partition by range(id);' % tb_name
                print(sql)
                pg.ddl_sql(sql)
                for i in range(1, 7):
                    shard = src_shard_id
                    small_value, big_value = 1 + (i - 1) * 250, 1 + (i * 250)
                    if i == 1:
                        small_value = 'MINVALUE'
                    elif i > 3:
                        shard = dst_shard_id
                    sql = 'create table %s_0%s partition of %s for values from (%s) to(%s) with ' \
                          '(shard = %s);' % (tb_name, i, tb_name, small_value, big_value, shard)
                    print(sql)
                    pg.ddl_sql(sql)
                if steps == 'only_create_partition_table':
                    return 1
                insert_act()
                select_act()
            elif steps == 'select':
                select_act()
        except Exception as err:
            print(err)
            return 0
        return 1

    def server_ddl_test1(self, server):
        try:
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            ddl_list = ["drop table if exists student;", "create table student(id int primary key, info text, wt int);",
                        "insert into student(id,info,wt) values(1, 'record1', 1);",
                        "insert into student(id,info,wt) values(2, 'record2', 2);"]
            for ddl_sql in ddl_list:
                print(ddl_sql)
                pg.ddl_sql(ddl_sql)
            pg.close()
        except Exception as err:
            print('！！！ddl失败: %s！！！' % err)
            return 0
        return 1

