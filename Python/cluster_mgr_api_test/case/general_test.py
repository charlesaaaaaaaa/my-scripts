from base.other.connect import *
from base.other.info import *
from base.other.sys_opt import *

class StorageState:
    def show_variables(self, storage_node_info, sql):
        res_list = []
        for i in storage_node_info:
            res = My(host=i[0], port=i[1], user=i[2], pwd=i[3], db='mysql').sql_with_result(sql)[0][1]
            res_list.append(res)
        return res_list

    def show_read_only(self):
        storage_node_info = node_info().show_all_running_storage()
        super_readonly_sql = 'show variables like "super_read_only";'
        readonly_sql = 'show variables like "read_only";'
        super_readonly_dict = {"super_read_only": self.show_variables(storage_node_info, super_readonly_sql)}
        readonly_dict = {"read_only": self.show_variables(storage_node_info, readonly_sql)}
        # print(super_readonly_dict.values(), readonly_dict.values())
        if str(super_readonly_dict.values()) == str(readonly_dict.values()):
            for i in range(len(storage_node_info)):
                show_res = '[%s:%s] super_read_only=[%s] read_only=[%s]' % (storage_node_info[i][0], storage_node_info[i][1],
                                                                                  super_readonly_dict["super_read_only"][i], readonly_dict["read_only"][i])
                if super_readonly_dict["super_read_only"][i] == 'ON':
                    show_res = 'shard备' + show_res
                else:
                    show_res = 'shard主' + show_res
                print(show_res)
        else:
            storage_node_list = []
            for i in storage_node_info:
                storage_node_list.append([i[0], i[1]])
            storage_node_dict = {"storage_node": storage_node_list}
            print('当前主备关系不正常')
            print(storage_node_dict)
            print(super_readonly_dict)
            print(readonly_dict)
            return 0
        return 1

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

    def server_smoke_test(self):
        server_node_dict = node_info().show_all_running_computer()
        self.smoke_test(server_node_dict)

    def server_partition_table(self, server_list, src_shard_id='all', dst_shard_id='all'):
        res = set_timeout()
        if res == 0:
            return res
        pg = connect.Pg(host=server_list[0], port=server_list[1], user=server_list[2], pwd=server_list[3],
                        db='postgres')
        sql = 'drop table if exists transfer_account;'
        print(sql)
        pg.ddl_sql(sql)
        sql = 'create table transfer_account(id int primary key,tradedate varchar(255), money int default 1000)' \
              'partition by range(id);'
        print(sql)
        pg.ddl_sql(sql)
        for i in range(1, 5):
            shard = src_shard_id
            small_value, big_value = 1 + (i - 1) * 250, 1 + (i * 250)
            if i == 1:
                small_value = 'MINVALUE'
            elif i > 2:
                shard = dst_shard_id
            sql = 'create table transfer_account_0%s partition of transfer_account for values from (%s) to(%s) with ' \
                  '(shard = %s);' % (i, small_value, big_value, shard)
            print(sql)
            pg.ddl_sql(sql)
        for i in range(8):
            this_year_month = time.strftime("%Y-%m-", time.localtime())
            random_day = str(random.randint(1, 28))
            date = this_year_month + random_day
            small_value, big_value = i * 100 + 1, (i + 1) * 100
            sql = "insert into transfer_account select generate_series(%s, %s),('%s');" % (small_value, big_value, date)
            print(sql)
            pg.ddl_sql(sql)
        select_sql = 'select sum(money) as moneytotal from transfer_account;'
        print(select_sql)
        res = pg.sql_with_result(select_sql)[0][0]
        print(res)
        if res != 800000:
            print("结果不正确，测试失败", 2)
            return 0
        else:
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

