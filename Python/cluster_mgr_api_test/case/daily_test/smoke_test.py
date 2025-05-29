import datetime
from base.api.post import *
from base.other.getconf import *
from base.other import info, connect
from case.general_test import *
from base.other.sys_opt import *
import time
import random
import subprocess
import os

class TestCase:
    def __init__(self, nodes):
        # 这个用例是重写hellen的脚本的
        self.cluster_info = get_conf_info().cluster_mgr()
        self.nodes = nodes

    def install_cluster(self):
        case = 'install_cluster'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        try:
            shard = 1
            comps = 1
            nodes = self.nodes
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic('安装[%s]个1主[%s]备shard, 且每shard[%s]个计算节点' % (shard, nodes - 1, comps), 2)
            res = cluster_setting(0).create_cluster(shard=shard, nodes=nodes, comps=comps)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic("设置超时变量", 2)
            res = set_server_nodes_timeout()
            t_res = 0
            if res == 0:
                t_res += 1
            res = set_storage_nodes_timeout()
            if res == 0:
                t_res += 1
            if t_res != 0:
                return [case, 0]
            else:
                show_topic('超时变量设置成功', 3)
            show_topic('对计算节点进行简单的冒烟测试', 2)
            res = ServerState().server_smoke_test()
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def add_shards(self):
        case = 'add_shards'
        show_topic("正在测试 [%s] ..." % case)
        try:
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[0][-1]
            res = cluster_setting(0).add_shards(cluster_id=the_latest_cluster_ids, shards=1, nodes=self.nodes)
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def add_comps(self):
        case = 'add_comps'
        show_topic("正在测试 [%s] ..." % case)
        try:
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[0][-1]
            res = cluster_setting(0).add_comps(the_latest_cluster_ids, 1)
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def add_nodes(self):
        case = 'add_nodes'
        show_topic("正在测试 [%s] ..." % case)
        try:
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[0][-1]
            the_latest_shard_ids = info.node_info().show_all_running_shard_id()[-1][0]
            res = cluster_setting(0).add_nodes(cluster_id=the_latest_cluster_ids, shard_id=the_latest_shard_ids, nodes_num=1)
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def rebuild_nodes(self):
        case = 'rebuild_nodes'
        show_topic("正在测试 [%s] ..." % case)
        try:
            def nodes_info(shard_id):
                sql = "select hostaddr, port from shard_nodes where shard_id = '%s';" % shard_id
                res = info.node_info().get_res(sql)
                return res
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[0][-1]
            the_latest_shard_ids = info.node_info().show_all_running_shard_id()[0][-1]
            node_infos = nodes_info(the_latest_shard_ids)
            res = cluster_setting(0).rebuild_node(shard_id=the_latest_shard_ids, cluster_id=the_latest_cluster_ids,
                                                  node_host=node_infos[-1][0], node_port=node_infos[-1][1])
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def del_comps(self):
        case = 'del_comps'
        show_topic("正在测试 [%s] ..." % case)
        try:
            def comp_ids():
                sql = 'select id from comp_nodes where status = "active"'
                res = info.node_info().get_res(sql)
                return res
            comps_info = comp_ids()
            old_len_comps = len(comps_info)
            new_len_comps = old_len_comps - 1
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[-1][0]
            the_latest_comp = comps_info[-1][0]
            res = cluster_setting(0).del_comps(cluster_id=the_latest_cluster_ids, comp_id=the_latest_comp)
            if res == 0:
                return [case, res]
            comps_info = comp_ids()
            now_len_comps = len(comps_info[0])
            if now_len_comps != new_len_comps:
                print('现计算节点个数[%s]与删除之前个数不正确[%s]' % (now_len_comps, old_len_comps))
                return [case, 0]
        except:
            return [case, 0]
        return [case, 1]

    def del_nodes(self):
        case = 'del_nodes'
        show_topic("正在测试 [%s] ..." % case)
        try:
            def nodes_info(shard_id):
                sql = "select hostaddr, port from shard_nodes where shard_id = '%s' and status = 'active';" % shard_id
                res = info.node_info().get_res(sql)
                return res
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[-1][0]
            the_latest_shard_ids = info.node_info().show_all_running_shard_id()[-1][0]
            node_infos = nodes_info(the_latest_shard_ids)
            old_len_nodes = len(node_infos)
            new_len_nodes = old_len_nodes - 1
            res = cluster_setting(0).del_nodes(cluster_id=the_latest_cluster_ids, shard_id=the_latest_shard_ids,
                                               stor_node_host=node_infos[-1][0], stor_node_port=node_infos[-1][1])
            if res == 0:
                return [case, res]
            show_topic("sleep 30s ...", 2)
            now_nodes = nodes_info(the_latest_shard_ids)
            now_len_nodes = len(now_nodes)
            if now_len_nodes != new_len_nodes:
                print('现存储节点节点个数[%s]与删除之前个数不正确[%s]' % (now_len_nodes, old_len_nodes))
                return [case, 0]
        except:
            return [case, 0]
        return [case, 1]

    def del_shard(self):
        case = 'del_shard'
        show_topic("正在测试 [%s] ..." % case)
        try:
            the_latest_cluster_id = info.node_info().show_all_running_cluster_id()[0][-1]
            shard_ids = info.node_info().show_all_running_shard_id()
            the_latest_shard_id = shard_ids[-1]
            old_shard_len = len(shard_ids)
            new_shard_len = old_shard_len - 1
            res = cluster_setting(0).del_shard(cluster_id=the_latest_cluster_id, shard_id=the_latest_shard_id)
            if res == 0:
                return [case, res]
            now_shard = info.node_info().show_all_running_shard_id()
            now_shard_len = len(now_shard)
            if now_shard_len != new_shard_len:
                print('现shard个数[%s]与删除之前个数不正确[%s]' % (now_shard_len, old_shard_len))
                return [case, 0]
        except:
            return [case, 0]
        return [case, 1]

    def del_cluster(self):
        case = 'del_clsuter'
        show_topic("正在测试 [%s] ..." % case)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
        except:
            return [case, 0]
        return [case, 1]

    def cluster_backup_restore(self, test_partition=0):
        # test_partition: 默认为0时不会创建分区表，为1时会根据shard数进行分区
        case = 'cluster_backup_restore'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)

        def stop_loading():
            # 一个文件，类似于标志点，不存在时会停掉后台的灌数据子进程
            loadword_flag = './log/tmp_loadwork.log'
            show_topic('停止负载', level=2)
            os.remove(loadword_flag)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("新建2 shards的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            # res = StorageState().show_cluster_general_job_log()
            # if res == 0:
            #     return [case, res]
            res = info.node_info().show_all_running_shard_id()
            print('当前shard_id: [%s]' % str(res))
            show_topic("新建另一个2 shards的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=2)
            if res == 0:
                return [case, res]
            comp_list = info.node_info().show_all_running_computer()
            ts = TranSfer(comp_list=comp_list[0])
            if test_partition == 1:
                master_cluster_id = info.node_info().show_all_running_cluster_id()[0]
                partition_shards_list = info.node_info().show_all_running_shard_id_with_cluster_id(cluster_id=master_cluster_id)
                ts.prepare(partition_shards_list=partition_shards_list)
            elif test_partition == 0:
                ts.prepare()
            print('')
            ts.loadwork(threads_num=10)
            show_topic('sleep 600s', 2)
            time.sleep(600)
            show_topic("手动备份集群", 2)
            src_cluster_id = info.node_info().show_all_running_cluster_id()[0][0]
            # backup_starttime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            backup_starttime = datetime.datetime.now()
            backup_after_30s = backup_starttime + datetime.timedelta(seconds=30)
            res = cluster_setting(60).manual_backup_cluster(cluster_id=src_cluster_id)
            if res == 0:
                stop_loading()
                return [case, res]
            res = StorageState().show_cluster_general_job_log()
            if res == 0:
                stop_loading()
                return [case, res]
            dst_cluster_id = info.node_info().show_all_running_cluster_id()[-1][0]
            # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            now = datetime.datetime.now()
            past_120s = now - datetime.timedelta(seconds=120)
            res = cluster_setting(0).cluster_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                     restore_time=backup_after_30s)
            if res == 0:
                stop_loading()
                return [case, res]
            stop_loading()
            show_topic("对主集群进行ddl操作", 2)
            server = info.node_info().show_all_running_computer()[0]
            res = ServerState().server_ddl_test1(server)
            if res == 0:
                return [case, res]
            show_topic("对备集群进行ddl操作，当前版本该操作备集群需失败", 2)
            server = info.node_info().show_all_running_computer()[-1]
            res = ServerState().server_ddl_test1(server)
            if res != 0:
                return [case, 0]
            res = ts.diff_res(comp_list_slave=comp_list[-1])
            if res == 0:
                return [case, 0]
        except Exception as err:
            print(err)
            stop_loading()
        return [case, 1]

    def cluster_table_repartition(self):
        case = 'cluster_table_repartition'
        show_topic("正在测试 [%s] ..." % case) 
        show_topic("删除可能存在的集群", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("新建2 shards, 1 comps的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic('对新集群计算节点创建常规表并且灌数据', 2)
            server = info.node_info().show_all_running_computer()[0]
            old_storage_node_id = info.node_info().show_all_running_shard_id()
            src_shard_id, dst_shard_id = old_storage_node_id[0][0], old_storage_node_id[1][0]
            res = ServerState().server_partition_table(server_list=server, src_shard_id=src_shard_id,
                                                       dst_shard_id=dst_shard_id, steps='table_all')
            if res == 0:
                return [case, 0]
            show_topic("新建另一个2 shards，2 comps的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=2)
            if res == 0:
                return [case, res]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            show_topic("创建分区表t1并\\d+", 2)
            servers = info.node_info().show_all_running_computer()
            server1, server2, server3 = servers[0], servers[1], servers[2]
            # server1 是前面集群的计算节点， server2 是后面建的集群的计算节点1， server3 是后面建的集群的计算节点2
            shard_id = info.node_info().show_all_running_shard_id()
            # 两个集群，每个集群两个shard， 故要用到最后的两个shard
            s2_src_shard_id, s2_dst_shard_id = shard_id[2][0], shard_id[3][0]
            """
            ddl_list = ["drop table if exists t1;",
                        "create table t1(id int primary key,tradedate varchar(255), money int default 1000);"]
            pg2 = connect.Pg(host=server2[0], port=server2[1], user=server2[2], pwd=server2[3], db='postgres')
            for sql in ddl_list:
                print(sql)
                pg2.ddl_sql(sql)
            """
            res = ServerState().server_partition_table(server_list=server2, src_shard_id=s2_src_shard_id,
                                                       dst_shard_id=s2_dst_shard_id, steps='only_create_partition_table', tb_name='t1')
            if res == 0:
                return [case, res]
            time.sleep(30)
            tb_name = 'transfer_account'
            for i in servers:
                show_topic('展示计算节点%s:%s的%s表结构' % (i[0], i[1], tb_name), 2)
                pg_show_table(signal_server_list=server1, table_name=tb_name)
                tb_name = 't1'
            time.sleep(30)
            # print('%s\n%s' % (res2, res3))
            show_topic('发送 【repartition_tables】 api', 2)
            cluster_ids = info.node_info().show_all_running_cluster_id()
            src_cluster_id, dst_cluster_id = cluster_ids[0][0], cluster_ids[1][0]
            repartition_tables = 'postgres_$$_public.transfer_account=>postgres_$$_public.t1'
            res = cluster_setting(0).repartition_tables(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                        repartition_tables=repartition_tables)
            if res == 0:
                return [case, res]
            time.sleep(120)
            # tb_name = 'transfer_account'
            # res_list = []
            # for i in servers:
            #     res = ServerState().server_partition_table(server_list=i, steps='select', tb_name=tb_name)
            #     show_topic(res)
            #     res_list.append(res)
            #     tb_name = 't1'
            # if res_list[0] == res_list[1] == res_list[2]:
            #     show_topic("当前三个计算节点表结果都为%s" % res_list[0], 2)
            show_topic("对新计算节点进行ddl操作", 2)
            server = info.node_info().show_all_running_computer()[-1]
            res = ServerState().server_ddl_test1(server)
            if res == 0:
                return [case, res]
            res = StorageState().show_cluster_general_job_log()
            if res == 0:
                return [case, res]
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def expand_cluster(self):
        case = 'expand_cluster'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("新建2 shards, 1 comps的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic('增加shard', 2)
            the_latest_cluster_ids = info.node_info().show_all_running_cluster_id()[0][-1]
            res = cluster_setting(0).add_shards(cluster_id=the_latest_cluster_ids, shards=1, nodes=self.nodes)
            if res == 0:
                return [case, res]
            show_topic('操作计算节点', 2)
            shard_ids = info.node_info().show_all_running_shard_id()
            src_shard_id, dst_shard_id = shard_ids[0][0], shard_ids[1][0]
            server = info.node_info().show_all_running_computer()[0]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            sql_list = ["drop table if exists ss;",
                        "create table ss(id int primary key, info text, wt int) with (shard = %s);" % src_shard_id,
                        "drop table if exists student;",
                        "create table student(id int primary key, info text, wt int) with (shard = %s);" % src_shard_id,
                        "insert into student(id,info,wt) values(1, 'record1', 1);",
                        "insert into student(id,info,wt) values(2, 'record2', 2);",
                        "insert into student(id,info,wt) values(3, 'record3', 3);",
                        "drop table if exists test1 ;",
                        "create table test1(id int primary key, name text, age int) with (shard = %s);" % src_shard_id,
                        "drop table if exists test2;",
                        "create table test2(id int primary key, address char(50), number int) with (shard = "
                        "%s);" % dst_shard_id, "insert into test2(id,address,number) values(1, 'abc', 001);",
                        "insert into test2(id,address,number) values(2, '2de', 002);", "drop table if exists test3;",
                        "create table test3(id int primary key, name char(50), empid int) with (shard = %s);" % src_shard_id
                        , "insert into test3(id,name,empid) values(1, 'john', 20220001);",
                        "insert into test3(id,name,empid) values(2, 'henry', 20220002);"]

            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            for sql in sql_list:
                print(sql)
                try:
                    pg.ddl_sql(sql)
                except Exception as err:
                    print("ERROR: %s" % err)
                    return [case, 0]
            res = ServerState().server_partition_table(server_list=server, src_shard_id=src_shard_id,
                                                       dst_shard_id=dst_shard_id)
            if res == 0:
                return [case, res]
            show_topic("发送 [expand_cluster] api", 2)
            table_list = ["postgres.public.student", "postgres.public.ss", "postgres.public.test1", "postgres.public.transfer_account_01"]
            res = cluster_setting(0).expand_cluster(cluster_id=the_latest_cluster_ids, src_shard_id=src_shard_id,
                                                    dst_shard_id=dst_shard_id, table_list=table_list)
            if res == 0:
                return [case, res]
            show_topic("展示主备所有表名", 2)
            node_list = [src_shard_id, dst_shard_id]
            db = 'postgres_$$_public'
            res = StorageState().show_shard_master_tables(shard_id_list=node_list, database=db)
            if res == 0:
                return [case, res]
            # sql = 'show tables;'
            # src_my = connect.My(host=src_master[0], port=src_master[1], user=src_master[2], pwd=src_master[3], db=db)
            # dst_my = connect.My(host=dst_master[0], port=dst_master[1], user=dst_master[2], pwd=dst_master[3], db=db)
            # src_res = src_my.sql_with_result(sql)
            # dst_res = dst_my.sql_with_result(sql)
            # if src_res != dst_res:
            #     print("主备shard表名不同，故本次测试失败")
            #     return [case, 0]
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def centos_logicalbackup_restore(self):
        case = 'centos_logicalbackup_restore'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)
        res = cluster_setting(0).delete_cluster_all()
        try:
            if res == 0:
                return [case, res]
            show_topic("新建2 shards, 1 comps的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            res = StorageState().show_cluster_general_job_log()
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]

            show_topic('操作计算节点', 2)
            shard_ids = info.node_info().show_all_running_shard_id()
            src_shard_id, dst_shard_id = shard_ids[0][0], shard_ids[1][0]
            server = info.node_info().show_all_running_computer()[0]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            sql_list = ["drop table if exists test1;", "drop table if exists test2;",
                        "create table test1(id int primary key, name text, age int) with (shard = %s);" % src_shard_id,
                        "create table test2(id int primary key, address char(50), number int) with (shard = %s);"
                        "" % dst_shard_id, "insert into test2(id,address,number) values(1, 'abc', 001);",
                        "insert into test2(id,address,number) values(2, '2de', 002);"]
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            for sql in sql_list:
                print(sql)
                try:
                    pg.ddl_sql(sql)
                except Exception as err:
                    print("ERROR: %s" % err)
                    return [case, 0]
            res = ServerState().server_partition_table(server_list=server, src_shard_id=src_shard_id,
                                                       dst_shard_id=dst_shard_id)
            if res == 0:
                return [case, res]
            show_topic("发起逻辑备份api", 2)
            current_time = datetime.datetime.now() + datetime.timedelta(seconds=30)
            five_hour_later = current_time + datetime.timedelta(hours=12)
            current_time = current_time.strftime("%H:%M:%S")
            five_hour_later = five_hour_later.strftime("%H:%M:%S")
            backup_time = '%s-%s' % (current_time, five_hour_later)
            backup_list = [{"db_table": "postgres_$$_public.transfer_account", "backup_time": backup_time},
                           {"db_table": "postgres_$$_public.test1", "backup_time": backup_time},
                           {"db_table": "postgres_$$_public.test2", "backup_time": backup_time}]
            src_cluster_id = info.node_info().show_all_running_cluster_id()[0][-1]
            res = cluster_setting(0).logical_backup(cluster_id=src_cluster_id, backup_type="table",
                                                    backup_info=backup_list)
            if res == 0:
                return [case, res]
            res = StorageState().show_cluster_general_job_log()
            if res == 0:
                return [case, res]
            show_topic("新建1 shards, 1 comps的集群, 并休眠600s", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            res = StorageState().show_cluster_general_job_log()
            if res == 0:
                return [case, res]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            time.sleep(600)
            dst_clsuter_id = info.node_info().show_all_running_cluster_id()[1][-1]
            meta_master = info.master().metadata()
            meta_host = "%s:%s" % (meta_master[0], meta_master[1])
            show_topic("运行脚本 loop_process_transfer.py", 2)
            absolute_path = os.path.abspath("./case")
            py_loc = absolute_path + "/daily_test/hellens_script/loop_process_transfer.py"
            command = 'python2 %s --meta_host %s --thread_num 1 --clusterid %s --timeout 50 --total_money 1000000' \
                      '' % (py_loc, meta_host, src_cluster_id)
            subprocess.run(command, shell=True)
            show_topic("sleep 100s 并发起 逻辑恢复 api", 2)
            time.sleep(130)
            # 获取当时时间点 再 往后延长30，并以该延长后的时间为恢复api的时间
            # current_time = datetime.datetime.now() + datetime.timedelta(seconds=15)
            # time_30s_later = current_time + datetime.timedelta(seconds=30)
            # api_time = time_30s_later.strftime("%Y-%m-%d %H:%M:%S")
            # show_topic('开始第 [%s] 次发送恢复api' % i)
            # current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            current_time = datetime.datetime.now() + datetime.timedelta(seconds=15)
            current_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            show_topic('当前时间： %s ' % current_time, 3)
            restore_list = [{"db_table": "postgres_$$_public.transfer_account",
                             "new_db_table": "postgres_$$_public1.transfer_account", "restore_time": "%s" % current_time},
                            {"db_table": "postgres_$$_public.test1", "new_db_table": "postgres_$$_public1.test1",
                             "restore_time": "%s" % current_time},
                            {"db_table": "postgres_$$_public.test2", "new_db_table": "postgres_$$_public1.test2",
                             "restore_time": "%s" % current_time}]
            res = cluster_setting(30).logical_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_clsuter_id,
                                                     restore_type="table", restore_info=restore_list)
            if res == 0:
                return [case, res]
            show_topic("对备集群计算节点进行ddl操作")
            dst_server = info.node_info().show_all_running_computer()[-1]
            res = ServerState().server_ddl_test1(dst_server)
            if res == 0:
                return [case, res]
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def mirror_tables(self):
        case = 'mirror_tables'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("新建2 shards, 1 comps的集群", 2)
            res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic('操作计算节点', 2)
            sql_list = ["drop table if exists ss;", "drop table if exists test1 ;", "drop table if exists test2 ;",
                        "create table ss(id int primary key, info text, wt int) with (shard = all);",
                        "create table test1(id int primary key, name text, age int) with (shard = all);",
                        "create table test2(id int primary key, address char(50), number int) with (shard = all);",
                        "insert into test2(id,address,number) values(1, 'abc', 001);",
                        "insert into test2(id,address,number) values(2, '2de', 002);"]
            server = info.node_info().show_all_running_computer()[0]
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            for sql in sql_list:
                print(sql)
                try:
                    pg.ddl_sql(sql)
                except Exception as err:
                    print("ERROR: %s" % err)
                    return [case, 0]
            res = ServerState().server_partition_table(server_list=server, src_shard_id="all",
                                                       dst_shard_id="all")
            if res == 0:
                return [case, res]
            show_topic('add_shards', 2)
            the_latest_cluster_id = info.node_info().show_all_running_cluster_id()[0][-1]
            res = cluster_setting(0).add_shards(cluster_id=the_latest_cluster_id, shards=1, nodes=self.nodes)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic("新计算节点进行ddl操作", 2)
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            res = ServerState().server_ddl_test1(server=server)
            if res == 0:
                return [case, res]
            show_topic("展示主备所有表名", 2)
            shard_ids = info.node_info().show_all_running_shard_id()
            db = 'postgres_$$_public'
            res = StorageState().show_shard_master_tables(shard_id_list=shard_ids, database=db)
            if res == 0:
                return [case, res]
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def rcr_smoke(self):
        case = 'rcr_smoke'

        def get_cur_rcr(rcr_role='master', return_info='host'):
            # rcr_role = 'master' | 'slave'
            # return type默认为host，返回rcr主备的计算节点信息，为shard_id则rcr主备返回shard ids
            # 先通过rcr元数据表获取把rcr主的shard主节点
            rcr_master_info = info.node_info().show_rcr_comps_infos(rcr_role=rcr_role)
            if rcr_role == 'slave':
                slave_shard_id = rcr_master_info['slave_shard_id']
                rcr_slave_sql = "select hostaddr, port from shard_nodes where status = 'active' and shard_id = %s" % slave_shard_id
                rcr_info = info.node_info().get_res(sql=rcr_slave_sql)[0]
            elif rcr_role == 'master':
                rcr_host = rcr_master_info['master_master_host']
                rcr_info = rcr_host.split(':')
            rcr_stor_host, rcr_stor_port = rcr_info[0], rcr_info[1]
            # 再通过shard主节点找到cluster_id
            sql = "select db_cluster_id from shard_nodes where hostaddr = '%s' and port = '%s' and status = 'active';" % (
                rcr_stor_host, rcr_stor_port)
            tmp_cluster_id = info.node_info().get_res(sql=sql)[0][0]
            # 当要返回的是shard_id时
            if return_info == 'shard_id':
                shard_ids_list = []
                shard_ids = info.node_info().show_all_running_shard_id(cluster_id=tmp_cluster_id)
                for id in shard_ids:
                    shard_id = id[0]
                    shard_ids_list.append(shard_id)
                print('当前rcr[%s]shard_id为：[%s]' % (rcr_role, shard_ids_list))
                return shard_ids_list
            elif return_info == 'host':
                # 再通过cluster_id找到计算节点信息
                sql = "select hostaddr, port, user_name, passwd, mysql_port from comp_nodes where db_cluster_id = %s;" % tmp_cluster_id
                res = info.node_info().get_res(sql=sql)[0]
                if rcr_role == 'master':
                    print('当前rcr主是[%s:%s]' % (res[0], res[1]))
                elif rcr_role == 'slave':
                    print('当前rcr备是[%s:%s]' % (res[0], res[1]))
                return res

        def stop_loading():
            # 一个文件，类似于标志点，不存在时会停掉后台的灌数据子进程
            loadword_flag = './log/tmp_loadwork.log'
            show_topic('停止负载', level=2)
            os.remove(loadword_flag)

        def show_meta_info():
            show_topic("查看元数据信息是否更新", 2)
            meta = info.master().metadata()
            sql_list = ["select * from cluster_rcr_infos ;", "select * from cluster_rcr_meta_sync ;"]
            for sql in sql_list:
                my = connect.My(host=meta[0], port=meta[1], user=meta[2], pwd=meta[3], db="kunlun_metadata_db")
                res = my.sql_with_result(sql)
                print('%s\n%s' % (sql, res))
        show_topic("正在测试 [%s] ..." % case)
        show_topic("1. create_rcr   |\n| 2. manualsw_rcr |\n| 3. del_rcr     ", 3)
        show_topic("删除可能存在的集群", 2)
        try:
            # res = cluster_setting(0).delete_cluster_all()
            # if res == 0:
            #     return [case, res]
            # shard_num = 2
            # show_topic("新建两个%s个shard且1个comps的集群" % shard_num, 2)
            # for i in range(2):
            #     res = cluster_setting(0).create_cluster(shard=shard_num, nodes=self.nodes, comps=1)
            #     if res == 0:
            #         return [case, res]
            # show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            # res = StorageState().show_read_only()
            # if res == 0:
            #     return [case, res]
            # # res = set_timeout(18000)
            # run_set_variables()
            # if res == 0:
            #     return [case, res]
            # show_topic("发送 [create_rcr] api", 2)
            # res = cluster_setting(0).create_rcr_with_thelatest_clusters()
            # if res == 0:
            #     return [case, res]
            # show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            # cluster_ids = node_info().show_all_running_cluster_id()
            # res = StorageState().show_read_only(enable_write_cluster_list=[cluster_ids[0][0]])
            # if res == 0:
            #     return [case, res]
            # show_topic("对两个集群计算节点进行简单smoke测试, 其中备节点不能成功", 2)
            # show_topic("当前测试主节点")
            # res = ServerState().server_smoke_test(serial_num=0)
            # if res == 0:
            #     return [case, res]
            # show_topic("当前测试备节点")
            # res = ServerState().server_smoke_test(serial_num=1)
            # if res != 0:
            #     return [case, res]
            # show_meta_info()

            def run_rcr_sql():
                master_shard_ids = get_cur_rcr(return_info='shard_id', rcr_role='master')
                sql_list = [
                    'create table t32(a serial primary key, b int);'
                    'create table t33(a serial primary key, b int) partition by hash(a) partitions 8;',
                    'create table t34(a int) partition by hash(a);',
                    'create table t34_0 partition of t34 for values with(modulus 2, remainder 0);',
                    'create table t34_1 partition of t34 for values with(modulus 2, remainder 1);'
                    'create table t35(id serial primary key, v float);',
                    'alter table  t34_0 set(shard = %s);' % (random.choice(master_shard_ids)),
                    "drop database if exists db2shards;",
                    "create database db2shards shards='%s';" % (master_shard_ids[0]),
                    "alter database db2shards shards='%s';" % (master_shard_ids[1]),
                    "create sequence seq37;",
                    "alter sequence seq37 shard %s;" % (random.choice(master_shard_ids)),
                    "create materialized view t10n with(shard=%s) AS select b from t33;" % master_shard_ids[0],
                    "alter  MATERIALIZED VIEW t10n set(shard=%s);" % master_shard_ids[1]
                    ]
                # tablegroup语法的列表，因为这个sql比较多所以单独放在一个列表里面
                tablegroup_list = [
                    "CREATE TABLEGROUP tg1 WITH (SHARD=%s);" % master_shard_ids[0],
                    "CREATE TABLE t1(a int) WITH(TABLEGROUP=tg1);",
                    "create table t2(a int) with (shard=%s);" % master_shard_ids[0],
                    "ALTER TABLE t2 SET (TABLEGROUP=tg1);",
                    "create table t3(a int) with(shard=%s, tablegroup=tg1);" % master_shard_ids[1],
                    "show create table t1;",
                    "CREATE TABLEGROUP tg2 WITH (SHARD=%s);" % master_shard_ids[0],
                    "select * From pg_tablegroup ;",
                    "select * from information_schema.tablegroup;",
                    "ALTER TABLE t1 SET (TABLEGROUP=tg2);",
                    "show create table t1;",
                    "select * From pg_tablegroup;",
                    "ALTER TABLEGROUP tg2 SET(SHARD=%s);" % master_shard_ids[1],
                    "select * From pg_tablegroup ;",
                    "show create table t1;",
                    "ALTER TABLE t1 RESET(TABLEGROUP);",
                    "show create table t1;",
                    "ALTER TABLE t2 SET (TABLEGROUP=tg1);",
                    "select * From pg_tablegroup ;",
                    "show create table t2;",
                    "DROP TABLEGROUP tg1;",
                    "show create table t2;"
                ]
                # tablegroup预期结果的列表
                exp_list = [
                    [('t1', "CREATE TABLE t1 (\n a integer\n) WITH (tablegroup=tg1, engine=innodb, shard='%s')" % master_shard_ids[0])],
                    [('tg1', 16385, 0, 0, ['shard=%s' % master_shard_ids[0]]), ('tg2', 16385, 0, 0, ['shard=%s' % master_shard_ids[0]])],
                    [(2200, 't1', master_shard_ids[0], 'tg1'), (2200, 't2', master_shard_ids[0], 'tg1')],
                    [('t1', "CREATE TABLE t1 (\n a integer\n) WITH (engine=innodb, shard='%s', tablegroup=tg2)" % master_shard_ids[0])],
                    [('tg1', 16385, 0, 0, ['shard=%s' % master_shard_ids[0]]), ('tg2', 16385, 0, 0, ['shard=%s' % master_shard_ids[0]])],
                    [('tg1', 16385, 0, 0, ['shard=%s' % master_shard_ids[0]]), ('tg2', 16385, 0, 0, ['shard=%s' % master_shard_ids[1]])],
                    [('t1', "CREATE TABLE t1 (\n a integer\n) WITH (engine=innodb, shard='%s', tablegroup=tg2)" % master_shard_ids[1])],
                    [('t1', "CREATE TABLE t1 (\n a integer\n) WITH (engine=innodb, shard='%s')" % master_shard_ids[1])],
                    [('tg1', 16385, 0, 0, ['shard=4']), ('tg2', 16385, 0, 0, ['shard=%s'% master_shard_ids[1]])],
                    [('t2', "CREATE TABLE t2 (\n a integer\n) WITH (engine=innodb, shard='%s', tablegroup=tg1)" % master_shard_ids[0])],
                    [('t2', "CREATE TABLE t2 (\n a integer\n) WITH (engine=innodb, shard='%s')" % master_shard_ids[0])],
                ]
                comps = get_cur_rcr(rcr_role='master', return_info='host')
                conn = connect.Pg(db='postgres', host=comps[0], port=comps[1], user=comps[2], pwd=comps[3])
                drop_create_db = ['drop database if exists test;', 'create database if not exists test;']
                for i in drop_create_db:
                    print(i)
                    conn.ddl_sql(i)
                conn.close()
                conn = connect.Pg(db='test', host=comps[0], port=comps[1], user=comps[2], pwd=comps[3])
                print('开始测试rcr常规sql')
                err_times, show_select_times = 0, 0
                for sql in sql_list:
                    print('++ test sql: %-100s ++' % sql)
                    try:
                        conn.ddl_sql(sql=sql)
                    except Exception as err:
                        print('ERROR: %s, 第%s次' % (err, show_select_times))
                        err_times += 1
                print('\n开始测试rcr下的tablegroup语法')
                for sql in tablegroup_list:
                    print('++ test sql: %-100s ++' % sql)
                    try:
                        # 当为show或者select语句时，会和exp_list的内容进行对比，一样就是成功，反之失败
                        # 然后每触发一次就会使show_select_time自增1，这个变量是用来指定exp_list索引值的
                        if 'show' in sql or 'select' in sql:
                            tmp_result = conn.sql_with_result(sql=sql)
                            for tr in tmp_result:
                                print('== 结果输出: %-100s ==' % str(tr))
                            if tmp_result == exp_list[show_select_times]:
                                print('与预期一致')
                            else:
                                print('与预期不一致，失败')
                                # print('%s: [%s]' % (show_select_times, tmp_result))
                                err_times += 1
                            show_select_times += 1
                            conn = connect.Pg(db='test', host=comps[0], port=comps[1], user=comps[2], pwd=comps[3])
                        else:
                            conn.ddl_sql(sql=sql)
                    except Exception as err:
                        print('ERROR: %-100s' % err)
                        if sql == tablegroup_list[4]:
                            if 'Specified shard not matched with the tablegroup.' in str(err):
                                print('该错误为预期结果')
                            else:
                                print('该错误为非预期结果，失败')
                                err_times += 1
                        conn.close()
                        conn = connect.Pg(db='test', host=comps[0], port=comps[1], user=comps[2], pwd=comps[3])
                        err_times += 1
                if err_times == 1:
                    print('预期失败1次，实际失败%s次, 故成功\n' % err_times)
                    return 1
                else:
                    print('预期失败1次，实际失败%s次, 故失败\n' % err_times)
                    return 0
            # 跑上面的rcr测试要的sql
            res = run_rcr_sql()
            if res == 0:
                return [case, res]

            def run_load():
                # 获取下rcr主的计算节点信息
                rcr_master_info = get_cur_rcr()
                master_cluster_id = info.node_info().show_all_running_cluster_id()[0][0]
                shard_list = info.node_info().show_all_running_shard_id(cluster_id=master_cluster_id)
                # 获取下rcr备的计算节点信息
                rcr_slave_info = get_cur_rcr(rcr_role='slave')
                ts = TranSfer(comp_list=rcr_master_info)
                # 创建表和函数、存储过程
                ts.prepare(partition_shards_list=shard_list)
                # 开始负载
                ts.loadwork(threads_num=10)
                print('600s后开始检查数据一致性')
                time.sleep(600)
                print('时间到，暂停负载并在60s后开始检查数据一致性')
                stop_loading()
                time.sleep(60)
                res = ts.diff_res(comp_list_slave=rcr_slave_info)
                if res == 0:
                    print('一致性检查测试失败')
                    return 0
                else:
                    print('一致性检查测试成功')
                    return 1
            # 开始写入负载并检查数据一致性
            res = run_load()
            if res == 0:
                return [case, res]

            # 开始切换rcr主备了
            show_topic("sleep 30s 并发送 [manualsw_rcr] api", 2)
            time.sleep(30)
            cluster_ids = info.node_info().show_all_running_cluster_id()
            src_cluster_id, dst_cluster_id = cluster_ids[0], cluster_ids[1]
            meta_info = info.node_info().show_all_meta_ip_port_by_clustermgr_format()
            res = cluster_setting(0).manualsw_rcr(meta_info=meta_info, src_cluster_id=src_cluster_id,
                                                  dst_cluster_id=dst_cluster_id)
            if res == 0:
                return [case, res]
            res = StorageState().show_read_only(enable_write_cluster_list=[cluster_ids[1][0]])
            if res == 0:
                return [case, res]
            show_topic("对两个集群计算节点进行简单smoke测试, 其中备节点不能成功", 2)
            show_topic("当前测试备节点")
            res = ServerState().server_smoke_test(serial_num=0)
            if res != 0:
                return [case, res]
            show_topic("当前测试主节点")
            res = ServerState().server_smoke_test(serial_num=1)
            if res == 0:
                return [case, res]
            show_meta_info()
            show_topic("发送 [del_rcr] api", 2)
            res = cluster_setting(0).delete_rcr()
            if res == 0:
                return [case, res]
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic("对两个集群计算节点进行简单smoke测试", 2)
            res = ServerState().server_smoke_test()
            if res == 0:
                return [case, res]
            # 开始写入负载并检查数据一致性
            res = run_load()
            if res == 0:
                return [case, res]
            show_meta_info()
        except Exception as err:
            print(str(err))
            cluster_setting(0).delete_rcr(1)
            return [case, 0]
        finally:
            cluster_setting(0).delete_rcr(1)
            # pass
        return [case, 1]

    def expand_tg(self):
        case = 'expand_tg'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)
        res = cluster_setting(0).delete_cluster_all()
        if res == 0:
            return [case, res]
        show_topic("新建1个 [1 shards, 1 comps] 的集群", 2)
        res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
        if res == 0:
            return [case, res]
        show_topic('检查shard主备状态(read_only && super_read_only)', 2)
        res = StorageState().show_read_only()
        if res == 0:
            return [case, res]
        show_topic('add_shards', 2)
        the_latest_cluster_id = info.node_info().show_all_running_cluster_id()[0][-1]
        res = cluster_setting(0).add_shards(cluster_id=the_latest_cluster_id, shards=1, nodes=self.nodes)
        if res == 0:
            return [case, res]
        shard_ids = info.node_info().show_all_running_shard_id()
        src_shard_id, dst_shard_id = shard_ids[0][0], shard_ids[1][0]
        server = info.node_info().show_all_running_computer()[0]
        res = set_timeout(18000)
        if res == 0:
            return [case, res]
        show_topic('计算节点执行ddl操作', 2)
        sql_list = ["create tablegroup tg1 with (shard = %s);" % src_shard_id, "drop table if exists ss;",
                    "create table ss(id int primary key, info text, wt int) with (tablegroup = tg1);",
                    "drop table if exists student;", "drop table if exists test1 ;",
                    "drop table if exists test2 ;","drop table if exists test3;",
                    "create table student(id int primary key, info text, wt int) with (shard = %s);" % src_shard_id,
                    "alter table student set (tablegroup = tg1);",
                    "insert into student(id,info,wt) values(1, 'record1', 1);",
                    "insert into student(id,info,wt) values(2, 'record2', 2);",
                    "insert into student(id,info,wt) values(3, 'record3', 3);",
                    "create table test1(id int primary key, name text, age int) with (shard = %s);" % src_shard_id,
                    "create table test2(id int primary key, address char(50), number int) with (shard = %s);" % dst_shard_id,
                    "insert into test2(id,address,number) values(1, 'abc', 001);",
                    "insert into test2(id,address,number) values(2, '2de', 002);",
                    "create table test3(id int primary key, name char(50), empid int) with (shard = %s);" % dst_shard_id,
                    "insert into test3(id,name,empid) values(1, 'john', 20220001);",
                    "insert into test3(id,name,empid) values(2, 'henry', 20220002);"]
        pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
        for sql in sql_list:
            print(sql)
            try:
                pg.ddl_sql(sql)
            except Exception as err:
                print(err)
                return [case, 0]
        res = ServerState().server_partition_table(server_list=server, src_shard_id=src_shard_id,
                                                   dst_shard_id=dst_shard_id)
        if res == 0:
            return [case, res]
        show_topic("发送 [expand_cluster] api", 2)
        table_list = ["postgres.public.student","postgres.public.ss","postgres.public.test1",
                      "postgres.public.transfer_account_01"]
        res = cluster_setting(0).expand_cluster(cluster_id=the_latest_cluster_id, src_shard_id=src_shard_id,
                                                dst_shard_id=dst_shard_id, table_list=table_list)
        if res == 0:
            return [case, res]
        res = StorageState().show_shard_master_tables(shard_id_list=shard_ids, database="postgres_$$_public")
        if res == 0:
            return [case, res]
        return [case, 1]

    def install_rbrcluster_degrade(self):
        case = 'install_rbrcluster_degrade'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("删除可能存在的集群", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("新建1个 [1 shards, 1 comps] 的集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            node_infos = info.node_info().show_all_running_storage()
            times = int(self.nodes) - 1
            show_topic('发起 [control_instance] api, 暂停[%s]个存储节点' % times, 2)
            for i in range(times):
                num = i + 1
                node = node_infos[num]
                res = cluster_setting(0).control_instance(host=node[0], port=node[1], machine_type="storage",
                                                          control_type="stop")
                if res == 0:
                    return [case, res]
            storage_info = info.node_info().show_all_running_storage()[0]
            sql = "show variables like '%fullsync%';"
            my = connect.My(host=storage_info[0], port=storage_info[1], user=storage_info[2], pwd=storage_info[3],
                            db="mysql")
            res = my.sql_with_result(sql)
            print(res)
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def cgroup_smoke(self):
        case = "cgroup_smoke"
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("安装一个cpu_cores限制库为2的集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1, cpu_cores=2)
            if res == 0:
                return [case, res]
            run_set_variables()

            def prepare_run_sysbench(prepare=1):
                server = info.node_info().show_all_running_computer()[0]
                if prepare == 1:
                    show_topic("sysbench prepare 操作", 2)
                    prepare_com = 'sysbench oltp_point_select --tables=10 --table-size=100000 --db-driver=pgsql --pgsql-user' \
                                  '=%s --pgsql-password=%s --pgsql-db=postgres --pgsql-host=%s --pgsql-port=' \
                                  '%s  --threads=32 prepare > prepare.log 2>&1' % (server[2], server[3], server[0], server[1])
                    print(prepare_com)
                    subprocess.run(prepare_com, shell=True)
                show_topic("sysbench run 操作", 2)
                run_com = 'sysbench oltp_point_select --tables=10 --table-size=100000 --db-driver=pgsql --pgsql-user=%s' \
                          ' --pgsql-password=%s --pgsql-db=postgres --pgsql-host=%s --pgsql-port=%s --time=60 --threads=' \
                          '100  --rand-type=uniform --db-ps-mode=disable --report-interval=1 run > ' \
                          'tmp.log 2>&1' % (server[2], server[3], server[0], server[1])
                print(run_com)
                subprocess.run(run_com, shell=True)
                res_com = "grep transactions tmp.log | awk '{print $3}' | awk -F'(' '{print $2}'"
                res_1 = subprocess.Popen(res_com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                stdout, stderr = res_1.communicate()
                print(stdout, stderr)
                res = res_1.stdout.read().decode('utf-8')
                res = res.replace('\n', '')
                try:
                    return float(res)
                except:
                    print('运行sysbench失败，无法找寻结果，请检查./tmp.log')
                    print(res_com, res_1)
                    return -1

            res_2cores = prepare_run_sysbench()
            if res_2cores == -1:
                show_topic('结果不存在，sysbench测试失败', 3)
                return [case, 0]
            show_topic("尝试删除所有运行中的cluster", 2)
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("安装一个cpu_cores限制为8的集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1, cpu_cores=8)
            if res == 0:
                return [case, res]
            run_set_variables()
            res_8cores = prepare_run_sysbench()
            if res_8cores == -1:
                show_topic('结果不存在，sysbench测试失败', 3)
                return [case, 0]
            if res_2cores * 2 <= res_8cores:
                print('qps: 8_cores=[%s], 2_cores=[%s], 成功' % (res_8cores, res_2cores))
            else:
                print('qps: 8_cores=[%s], 2_cores=[%s], 失败' % (res_8cores, res_2cores))
                return [case, res]

            def update_cpu_core_test(cores):
                show_topic("将最近的集群计算节点及存储节点cpu核数改为%s" % cores, 2)
                server = info.node_info().show_all_running_computer()[0]
                res = cluster_setting(0).update_instance_cgroup(ip=server[0], port=server[1], node_type='pg', cpu_cores=cores)
                if res == 0:
                    return 0
                storages = info.node_info().show_all_running_storage()
                for stor in storages:
                    res = cluster_setting(0).update_instance_cgroup(ip=stor[0], port=stor[1], cpu_cores=cores)
                    if res == 0:
                        return 0
                return 1

            def show_res(res_8cores, res_2cores):
                if res_2cores * 2 <= res_8cores:
                    print('qps: 8_cores=[%s], 2_cores=[%s], 成功' % (res_8cores, res_2cores))
                    return 1
                else:
                    print('qps: 8_cores=[%s], 2_cores=[%s], 失败' % (res_8cores, res_2cores))
                    return 0
            show_topic("先跳过有关修改cpu核心数量限制的用例，修改好后记得加回来", 2)
            """
            res = update_cpu_core_test(2)
            if res == 0:
                return [case, res]
            res_2cores = prepare_run_sysbench(prepare=0)
            res = show_res(res_2cores=res_2cores, res_8cores=res_8cores)
            if res == 0:
                return [case, res]
            res = update_cpu_core_test(8)
            if res == 0:
                return [case, res]
            res_8cores = prepare_run_sysbench(prepare=0)
            show_res(res_2cores=res_2cores, res_8cores=res_8cores)
            if res == 0:
                return [case, res]
            """
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def proxysql_smoke(self):
        case = "proxysql_smoke"
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        res = cluster_setting(0).delete_cluster_all()
        if res == 0:
            return [case, res]
        show_topic("安装一个带有proxysql的单shard集群", 2)
        try:
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1,
                                                    other_paras_dict={"install_proxysql": "1"})
            if res == 0:
                return [case, res]
            proxy_info = info.node_info().show_all_running_proxysql()[-1]
            run_set_variables()
            pro_conn = connect.My(host=proxy_info[0], port=proxy_info[1], user=proxy_info[2], pwd=proxy_info[3], db='mysql')
            pro_conn.ddl_sql('create database sysbench;')
            pro_conn.close()

            def prepare_run_sysbench(prepare=1):
                server = info.node_info().show_all_running_proxysql()[-1]
                if prepare == 1:
                    show_topic("sysbench prepare 操作", 2)
                    prepare_com = 'sysbench oltp_point_select --tables=10 --table-size=100000 --db-driver=mysql --mysql-user' \
                                  '=%s --mysql-password=%s --mysql-db=sysbench --mysql-host=%s --mysql-port=' \
                                  '%s  --threads=32 prepare > prepare.log 2>&1' % (server[2], server[3], server[0], server[1])
                    print(prepare_com)
                    subprocess.run(prepare_com, shell=True)
                show_topic("sysbench run 操作", 2)
                run_com = 'sysbench oltp_point_select --tables=10 --table-size=100000 --db-driver=mysql --mysql-user=%s' \
                          ' --mysql-password=%s --mysql-db=sysbench --mysql-host=%s --mysql-port=%s --time=60 --threads=' \
                          '100  --rand-type=uniform --db-ps-mode=disable --report-interval=1 run > ' \
                          'tmp.log 2>&1' % (server[2], server[3], server[0], server[1])
                print(run_com)
                subprocess.run(run_com, shell=True)
                res_com = "grep transactions tmp.log | awk '{print $3}' | awk -F'(' '{print $2}'"
                res_1 = subprocess.Popen(res_com, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                res = res_1.stdout.read().decode('utf-8')
                res = res.replace('\n', '')
                return float(res)
            res = prepare_run_sysbench()
        except:
            return [case, 0]
        if res:
            return [case, 1]
