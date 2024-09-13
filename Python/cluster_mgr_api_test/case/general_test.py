from base.other.connect import *
from base.other.info import *
from base.other.sys_opt import *

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
            print(select_sql)
            res = pg.sql_with_result(select_sql)[0][0]
            print(res)
            right_res = days * 100000
            if res != right_res and steps != 'select':
                print("结果不正确，测试失败", 2)
                return 0
            elif steps == 'select':
                return res

        try:
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

