import time
from base.api import post
from base.other import write_log, connect, info, sys_opt
import random


def print_log(txt):
    write_log.w2File().tolog(txt)
    print(txt)

def test_case():
    case = 'ticket_#1930'
    print_log('开始测试 %s' % case)
    print_log('第一步： 创建集群，创建时开启global mvcc')
    print_log('尝试删除正在运行的集群')
    post.cluster_setting(0).delete_cluster_all()
    # other_paras_dict这个字典的所有key和value都要str类型的，不能是其它类型的，因为cluster_mgr api就是这样用的
    other_paras_dict = {'enable_global_mvcc': "1"}
    nick_name = 'ticket_1930'
    cre_res = post.cluster_setting(0).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=1, nodes=3,
                                                    comps=1, max_storage_size=1024, max_connections=2000,
                                                    cpu_limit_node='quota', innodb_size=1024, cpu_cores=8,
                                                    rocksdb_block_cache_size_M=1024, fullsync_level=1,
                                                    data_storage_MB=1024, log_storage_MB=1024,
                                                    other_paras_dict=other_paras_dict)
    if cre_res == 0:
        return [case, 0]

    print_log('第二步： 新增shard')
    cluster_id = cre_res[1]['cluster_id']
    add_res = post.cluster_setting(0).add_shards(cluster_id=cluster_id, shards=1, nodes=3)
    if add_res == 0:
        return [case, 0]

    print_log('设置变量')
    # pgs = {'statement_timeout': 7200000, 'mysql_read_timeout': 7200, 'mysql_write_timeout': 7200,
    #        'lock_timeout': 7200000, 'log_min_duration_statement': 7200000}
    mys = {'lock_wait_timeout': 7200, 'net_read_timeout': 7200, 'net_write_timeout': 7200,
           'innodb_lock_wait_timeout': 7200}
    # for i in pgs:
    #     sys_opt.setting_variable('computer', i, pgs[i])
    for i in mys:
        sys_opt.setting_variable('storage', i, mys[i])

    print_log('第三步： 进行写操作')
    comp_sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active' " \
               "and db_cluster_id = %s;" % cluster_id
    meta_info = info.master().metadata()
    conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
    comps = conn.sql_with_result(comp_sql)
    # 在所有计算节点中随机选择其中一个
    comp_info = random.choices(comps)
    print_log('       开始对 %s 进行写操作' % comp_info)
    try:
        conn = connect.Pg(host=comp_info[0][0], port=int(comp_info[0][1]), user=comp_info[0][2], pwd=comp_info[0][3],
                          db='postgres')
        create_table_sql = "CREATE TABLE measurement1 ( \
                logdate date not null, \
                peaktemp int, \
                unitsales int \
                ) PARTITION BY RANGE (logdate); \
                create table m1_p0 partition of measurement1 for values from (minvalue) to ('20201231'); \
                create table m1_p1 partition of measurement1 for values from ('20201231') to ('20211231'); \
                create table m1_p2 partition of measurement1 for values from ('20211231') to ('20221231'); \
                create table m1_p3 partition of measurement1 for values from ('20221231') to ('20231231'); \
                create table m1_p4 partition of measurement1 for values from ('20231231') to (maxvalue);"
        conn.ddl_sql(create_table_sql)
        insert_sql = "insert into measurement1 values('20080808',1,1),('20210101',6,6),('20220101',7,7)," \
                     "('20230606',8,8),('20241001',9,9);"
        conn.ddl_sql(insert_sql)
        conn.close()
    except Exception as err:
        print_log('写操作失败')
        print_log(err)
        return [case, 0]

    print_log('第四步：     检查 enable_global_mvcc 参数是否开启')
    print_log('等待20s')
    time.sleep(20)
    try:
        def connmy(sql):
            conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
            res = conn.sql_with_result(sql)
            return res
        max_cluster_id_sql = "select max(id) from db_clusters ;"
        max_shard_id_sql = "select max(shard_id) from shard_nodes;"
        max_cluster_id = connmy(max_cluster_id_sql)[0][0]
        max_shard_id = connmy(max_shard_id_sql)[0][0]
        new_master_sql = "select hostaddr, port, user_name, passwd from shard_nodes where db_cluster_id = %s and " \
                         "shard_id = %s and member_state = 'source';" % (max_cluster_id, max_shard_id)
        new_slave_sql = "select hostaddr, port, user_name, passwd from shard_nodes where db_cluster_id = %s and " \
                        "shard_id = %s and member_state != 'source';" % (max_cluster_id, max_shard_id)
        new_slave_master_node = connmy(new_slave_sql)
        new_shard_master_node = connmy(new_master_sql)[0]
        print_log('当前新增加shard的 主节点是: %s:%s' % (new_shard_master_node[0], new_shard_master_node[1]))
        conn = connect.My(new_shard_master_node[0], int(new_shard_master_node[1]), new_shard_master_node[2],
                          new_shard_master_node[3], 'mysql')
        sql = "show variables like 'enable_global_mvcc';"
        mvcc_status = conn.sql_with_result(sql)[0][1]
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
        print('当前 新增加节点 mvcc 为 %s, 检查成功' % mvcc_status)
    sql = "show slave status;"
    print('等待10s后检查备节点状态')
    for i in range(len(new_slave_master_node)):
        conn = connect.My(new_slave_master_node[i][0], int(new_slave_master_node[i][1]), new_slave_master_node[i][2],
                    new_slave_master_node[i][3], 'mysql')
        slave_status = conn.sql_with_result(sql)[0]
        Last_IO_Errno = slave_status[36]
        Last_IO_Error = slave_status[37]
        if Last_IO_Errno == 0 and not Last_IO_Error:
            print('succ: node - %s:%s\n\t Last_IO_Errno = %s\n\tLast_IO_Error = %s' % (new_slave_master_node[i][0],
                                        new_slave_master_node[i][1], Last_IO_Errno, Last_IO_Error))
        else:
            print('ERROR: node - %s:%s\n\t Last_IO_Errno = %s\n\tLast_IO_Error = %s' % (new_slave_master_node[i][0],
                                        new_slave_master_node[i][1], Last_IO_Errno, Last_IO_Error))

    print('检查所有主备复制是否一制')
    res = info.node_info().compare_shard_master_and_standby('postgres_$$_public')
    return [case, res]
    # storage_nodes_info_sql = "select shard_id, member_state, hostaddr, port, user_name, passwd from shard_nodes " \
    #                          "where status = 'active' and db_cluster_id = %s;" % max_cluster_id
    # storage_nodes_info = connmy(storage_nodes_info_sql)
    # storage_nodes_dict = {}
    # for i in range(len(storage_nodes_info)):
    #     tmpdict = {storage_nodes_info[i][0]: storage_nodes_info}
    #     storage_nodes_dict.update(tmpdict)
    # print(storage_nodes_dict)
