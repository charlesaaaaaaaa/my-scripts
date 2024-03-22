from base.api import post
from base.other import write_log
from base.other import connect
from base.other import info
import random


def print_log(txt):
    write_log.w2File().tolog(txt)
    print(txt)

def test_case():
    case = 'ticket #1930'
    print_log('开始测试 %s' % case)
    print_log('第一步： 创建集群，创建时开启global mvcc')
    other_paras_dict = {'enable_global_mvcc': 1}
    nick_name = 'ticket_1930'
    cre_res = post.cluster_setting().create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=1, nodes=3,
                                                    comps=1, max_storage_size=1024, max_connections=2000,
                                                    cpu_limit_node='quota', innodb_size=1024, cpu_cores=8,
                                                    rocksdb_block_cache_size_M=1024, fullsync_level=1,
                                                    data_storage_MB=1024, log_storage_MB=1024,
                                                    other_paras_dict=other_paras_dict)
    if cre_res == 0:
        return [case, 0]

    print_log('第二步： 新增shard')
    cluster_id = cre_res[1]['cluster_id']
    add_res = post.cluster_setting().add_shards(cluster_id=cluster_id, shards=1, nodes=3)
    if add_res == 0:
        return [case, 0]

    print_log('第三步： 进行写操作')
    try:
        comp_sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active' " \
                   "and db_cluster_id = %d;" % cluster_id
        meta_info = info.master().metadata()
        conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
        comps = conn.sql_with_result(comp_sql)
        # 在所有计算节点中随机选择其中一个
        comp_info = random.choices(comps)
        print_log('       开始对 %s 进行写操作' % comp_info)
        conn = connect.Pg(comp_info[0], comp_info[1], comp_info[2], comp_info[3], 'postgres')
        create_table_sql = "CREATE TABLE measurement1 ( \
                logdate date not null, \
                peaktemp int, \
                unitsales int \
                ) PARTITION BY RANGE (logdate); \
                create table m1_p0 partition of measurement1 for values from (minvalue) to ('20201231'); \
                create table m1_p1 partition of measurement1 for values from ('20201231') to ('20211231'); \
                create table m1_p2 partition of measurement1 for values from ('20211231') to ('20221231'); \
                create table m1_p3 partition of measurement1 for values from ('20221231') to ('20231231'); \
                create table m1_p4 partition of measurement1 for values from ('20231231') to (maxvalue);'"
        conn.ddl_sql(create_table_sql)
        insert_sql = "insert into measurement1 values('20080808',1,1),('20210101',6,6),('20220101',7,7)," \
                     "('20230606',8,8),('20241001',9,9);"
        conn.ddl_sql(insert_sql)
        conn.close()
    except Exception as err:
        print(err)
        print_log('写操作失败')
        return [case, 0]

    print_log('第四步：     检查 enable_global_mvcc 参数是否开启')
    try:
        new_master_sql = "select hostaddr, port, user_name, passwd from shard_nodes where db_cluster_id = 1 and " \
                         "shard_id = 2 and member_state = 'source';"
        conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
        new_shard_master_node = conn.sql_with_result(new_master_sql)[0]
        print_log('当前新增加shard的 主节点是: %s' % new_shard_master_node)
        conn = connect.My(new_shard_master_node[0], int(new_shard_master_node[1]), new_shard_master_node[2],
                          new_shard_master_node[3], 'mysql')
        sql = "show variables like 'enable_global_mvcc';"
        mvcc_status = conn.sql_with_result(sql)[0][0]
        print(sql)
        print(mvcc_status)
    except Exception as err:
        print_log('无法获取mvcc信息')
        print(err)
        return [case, 0]
    if mvcc_status == 'OFF':
        print('当前 新增加节点 mvcc 为 %s, 该用例失败' % mvcc_status)
        return [case, 0]
    elif mvcc_status == 'ON':
        print('当前 新增加节点 mvcc 为 %s, 该用例成功' % mvcc_status)
        return [case, 1]


