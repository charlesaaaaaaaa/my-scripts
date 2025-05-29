import random

from case import load_data
from res import connection, read, other
import multiprocessing


class TestCase:
    def __init__(self):
        # 这里要先建一个两shard的集群再开始
        self.conf = read.conf_info()
        self.comps_info = connection.meta().all_comps()

    def deal_lock(self):
        res = 1
        conf = self.conf
        comps_info = self.comps_info
        case = '死锁检测'
        pt_num = 10
        print('开始创建一个分区表')
        load_data.CreateTable().create_partition_table(node_info=comps_info[0], partition_table_num=pt_num)
        print('开始灌数据')
        tb_size = pt_num * 100
        load_data.load_worker(db='postgres', table='test_pt', tb_size=tb_size)
        rand_ids = []
        # 随机选择10个不重复的id值
        for i in range(10):
            tmp_id = random.randint(0, tb_size)
            while tmp_id in rand_ids:
                tmp_id = random.randint(0, tb_size)
            rand_ids.append(tmp_id)

        # 随机获取其中一个列信息
        columns_tuple = load_data.get_column_info(node_info=comps_info[0], table='test_pt')
        rand_column = random.choice(columns_tuple)
        while rand_column[3] and 'nextval' in rand_column[3]:
            rand_column = random.choice(columns_tuple)
        print(rand_column)

        def signal_update(proess_num, share_value):
            # 单个update子进程要做的事
            result = 1
            sql_list = ['begin']
            for i in range(5):
                # 每个sql选出两个id值
                index1 = (i + 1) * 2 - 2
                index2 = (i + 1) * 2 - 1
                rand_data = load_data.gen_type_data(data_type=rand_column[2], id=rand_ids[index1], numeric_precision=rand_column[4],
                                                    numeric_scale=rand_column[5])
                tmp_sql = 'update test_pt set %s = %s where id = %s or id = %s; select pg_sleep(2);' % (rand_column[0], rand_data, rand_ids[index1], rand_ids[index2])
                sql_list.append(tmp_sql)
            sql_list.append('commit;')
            # sql = '; '.join(sql_list)
            pg_conn = connection.pgsql(node_info_list=comps_info[0], db='postgres')
            commit_times = 0
            for sql in sql_list:
                try:
                    print('process_%s: %s' % (proess_num, sql))
                    pg_conn.sql(sql, commit=0)
                except Exception as err:
                    # 当一个事务第一次死锁的时候同会有死锁超时的错误
                    if sql != 'commit;' and commit_times == 0:
                        if '1205, Lock wait timeout exceeded; try restarting transaction.' in str(err):
                            print('[test succ] process_%s: %s' % (proess_num, str(err)), end='')
                            commit_times = 1
                        else:
                            print('[test fail] process_%s: %s sql=%s' % (proess_num, str(err), sql), end='')
                            share_value.value += 1
                    # 死锁一次之后的事务都是失败的，都是提示当前的事务被中断了
                    elif sql == 'commit;' or commit_times == 1:
                        if 'current transaction is aborted, commands ignored until end of transaction block' in str(err):
                            print('[test succ] process_%s: %s' % (proess_num, str(err)), end='')
                        else:
                            print('[test fail] process_%s: %s sql=%s' % (proess_num, str(err), sql), end='')
                            share_value.value += 1
            pg_conn.close(commit=1)

        l = []
        share_res = multiprocessing.Manager().Value('i', 0)
        for i in range(5):
            p = multiprocessing.Process(target=signal_update, args=(i, share_res,))
            l.append(p)
            p.start()
        for i in l:
            i.join()
        if share_res.value != 0:
            res = 0
        return [case, res]

    def isolation_test(self):
        res = 1
        case = '故障隔离'
        conf = self.conf
        comps_info = self.comps_info
        comp_info = comps_info[0]
        pt_num = 10
        sys_user = conf['sys_user']
        print('开始创建一个分区表')
        load_data.CreateTable().create_partition_table(node_info=comps_info[0], partition_table_num=pt_num)
        # 创建完表后就要马上获取表结构，不然后面kill掉shard后无法获取
        columns = load_data.get_column_info(node_info=comp_info, table='test_pt')
        cluster_id = connection.meta().all_cluster_id()[0][0]
        shard_id = connection.meta().shard_id(cluster_id)
        shard_nodes_info_tuple = connection.meta().show_shard_nodes(shard_id)
        tb_size = pt_num * 100
        load_data.load_worker(db='postgres', table='test_pt', tb_size=tb_size)
        print('kill掉其中一个shard的所有节点')
        for node_info in shard_nodes_info_tuple:
            host = node_info[0]
            port = node_info[1]
            comm = 'ssh %s@%s "ps -ef | grep %s | grep -v grep | awk \'{print \\$2}\' | xargs kill -9"' % (sys_user, host, port)
            other.run_shell(command=comm)
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        print('开始验证读数据')
        rand_id = random.randint(1, tb_size)
        err_times = 0
        for i in range(2):
            try:
                if i == 0:
                    sql = 'select * from test_pt where id = %s;' % str(rand_id)
                else:
                    sql = 'select * from test_pt;'
                print(sql)
                result = pg_conn.sql_with_res(sql)
                for i in result:
                    print('\t%s' % i)
            except Exception as err:
                if 'Kunlun-db: Failed to connect to mysql storage node at ' in str(err) and err_times == 0:
                    exists_same_node = 0
                    for node_info in shard_nodes_info_tuple:
                        # 连接失败的时候报错会有(192.168.0.1, 5555)这样的节点信息，这点也要对比一下和kill掉的是否一致
                        tmp_info = '(%s, %s)' % (node_info[0], node_info[1])
                        if tmp_info in str(err):
                            exists_same_node = 1
                    if exists_same_node == 1:
                        print('[test succ] %s' % str(err), end='')
                    else:
                        print('[test fail] %s' % str(err), end='')
                        res = 0
                elif 'current transaction is aborted, commands ignored until end of transaction block' in str(err):
                    print('[test succ] %s' % str(err), end='')
                else:
                    print('[test fail] %s' % str(err), end='')
                    res = 0
                err_times == 1
        pg_conn.close()
        print('开始验证写数据')
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        columns_str = ''
        for column in columns:
            if not column[3] or 'nextval' not in column[3]:
                if columns_str:
                    columns_str += ', %s' % column[0]
                else:
                    columns_str = column[0]
        old_sql = 'insert into test_pt(%s) values(' % columns_str
        err_times = 0
        for i in range(1, 3):
            sql = old_sql
            for column in columns:
                tmp_data = str(load_data.gen_type_data(column[2], tb_size + i, column[4], column[5]))
                if not column[3] or 'nextval' not in column[3]:
                    if sql == old_sql:
                        sql += tmp_data
                    else:
                        sql += ', %s' % tmp_data
            sql += ');'
            print(sql)
            try:
                pg_conn.sql(sql)
            except Exception as err:
                if 'Kunlun-db: Failed to connect to mysql storage node at ' in str(err) and err_times == 0:
                    exists_same_node = 0
                    for node_info in shard_nodes_info_tuple:
                        # 连接失败的时候报错会有(192.168.0.1, 5555)这样的节点信息，这点也要对比一下和kill掉的是否一致
                        tmp_info = '(%s, %s)' % (node_info[0], node_info[1])
                        if tmp_info in str(err):
                            exists_same_node = 1
                    if exists_same_node == 1:
                        print('[test succ] %s' % str(err), end='')
                    else:
                        print('[test fail] %s' % str(err), end='')
                        res = 0
                elif 'current transaction is aborted, commands ignored until end of transaction block' in str(err):
                    print('[test succ] %s' % str(err), end='')
                else:
                    print('[test fail] %s' % str(err), end='')
                    res = 0
                err_times == 1
        return [case, res]






