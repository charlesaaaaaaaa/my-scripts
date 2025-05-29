from base.api.post import *
from base.other.getconf import *
from base.other import info, connect
from case.general_test import *
from base.other.sys_opt import *
from case.daily_test.hellens_script import hdfs_query
import time
import random
import subprocess
import string
import threading


class CaictCase:
    def __init__(self, nodes):
        # 这个用例是重写hellen的脚本的
        self.nodes = nodes
        self.conf = getconf.get_conf_info().cluster_mgr()

    def sysbench_test(self, host, port, user, pwd, db="postgres", thread=10, action="prepare", case="point_select", db_driver="pgsql", runtime=300):
        file_loc = "./%s_oltp_%s" % (thread, action)
        server_info = "--db-driver=%s --pgsql-host=%s --report-interval=10 --pgsql-port=%s --pgsql-user=%s " \
                      "--pgsql-password=%s --pgsql-db=%s " % (db_driver, host, port, user, pwd, db)
        if action == "run":
            sysbench = "sysbench oltp_%s %s --tables=10 --table-size=10000 --db-ps-mode=disable " \
                       "--threads=%s --time=%s --rand-type=uniform %s > %s 2>&1" \
                       "" % (case, server_info, thread, runtime, action, file_loc)
        else:
            sysbench = "sysbench oltp_%s %s --tables=10 --table-size=10000 --db-ps-mode=disable " \
                      "--threads=%s --rand-type=uniform %s > %s.log 2>&1" \
                      "" % (case, server_info, thread, action, action)
        subprocess.run(sysbench, shell=True)
        if action == "run":
            op = open(file_loc, 'r', encoding="utf-8")
            print(op.read())
            op.close()

    def cur_time(self, seconds=0):
        timestamp = time.time() + seconds
        local_time = time.localtime(timestamp)
        format_time = time.strftime("%H:%M:%S", local_time)
        return format_time

    def create_db_tb_apsd(self, stor_master, db="cdmsrc"):
        create_db_sql = "create database if not exists %s character set utf8;" % db
        create_tb_sql = "CREATE TABLE apsd (apsdprocod varchar(2) NOT NULL DEFAULT ' '," \
                        "apsdactno varchar(15) NOT NULL DEFAULT ' '," \
                        "apsdtrdat int(11) NOT NULL DEFAULT '19700101'," \
                        "apsdjrnno decimal(10,0) NOT NULL DEFAULT '0'," \
                        "apsdseqno decimal(6,0) NOT NULL DEFAULT '0'," \
                        "apsdprdno varchar(19) NOT NULL DEFAULT ' '," \
                        "apsdfrnjrn varchar(12) NOT NULL DEFAULT ' '," \
                        "apsdtrtm varchar(6) NOT NULL DEFAULT ' '," \
                        "apsdvchno varchar(8) NOT NULL DEFAULT ' '," \
                        "apsdtrproccod varchar(2) NOT NULL DEFAULT ' '," \
                        "apsdtrbk varchar(4) NOT NULL DEFAULT ' '," \
                        "apsdtrcod decimal(6,0) NOT NULL DEFAULT '0'," \
                        "apsdtramt decimal(18,2) NOT NULL DEFAULT '0.00'," \
                        "apsdcshtfr varchar(1) NOT NULL DEFAULT ' '," \
                        "apsdrbind varchar(1) NOT NULL DEFAULT ' '," \
                        "apsdtraftbal decimal(18,2) NOT NULL DEFAULT '0.00'," \
                        "apsderrdat varchar(8) NOT NULL DEFAULT ' '," \
                        "apsddbktyp decimal(10,0) NOT NULL DEFAULT '0'," \
                        "apsddbkpro varchar(2) NOT NULL DEFAULT ' '," \
                        "apsdbatno varchar(2) NOT NULL DEFAULT ' '," \
                        "apsddbkno decimal(10,0) NOT NULL DEFAULT '0'," \
                        "apsdaprocod varchar(2) NOT NULL DEFAULT ' '," \
                        "apsdaacno varchar(15) NOT NULL DEFAULT ' '," \
                        "apsdabs varchar(15) NOT NULL DEFAULT ' '," \
                        "apsdrem varchar(45) NOT NULL DEFAULT ' '," \
                        "apsdtrchl varchar(4) NOT NULL DEFAULT ' '," \
                        "apsdtrfrm varchar(10) NOT NULL DEFAULT ' '," \
                        "apsdtrpla varchar(45) NOT NULL DEFAULT ' '," \
                        "apsdecind varchar(1) NOT NULL DEFAULT ' '," \
                        "apsdprtind varchar(1) NOT NULL DEFAULT ' '," \
                        "apsdsup1 varchar(4) NOT NULL DEFAULT ' '," \
                        "apsdsup2 varchar(4) NOT NULL DEFAULT ' '," \
                        "id int(9) NOT NULL,PRIMARY KEY (id,apsdprocod,apsdtrdat)" \
                        ") ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;"
        my = connect.My(host=stor_master[0], port=stor_master[1], user=stor_master[2], pwd=stor_master[3], db="mysql")
        my.ddl_sql(create_db_sql)
        my.close()
        my = connect.My(host=stor_master[0], port=stor_master[1], user=stor_master[2], pwd=stor_master[3], db=db)
        my.ddl_sql(create_tb_sql)
        my.close()

    def connect_server(self, sql_list, server, db="postgres"):
        show_topic("操作计算节点", 2)
        pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db=db)
        for sql in sql_list:
            print(sql)
            try:
                if "select" in sql:
                    res = pg.sql_with_result(sql)
                    print(res)
                    pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db=db)
                else:
                    pg.ddl_sql(sql)
            except Exception as err:
                print(err)
                return 0
        return 1

    def check_metadata_117(self):
        case = 'check_metadata_117'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic('安装 [1shard, 1 comps] 集群', 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic('检查shard主备状态(read_only && super_read_only)', 2)
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            show_topic('对计算节点进行分区表操作', 2)
            server = info.node_info().show_all_running_computer()[0]
            res = ServerState().server_partition_table(server)
            if res == 0:
                return [case, res]
            res = pg_show_table(table_name='transfer_account', signal_server_list=server)
            print(res)
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def wr_split_118(self):
        case = 'wr_split_118'
        show_topic("正在测试 [%s] ..." % case)
        try:
            the_latest_clsuter_id = info.node_info().show_all_running_cluster_id()[-1]
            the_latest_shard_id = info.node_info().show_all_running_shard_id()[-1]
            server = info.node_info().show_all_running_computer()[0]

            def add_nodes():
                show_topic("发送 [add_nodes] api", 2)
                res = cluster_setting(0).add_nodes(cluster_id=the_latest_clsuter_id, shard_id=the_latest_shard_id, nodes_num=1)
                if res == 0:
                    return [case, res]

            def show_meta():
                show_topic("查看元数据信息", 2)
                sql_list = ["select * from meta_db_nodes;",
                            'select shard_id, hostaddr, port, member_state, db_cluster_id ,backup_node ,replica_delay,'
                            'status, when_created from shard_nodes  where status = "active";']
                for sql in sql_list:
                    print(sql)
                    res = info.node_info().get_res(sql)
                    print(res)
            add_nodes()
            show_meta()
            show_topic("运行sysbench", 2)
            self.sysbench_test(host=server[0], port=server[1], user=server[2], pwd=server[3])
            self.sysbench_test(host=server[0], port=server[1], user=server[2], pwd=server[3], action="run",
                               case="read_write")

            sql_list = ["set enable_sql_log = on;", "set enable_replica_read=on;", "show enable_replica_read;",
                        "show replica_read_ping_threshold;", "show replica_read_latency_threshold;",
                        "show replica_read_order;", "show replica_read_fallback;", "select * from pg_shard_node;",
                        "update pg_shard_node set ro_weight=30 where hostaddr = '192.168.0.136'and port = 59403 ;",
                        "select * from pg_shard_node;", "create table t1(a int,b int);", "insert into t1  values(1,2);",
                        "select * from t1;", "update t1 set b = 3;"]
            res = self.connect_server(sql_list=sql_list, server=server)
            if res == 0:
                return [case, res]
            add_nodes()
            show_meta()
            sql_list = ["set log_min_messages to 'debug1';", "set enable_sql_log = on;", "set enable_replica_read=on;",
                        "select * from pg_shard_node;",
                        "update pg_shard_node set ro_weight=30 where hostaddr = '%s'and port = %s;" % (server[0], server[1])
                        ]
            res = self.connect_server(sql_list=sql_list, server=server)
            if res == 0:
                return [case, res]
            show_topic("发送 [delete_nodes] api", 2)
            new_ndoes = info.node_info().show_all_running_storage()[-1]
            res = cluster_setting(0).del_nodes(cluster_id=the_latest_clsuter_id, shard_id=the_latest_shard_id,
                                               stor_node_host=new_ndoes[0], stor_node_port=new_ndoes[1])
            if res == 0:
                return [case, res]
            show_meta()
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def cluster_data_backup_312(self):

        case = "cluster_data_backup_312"
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic('安装 [1shard, 1 comps] 集群', 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            res = set_storage_nodes_timeout()
            if res == 0:
                return [case, res]
            show_topic("创建 apsd 表")
            new_shard_id = info.node_info().show_all_running_shard_id()[-1]
            stor_master = info.node_info().show_specify_shard_master_node(new_shard_id)
            # self.create_db_tb_apsd(stor_master=stor_master, db='mysql')
            self.create_db_tb_apsd(stor_master=stor_master)
            show_topic('对新集群计算节点创建分区表并且灌数据', 2)
            server = info.node_info().show_all_running_computer()[0]
            res = ServerState().server_partition_table(server_list=server)
            if res == 0:
                return [case, 0]
            show_topic("插入数据", 2)
            new_cluster_id = info.node_info().show_all_running_cluster_id()[-1]
            script_loc = './case/daily_test/hellens_script/insert_data.py'
            comm = "python3 %s --host %s --port %s --clusterid %s --thread_num 9" % (script_loc, stor_master[0],
                                                                                     stor_master[1], new_cluster_id[0])
            subprocess.run(comm, shell=True)
            sql = "select count(*) from apsd;"
            my = connect.My(host=stor_master[0], port=stor_master[1], user=stor_master[2], pwd=stor_master[3], db="cdmsrc")
            res = my.sql_with_result(sql)
            print(res)
            # 还有kunlun-test/t/3_12_cluster_data_backup.test没整

            def add_time(seconds):
                curtime = self.cur_time()
                next_time = self.cur_time(seconds)
                format_time = "%s-%s" % (curtime, next_time)
                return format_time
            show_topic("发送 [update_cluster_coldback_time_period] api", 2)
            res = cluster_setting(0).update_cluster_coldback_time_period(cluster_id=new_cluster_id,
                                                                         time_period_str=add_time(120))
            if res == 0:
                return [case, 0]

            def check_hdfs():
                show_topic("检查hdfs状态", 2)
                clsuter_name_sql = 'select name from db_clusters  where status = "inuse"  limit 0,1;'
                cluster_name = info.node_info().get_res(clsuter_name_sql)[0][0]
                hdfs_host = self.conf["hdfs_host"]
                hdfs_port = self.conf["hdfs_port"]
                hdfs_user = self.conf["hdfs_user"]
                hdfs_query.run(hdfs_host=hdfs_host, hdfs_port=hdfs_port, cluster_name=cluster_name, hdfs_user=hdfs_user)
            meta_master = info.master().metadata()
            meta_host = "%s:%s" % (meta_master[0], meta_master[1])
            check_hdfs()
            show_topic("运行脚本 loop_process_transfer.py", 2)
            command = 'python3 ./case/daily_test/hellens_script/loop_process_transfer.py --meta_host %s --thread_num 1 ' \
                      '--clusterid %s --timeout 50 --total_money 1000000' % (meta_host, new_cluster_id)
            subprocess.run(command)
            for i in range(3):
                show_topic("发送 [manual_backup_cluster] api", 2)
                res = cluster_setting(0).manual_backup_cluster(cluster_id=new_cluster_id)
                if res == 0:
                    return [case, 0]
                # 不明白这里hellen为什么要检查两次hdfs，就这样吧
                check_hdfs()
                if i != 2:
                    check_hdfs()
                    show_topic("运行 insert_data.py 脚本", 2)
                    script_loc_indertdata = "./case/daily_test/hellens_script/insert_data.py"
                    comm = "python3 %s --host %s --port %s --clusterid %s --timeout 50" % (script_loc_indertdata,
                                                                                           stor_master[0], stor_master[1],
                                                                                           new_cluster_id)
                    subprocess.run(comm, shell=True)
        except Exception as err:
            print(err)
            return [case, 0]
        # show_topic("发送 [manual_backup_cluster] api", 2)
        # res = cluster_setting(0).manual_backup_cluster(cluster_id=new_cluster_id)
        # if res == 0:
        #     return [case, 0]
        # # 虽然这里hellen只跑了一次检查hdfs的脚本，但那个脚本里面是跑了两次hdfs检查的，不明白，为什么？
        # check_hdfs()
        # check_hdfs()
        # show_topic("运行 insert_data.py 脚本", 2)
        # script_loc_indertdata = "./case/daily_test/hellens_script/insert_data.py"
        # comm = "python3 %s --host %s --port %s --clusterid %s --timeout 50" % (script_loc_indertdata, stor_master[0],
        #                                                                        stor_master[1], new_cluster_id)
        # subprocess.run(comm, shell=True)
        # show_topic("发送 [manual_backup_cluster] api", 2)
        # res = cluster_setting(0).manual_backup_cluster(cluster_id=new_cluster_id)
        # if res == 0:
        #     return [case, 0]
        # # 这次只检查了一次hdfs，实在是找不到执行次数的规律啊，脑壳疼
        # check_hdfs()
        return [case, 1]

    def cluster_data_restore_313(self):
        case = "cluster_data_restore_313"
        show_topic("正在测试 [%s] ..." % case)
        # 这一条用例用的集群是上一个312的，所以不用清除集群
        try:
            src_cluster_id = info.node_info().show_all_running_cluster_id()[-1]
            show_topic("发送 [manual_backup_cluster] api", 2)
            res = cluster_setting(0).manual_backup_cluster(cluster_id=src_cluster_id)
            if res == 0:
                return [case, 0]
            show_topic("创建 apsd 表")
            new_shard_id = info.node_info().show_all_running_shard_id()[-1]
            stor_master = info.node_info().show_specify_shard_master_node(new_shard_id)
            self.create_db_tb_apsd(stor_master=stor_master)
            for i in range(4):
                show_topic("插入数据", 2)
                new_cluster_id = info.node_info().show_all_running_cluster_id()[-1]
                script_loc = './case/daily_test/hellens_script/insert_data.py'
                comm = "python3 %s --host %s --port %s --clusterid %s --thread_num 9" % (script_loc, stor_master[0],
                                                                                         stor_master[1], new_cluster_id)
                subprocess.run(comm, shell=True)
                show_topic("发送 [manual_backup_cluster] api", 2)
                res = cluster_setting(0).manual_backup_cluster(cluster_id=new_cluster_id)
                if res == 0:
                    return [case, 0]
            show_topic('安装 [1shard, 1 comps] 集群', 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic("发送 [cluster_restore] api", 2)
            dst_cluster_id = info.node_info().show_all_running_cluster_id()[-1]

            res = cluster_setting(0).cluster_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                     restore_time=self.cur_time())
            if res == 0:
                return [case, res]
            sql_list = ["show slave hosts;", "select count(*) from apsd;"]
            for sql in sql_list:
                my = connect.My(host=stor_master[0], port=stor_master[1], user=stor_master[2], pwd=stor_master[3],
                                db='cdmsrc')
                print(sql)
                res = my.sql_with_result(sql)
                print(res)
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def resource_split_314(self):
        # 3_14_resource_split
        case = 'resource_split_314'
        show_topic("正在测试 [%s] ..." % case)
        try:
            show_topic("尝试删除所有运行中的cluster", 2)
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("安装集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic("创建kltestmgr数据库", 2)
            shard_id = info.node_info().show_all_running_shard_id()[-1]
            shard_master = info.node_info().show_specify_shard_master_node(shard_id=shard_id)
            my = connect.My(host=shard_master[0], port=shard_master[1], user=shard_master[2], pwd=shard_master[3], db="mysql")
            my.ddl_sql("create database kltestmgr;")
            my.close()
            show_topic("shard主测试sysbench", 2)
            self.sysbench_test(host=shard_master[0], port=shard_master[1], user=shard_master[2], pwd=shard_master[3], db='kltestmgr', db_driver="mysql")
            show_topic("安装集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]
        # 还有一个manual_switch api，不知道干嘛的

    def balanced_distribution_hash_502(self):
        # 5_2_balanced_distribution_hash
        case = 'balanced_distribution_hash_502'
        show_topic("正在测试 [%s] ..." % case)
        try:
            show_topic("尝试删除所有运行中的cluster", 2)
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("安装3shard集群", 2)
            res = cluster_setting(0).create_cluster(shard=3, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            show_topic("检查shard状态", 2)
            #res = set_timeout(18000)
            if res == 0:
                return [case, res]
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            run_set_variables()
            show_topic("创建分区表并灌3万行数据", 2)
            shard_ids = info.node_info().show_all_running_shard_id()
            server = info.node_info().show_all_running_computer()[-1]
            create_db_sql = 'create database if not exists shard502'
            create_tb_sql = 'create table item(id int, name text) partition by Hash(id)'
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            print(create_db_sql)
            pg.ddl_sql(create_db_sql)
            pg.close()
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='shard502')
            print(create_tb_sql)
            pg.ddl_sql(create_tb_sql)
            num = 0
            for shard_id in shard_ids:
                sql = 'CREATE TABLE item_%s PARTITION OF item FOR VALUES WITH (MODULUS %s, REMAINDER %s) with (shard = %s' \
                      ')' % (num, len(shard_ids), num, shard_id[0])
                print(sql)
                pg.ddl_sql(sql)
                num += 1
            random_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l']
            for i in range(1, 30001):
                random_str = random.choices(random_list, k=8)
                random_str = ''.join(random_str)
                sql = "insert into item values(%s, '%s')" % (i, random_str)
                pg.ddl_sql(sql)
            pg.close()
            show_topic("检查所有子分区表是否存在数据", 2)
            num = 0
            db = 'shard502_$$_public'
            for shard_id in shard_ids:
                master = info.node_info().show_specify_shard_master_node(shard_id)
                my = connect.My(host=master[0], port=master[1], user=master[2], pwd=master[3], db=db)
                sql = 'explain select count(*) from item_%s;' % num
                print(sql)
                my.sql_with_result(sql)
                num += 1
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def online_expand_503(self):
        # 5_3_online_expand
        case = 'online_expand_503'
        show_topic("正在测试 [%s] ..." % case)
        try:
            show_topic("尝试删除所有运行中的cluster", 2)
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                return [case, res]
            show_topic("安装1shard集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=self.nodes, comps=1)
            if res == 0:
                return [case, res]
            res = StorageState().show_read_only()
            if res == 0:
                return [case, res]
            res = set_timeout(18000)
            if res == 0:
                return [case, res]
            create_tb_sql = 'create table if not exists ss(id int, apsdprocod varchar(2),apsdactno varchar(15));'
            server = info.node_info().show_all_running_computer()[-1]
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            pg.ddl_sql(create_tb_sql)
            pg.close()
            letters = string.ascii_letters
            show_topic("后台不间断insert", 2)
            def random_str(num):
                random_letters = random.choices(letters, k=num)
                random_letters_str = ''.join(random_letters)
                return random_letters_str

            def insert_table():
                for i in range(300):
                    pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
                    for j in range(100):
                        id = i * 100 + j
                        procod = random_str(2)
                        actno = random_str(15)
                        sql = "insert into ss value(%s, '%s', '%s')" % (id, procod, actno)
                        pg.ddl_sql(sql)
                    pg.close()
                    time.sleep(1)
            t = threading.Thread(target=insert_table, daemon=True)
            t.start()
            time.sleep(10)
            show_topic("增加shard", 2)
            cluster_id = info.node_info().show_all_running_cluster_id()[-1]
            shard_id = info.node_info().show_all_running_shard_id()[-1]
            res = cluster_setting(0).add_shards(cluster_id=cluster_id[0], shards=1, nodes=self.nodes)
            if res == 0:
                return [case, res]
            show_topic("增加计算节点并sleep 600s", 2)
            res = cluster_setting(0).add_comps(cluster_id=cluster_id, comps_num=1)
            if res == 0:
                return [case, res]
            dst_shard_id = info.node_info().show_all_running_shard_id()[-1]
            show_topic("sleep 600", 2)
            time.sleep(600)
            show_topic("发送 [expand_cluster] api", 2)
            table_list = ['postgres.public.ss']
            res = cluster_setting(0).expand_cluster(cluster_id=cluster_id,src_shard_id=shard_id, dst_shard_id=dst_shard_id,
                                                    table_list=table_list)
            if res == 0:
                return [case, res]
            pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db='postgres')
            res = pg.sql_with_result('select count(*) from ss;')
            print(res)
        except Exception as err:
            print(err)
            return [case, 0]
        return [case, 1]

    def online_shrinkage_504(self):
        # 5_4_online_shrinkage
        # 先不管了，用hellen之前的那个脚本吧，反正504一直以来也没有出过什么错
        case = 'online_shrinkage_504'
        show_topic("正在测试 [%s] ..." % case)
        show_topic("尝试删除所有运行中的cluster", 2)
        res = cluster_setting(0).delete_cluster_all()
        if res == 0:
            return [case, res]
        show_topic("安装2shard集群", 2)
        res = cluster_setting(0).create_cluster(shard=2, nodes=self.nodes, comps=1)
        if res == 0:
            return [case, res]
        sql_list = ["CREATE TABLE NATION (N_NATIONKEY INTEGER NOT NULL, N_NAME CHAR(25) NOT NULL, N_REGIONKEY  INTEGER "
                    "NOT NULL, N_COMMENT  VARCHAR(152))  with (shard = $dst_shard_id);"
                    "CREATE TABLE REGION (R_REGIONKEY INTEGER NOT NULL, R_NAME CHAR(25) NOT NULL, R_COMMENT "
                    "VARCHAR(152)) with (shard = $dst_shard_id);"
                    "CREATE TABLE PART (P_PARTKEY INTEGER NOT NULL, P_NAME VARCHAR(55) NOT NULL, P_MFGR CHAR(25) NOT "
                    "NULL,P_BRAND CHAR(10) NOT NULL,P_TYPE VARCHAR(25) NOT NULL, P_SIZE INTEGER NOT NULL, P_CONTAINER "
                    "CHAR(10) NOT NULL,P_RETAILPRICE DECIMAL(15,2) NOT NULL,P_COMMENT VARCHAR(23) NOT NULL) with (shard"
                    "= $src_shard_id);"
                    "CREATE TABLE SUPPLIER ( S_SUPPKEY INTEGER NOT NULL, S_NAME CHAR(25) NOT NULL,S_ADDRESS VARCHAR(40)"
                    " NOT NULL, S_NATIONKEY INTEGER NOT NULL,S_PHONE CHAR(15) NOT NULL,S_ACCTBAL DECIMAL(15,2) NOT "
                    "NULL,S_COMMENT VARCHAR(101) NOT NULL) with (shard = $dst_shard_id);"
                    "CREATE TABLE PARTSUPP (PS_PARTKEY INTEGER NOT NULL,PS_SUPPKEY INTEGER NOT NULL,PS_AVAILQTY INTEGER"
                    " NOT NULL, PS_SUPPLYCOST DECIMAL(15,2) NOT NULL,PS_COMMENT VARCHAR(199) NOT NULL ) with "
                    "(shard = $src_shard_id);"
                    "CREATE TABLE CUSTOMER (C_CUSTKEY INTEGER NOT NULL,C_NAME VARCHAR(25) NOT NULL,C_ADDRESS "
                    "VARCHAR(40) NOT NULL,C_NATIONKEY INTEGER NOT NULL,C_PHONE CHAR(15) NOT NULL,C_ACCTBAL "
                    "DECIMAL(15,2) NOT NULL,C_MKTSEGMENT CHAR(10) NOT NULL,C_COMMENT VARCHAR(117) NOT NULL) with (shard"
                    " = $src_shard_id);"
                    "CREATE TABLE ORDERS (O_ORDERKEY INTEGER NOT NULL,O_CUSTKEY INTEGER NOT NULL,O_ORDERSTATUS CHAR(1)"
                    " NOT NULL,O_TOTALPRICE DECIMAL(15,2) NOT NULL,O_ORDERDATE DATE NOT NULL,O_ORDERPRIORITY CHAR(15)"
                    " NOT NULL,O_CLERK CHAR(15) NOT NULL,O_SHIPPRIORITY INTEGER NOT NULL,O_COMMENT VARCHAR(79) NOT"
                    " NULL) with (shard = $dst_shard_id);"
                    "CREATE TABLE LINEITEM (L_ORDERKEY INTEGER NOT NULL,L_PARTKEY INTEGER NOT NULL, L_SUPPKEY INTEGER"
                    " NOT NULL,L_LINENUMBER  INTEGER NOT NULL,L_QUANTITY DECIMAL(15,2) NOT NULL, L_EXTENDEDPRICE"
                    " DECIMAL(15,2) NOT NULL,L_DISCOUNT DECIMAL(15,2) NOT NULL,L_TAX DECIMAL(15,2) NOT NULL,"
                    " L_RETURNFLAG CHAR(1) NOT NULL,L_LINESTATUS CHAR(1) NOT NULL,L_SHIPDATE DATE NOT NULL,L_COMMITDATE"
                    " DATE NOT NULL,L_RECEIPTDATE DATE NOT NULL,L_SHIPINSTRUCT CHAR(25) NOT NULL,L_SHIPMODE CHAR(10)"
                    " NOT NULL,L_COMMENT VARCHAR(44) NOT NULL) with (shard = $src_shard_id);"
                    ]

