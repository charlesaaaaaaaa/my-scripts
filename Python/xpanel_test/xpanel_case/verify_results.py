import random
import string
import multiprocessing
import psycopg2
import pymysql
from xpanel_case.load import *


def get_meta_info(sql):
    conf = getconf().getXpanelInfo()
    host, port = conf['meta_host'], conf['meta_port']
    print(host, port, type(host), type(port))
    conn = pymysql.connect(host=host, port=int(port), user='pgx', password='pgx_pwd', db='kunlun_metadata_db')
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return res

def pg_conn(node_info, sql_list, db):
    # node_info和sql_list都是列表
    fail_times = 0
    #print('开始冒烟测试计算节点 %s' % str(node_info))
    try:
        conn = psycopg2.connect(host=node_info[0], port=node_info[1], user=node_info[2], password=node_info[3], dbname=db)
        conn.autocommit = True
        cur = conn.cursor()
        for sql in sql_list:
            print('    %s' % sql)
            try:
                cur.execute(sql)
            except Exception as err:
                print(fail_times, err)
                fail_times += 1
            try:
                res = cur.fetchall()
                print('\t%s' % res)
            except:
                pass
        conn.commit()
        cur.close()
        conn.close()
    except Exception as err:
        print(err)
        return 0
    if fail_times == 0:
        return 1
    else:
        return 0


def pg_get_data(node_info, sql, db):
    conn = psycopg2.connect(host=node_info[0], port=node_info[1], user=node_info[2], password=node_info[3], dbname=db)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return res


class Meta_Info:
    def __init__(self):
        pass

    def all_comps(self, other_column=''):
        # other_column可以有多个，用','逗号隔开
        if other_column:
            sql = "select hostaddr, port, user_name, passwd, %s from comp_nodes where status = 'active';" % other_column
        else:
            sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active';"
        res = get_meta_info(sql)
        return res

    def comps_with_cluster_id(self, cluster_id):
        sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active' and db_cluster_id = %s;" % cluster_id
        res = get_meta_info(sql)
        return res

    def all_storages(self, other_column=''):
        # other_column可以有多个，用','逗号隔开
        if other_column:
            sql = "select hostaddr, port, user_name, passwd, %s from shard_nodes where status = 'active';" % other_column
        else:
            sql = "select hostaddr, port, user_name, passwd from shard_nodes where status = 'active';"
        res = get_meta_info(sql)
        return res

    def all_shard_master(self, other_column=''):
        if other_column:
            sql = "select hostaddr, port, user_name, passwd, %s from shard_nodes where status = 'active' and member_state = 'source';" % other_column
        else:
            sql = "select hostaddr, port, user_name, passwd from shard_nodes where status = 'active' and member_state = 'source';"
        res = get_meta_info(sql)
        return res

    def all_shard_id(self):
        sql = "select distinct(shard_id) from shard_nodes where status = 'active';"
        res = get_meta_info(sql)
        return res

    def wait_backup_node(self):
        # 检查所有的shard是否存在冷备节点，不存在则等待1分钟后再检查直到所有shard都有冷备节点
        # 当检查超过20次，也就是20分钟后还没有检查出冷备节点就直接认为冷备节点选主失败了
        shard_ids = self.all_shard_id()
        shard_num = len(shard_ids)
        review_times = 0
        backup_num = 0
        while backup_num != shard_num:
            backup_num = 0
            for shard_id in shard_ids:
                sql = "select hostaddr, port, backup_node from shard_nodes where status = 'active' and shard_id = %s;" % shard_id[0]
                backup_info = get_meta_info(sql)
                print('shard_%s 冷备情况 |' % shard_id[0], end='')
                backup_times = 0
                for node in backup_info:
                    print(' %s:%s backup_node=[%s] |' % (node[0], node[1], node[2]), end='')
                    if node[2] == 'ON':
                        backup_times += 1
                print()
                # 当冷备节点的个数超过0的时候就给这个backup_num + 1, 如果和shard个数不同则这个变量又会回到0
                if backup_times > 0:
                    backup_num += 1
            review_times += 1
            if review_times > 20:
                print('\n检查超过20次，本次检查冷备节点失败')
                return 0
        return 1

    def all_cluster_id_name(self):
        sql = "select id, name from db_clusters where status = 'inuse';"
        res = get_meta_info(sql)
        return res

    def metadata_info_format(self):
        # 以 hsot:port,host:port... 的形式返回metadata信息
        sql = "select hostaddr, port from meta_db_nodes;"
        metadata_res = get_meta_info(sql)
        res = ''
        for meta_info in metadata_res:
            tmp = '%s:%s' % (meta_info[0], meta_info[1])
            if not res:
                res = tmp
            else:
                res += ',%s' % tmp
        return res

    def clustermgr_infos(self):
        sql = "select hostaddr, port, member_state from cluster_mgr_nodes;"
        res = get_meta_info(sql)
        return res

    def metadata_infos(self):
        sql = 'select hostaddr, port, user_name, passwd, member_state from meta_db_nodes;'
        res = get_meta_info(sql)
        return res

def set_storage_variables(var_list=None):
    # var_list 二级列表，第二级列表应该有两个元素，第0个是变量名，第1个是变量值
    if not var_list:
        var_list = [['lock_wait_timeout', 7200], ['net_read_timeout', 7200], ['net_write_timeout', 7200], ['innodb_lock_wait_timeout', 7200],
                    ['fullsync_timeout', 7200000]]
    all_storage = Meta_Info().all_storages()
    for i in var_list:
        sql = 'set persist %s = %s;' % (i[0], i[1])
        show_sql = "show variables like '%s';" % i[0]
        print('%s' % sql)
        for stor in all_storage:
            my = pymysql.connect(host=stor[0], port=stor[1], user=stor[2], password=stor[3], db='mysql', autocommit=True)
            cur = my.cursor()
            cur.execute(sql)
            cur.execute(show_sql)
            res = cur.fetchall()
            print('存储节点[%s:%s] 变量[%s]' % (stor[0], stor[1], res[0]))

class Verify:
    def __init__(self):
        self.meta = Meta_Info

    def comps(self, fail_comps=None):
        # fail_comps就是第几个正在运行的计算节点的预期是失败的, 给个列表
        # 如 [0, 2], 计算节点信息列表的第0个和第2个元素(计算节点)要失败, 默认为None代表所有计算节点都要成功
        comps_tuple = self.meta().all_comps()
        time.sleep(5)
        fail_times = 0
        num = 0
        sql_list = ["SET client_min_messages TO 'warning';", "drop table if exists t1111;",
                    "RESET client_min_messages;", "create table t1111(id int primary key, info text, wt int);",
                    "insert into t1111(id,info,wt) values(1, 'record1', 1);",
                    "insert into t1111(id,info,wt) values(2, 'record2', 2);", "update t1111 set wt = 12 where id = 1;",
                    "select * from t1111;", "delete from t1111 where id = 1;", "select * from t1111;",
                    "drop table t1111;"]
        for comp_info in comps_tuple:
            res = pg_conn(node_info=comp_info, sql_list=sql_list, db='postgres')
            # 当计算节点信息列表对应索引不存在于fail_comps列表，则有以下几种可能
            if fail_times and num in fail_comps:
                if res == 1:
                    fail_times += 1
                    print('%s预期失败，实际成功, 故失败' % str(comp_info))
                elif res == 0:
                    print('%s预期失败，实际失败, 故成功' % str(comp_info))
            else:
                if res == 1:
                    print('%s预期成功，实际成功, 故成功' % str(comp_info))
                elif res == 0:
                    fail_times += 1
                    print('%s预期成功，实际失败, 故失败' % str(comp_info))
            num += 1
        if fail_times == 0:
            print('本次所有计算节点冒烟测试成功')
        else:
            print('本次所有计算节点冒烟测试失败')
        if fail_times == 0:
            return 1
        else:
            return 0

    def load_worker(self, comp_info, db_name='postgres', tb_name='test1', threads=1, load_times=50):
        # comp_num 就是在当前的metadata获取正在运行的计算节点元组里面的第几个元素，默认0为第一个
        # load_times 数据更新的数据，默认每个子进程50次，每次更新随机1~50行数据量, 每次更新后会停止0到10s
        drop_sql = 'drop table if exists %s;' % tb_name
        create_sql = 'create table if not exists %s(id bigserial primary key, txt text)' % tb_name
        sql_list = [drop_sql, create_sql]
        print('开始创建[%s.%s]表' % (db_name, tb_name))
        res = pg_conn(node_info=comp_info, db=db_name, sql_list=sql_list)
        if res != 1:
            return 0
        print('启动[%s]进程数进行数据更新' % threads)

        def worker():
            for i in range(load_times):
                insert_sql = 'insert into %s(txt) values' % tb_name
                rand_times = random.randint(1, 50)
                data = ''
                for i in range(rand_times):
                    data_len = random.randint(5, 20)
                    tmp = random.choices(string.digits + string.ascii_letters, k=data_len)
                    tmp = ''.join(tmp)
                    data += "('%s')" % tmp
                    if i != rand_times - 1:
                        data += ', '
                    else:
                        data += ';'
                insert_sql += data
                res = pg_conn(node_info=comp_info, db=db_name, sql_list=[insert_sql])
                if res != 1:
                    print('insert 失败')
                    return 0
                sleep_time = random.randint(0, 10)
                sleep(sleep_time)

        process_list = []
        for i in range(threads):
            p = multiprocessing.Process(target=worker)
            process_list.append(p)
            p.start()

    def review_worker(self,  res_comp_info, dst_comp_info, res_tb_name='test1', res_db_name='postgres', dst_tb_name='test1', dst_db_name='postgres',  review_times=3):
        # review_times 结果检查的次数，默认为3次，每次检验后有10到60s的休眠时间
        # res_comp_info 是源库的计算节点，dst是目标端的计算节点
        err_times = 0
        for i in range(review_times):
            max_id_sql = 'select max(id) from %s;' % dst_tb_name
            max_id = pg_get_data(node_info=dst_comp_info, sql=max_id_sql, db=dst_db_name)[0][0]
            dst_sql = 'select * from %s where id <= %s order by id;' % (dst_tb_name, max_id)
            res_sql = 'select * from %s where id <= %s order by id;' % (res_tb_name, max_id)
            dst_res = pg_get_data(node_info=dst_comp_info, sql=dst_sql, db=dst_db_name)
            res_res = pg_get_data(node_info=res_comp_info, sql=res_sql, db=res_db_name)
            if dst_res != res_res:
                print('[%s]与[%s]结果不一致' % (res_comp_info, dst_comp_info))
                err_times += 1
        if err_times == 0:
            return 1
        else:
            return 0





