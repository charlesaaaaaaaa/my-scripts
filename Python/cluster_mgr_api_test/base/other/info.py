import time

from base.other import getconf as conf
from base.other import connect
from base.other import write_log

class master():
    def __init__(self):
        self.meta_info = conf.get_conf_info().klustron_metadata()

    def metadata(self):
        # 这个函数会比较三个元数据节点的主是否为同一个，同一个代表集群正常
        # 如果一致，则返回一个元组
        # 这个元组第0个元素是元数据主节点host
        # 这个元组第1个元素是元数据主节点port
        # 这个元组第2个元素是元数据主节点user
        # 这个元组第3个元素是元数据主节点password
        # 如：('192.168.0.170', 18882, user, port)
        meta_info = self.meta_info
        hosts = meta_info['host'].replace(' ', '').split(',')
        ports = meta_info['port'].replace(' ', '').split(',')
        ip_len = len(hosts)
        sql = "select hostaddr, port, user_name, passwd from meta_db_nodes where member_state = 'source';"
        meta_master_info = []
        for node in range(ip_len):
            conn = connect.My(hosts[node], int(ports[node]), meta_info['user'], meta_info['pass'], 'kunlun_metadata_db')
            res = conn.sql_with_result(sql)[0]
            meta_master_info.append(res)
        if ip_len > 1:
            for i in range(ip_len - 1):
                master_1 = meta_master_info[i]
                master_2 = meta_master_info[i + 1]
                if master_1 != master_2:
                    warn_log = '元数据节点 - 主节点 不一致，退出测试'
                    write_log.w2File().tolog(warn_log)
                    print(warn_log)
                    print('当前有以下几个主')
                    print(meta_master_info)
                    break
        wlog = '当前metadata主节点是: %s' % (str(meta_master_info[0]))
        write_log.w2File().tolog(wlog)
        return meta_master_info[0]

    def cluster_mgr(self):
        # 这个函数会返回一个元组
        # 列表第0个元素是clustermgr主节点的host
        # 列表第1个元素是clustermgr主节点的port
        # 如：
        #    ('192.168.0.170', 18885)
        meta_info = self.metadata()
        conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
        sql = "select hostaddr, port from cluster_mgr_nodes where member_state = 'source'"
        try:
            res = conn.sql_with_result(sql)[0]
        except:
            write_log.w2File().tolog('ERROR： 无法获取cluster_mgr节点，请检查cluster_mgr是否存在')
            write_log.w2File().tolog('退出测试')
            res = '不存在'
        wlog = '当前cluster_mgr主节点是: %s' % (str(res))
        if res == '不存在':
            raise "ERROR： 无法获取cluster_mgr节点，请检查cluster_mgr是否存在"
        write_log.w2File().tolog(wlog)
        return res

class node_info():
    def __init__(self):
        self.meta_info = master().metadata()
        self.meta_conf = conf.get_conf_info().klustron_metadata()

    def get_sql(self, sql):
        meta_master = self.meta_info
        meta_conf = self.meta_conf
        conn = connect.My(meta_master[0], meta_master[1], meta_conf['user'], meta_conf['pass'], 'kunlun_metadata_db')
        hosts = conn.sql_with_result(sql)
        res = []
        for host in hosts:
            tmp = host[0]
            res.append(tmp)
        return res

    def get_res(self, sql):
        meta_master = self.meta_info
        meta_conf = self.meta_conf
        conn = connect.My(meta_master[0], meta_master[1], meta_conf['user'], meta_conf['pass'], 'kunlun_metadata_db')
        res = conn.sql_with_result(sql)
        return res

    def show_all_running_sever_nodes(self):
        # 获取正在运行的server nodes
        # 会返回两个列表
        # 第一个列表是正在运行的可以安装计算节点的机器ip
        # 第二个列表是正在运行的可以安装存储节点的机器ip
        # meta_master = self.meta_info
        # meta_conf = self.meta_conf
        comp_sql = "select hostaddr from server_nodes where machine_type = 'computer' and node_stats = 'running';"
        stor_sql = "select hostaddr from server_nodes where machine_type = 'storage' and node_stats = 'running';"
        comp_hosts = self.get_sql(comp_sql)
        stor_hosts = self.get_sql(stor_sql)
        return comp_hosts, stor_hosts

    def show_all_running_computer(self):
        # 获取所有在运行的计算节点
        # 返回一个列表
        # 列表里面多个元组
        #   每个元组里面第0个元素是ip，第1个元素是port, 2是用户， 3是密码
        sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active';"
        res = self.get_res(sql)
        return res

    def show_all_running_computer_with_id(self):
        # 和上面差不多，但第0个元素是id
        sql = "select id, hostaddr, port, user_name, passwd from comp_nodes where status = 'active';"
        res = self.get_res(sql)
        return res

    def show_all_running_storage(self):
        # 获取所有在运行的存储节点
        # 返回一个元组
        # 元组里面多个元组
        #   每个元组里面第0个元素是ip，第1个元素是port， 2是用户， 3是密码
        sql = "select hostaddr, port, user_name, passwd from shard_nodes where status = 'active';"
        res = self.get_res(sql)
        return res

    def show_all_storage_with_id(self, shard_id):
        sql = "select id, hostaddr, port, user_name, passwd from shard_nodes where shard_id = %s;" % shard_id
        res = self.get_res(sql)
        return res

    def show_all_running_storage_replice(self):
        # 获取所有在运行的存储节点，返回一个元组，元组里面有多个二级元组，每个二级元组都是一个存储shard备节点的信息
        # 二级元组如示：(cluster_id, shard_id, ip, port, user, pwd)
        sql = "select db_cluster_id, shard_id, hostaddr, port, user_name, passwd from shard_nodes where " \
              "member_state = 'replica' and status = 'active';"
        res = self.get_res(sql)
        return res

    def show_all_running_cluster_id(self):
        # 获取所有在运行的存储节点的id
        # 返回一个元组
        # 元组里面多个元组
        #   每个元组里面第0个元素是cluster_id
        #   ((8,),)
        sql = "select id from db_clusters where status = 'inuse';"
        res = self.get_res(sql)
        return res

    def show_all_running_shard_id(self):
        # 获取所在在运行的shard_id
        # 返回一个元组
        # 元组里面多个元组
        #   每个元组里面第0个元素是cluster_id
        #   ((8,),)
        sql = "select distinct(shard_id) from shard_nodes where status = 'active';"
        res = self.get_res(sql)
        return res

    def show_specify_shard_master_node(self, shard_id):
        # 获取指定的shard主节点信息
        # 结果 = [hostaddr, port, user_name, passwd], 返回一级元组
        sql = 'select hostaddr, port, user_name, passwd from shard_nodes where shard_id = "%s" and member_state = ' \
              '"source";' % shard_id
        res = self.get_res(sql)[0]
        return res

    def show_all_running_cluster_id_and_shard_id(self):
        # 获取所有正在支持的shard_id, 带上cluster id
        # 如 ((5, 5,),(5, 6,),) [0]=cluster_id [1] = shard_id
        sql = "select db_cluster_id, id from shards where status = 'inuse';"
        res = self.get_res(sql)
        return res

    def show_all_meta_ip_port_by_clustermgr_format(self):
        # 获取所有metadata的host和port, 返回一个str
        # 返回结果：'192.168.0.0:3006,192.168.0.0:3007,192.168.0.1:3006'
        sql = "select hostaddr, port from meta_db_nodes;"
        result = self.get_res(sql)
        res = ''
        first = 0
        for i in result:
            tmp = '%s:%s' % (i[0], i[1])
            if first == 0:
                res += tmp
                first = 1
            else:
                res += ',%s' % tmp
        return res

    def show_all_running_rcr_info(self):
        # 获取所有正在运行的rcr集群信息
        # 返回结果：
        sql = 'select master_rcr_meta, master_cluster_id, slave_cluster_id from cluster_rcr_infos where status = ' \
              '"running";'
        result = self.get_res(sql)
        return result

    def show_cluster_nick_name(self, cluster_id):
        sql = "select nick_name from db_clusters where id = %s" % cluster_id
        result = self.get_res(sql)[0][0]
        return result

    def show_signal_master_storage_table(self, cluster_id, shard_id, db, tb):
        sql = "select hostaddr, port, user_name, passwd  from shard_nodes where status ='active' and member_state = " \
              "'source' and db_cluster_id = %s and shard_id = %s" % (cluster_id, shard_id)
        stor_node_info = self.get_res(sql)
        conn = connect.My(stor_node_info[0], stor_node_info[1], stor_node_info['user'], stor_node_info['pass'], db)
        sql = 'select * from %s' % tb
        res = conn.sql_with_result(sql)
        return res

    def show_all_running_proxysql(self):
        # 在安装了proxysql的情况下，展示出所有正在活动的proxysql节点的ip host user pass
        # 示例 ((ip, host, user, pass)[, (...), ...])
        sql = "select hostaddr, port, user_name, passwd from proxysql_nodes where status = 'active';"
        res = self.get_res(sql)
        return res

    def compare_shard_master_and_standby(self, dbname):
        # 对比shard主和备的内容是否一致
        meta_info = master().metadata()

        def connmy(sql):
            conn = connect.My(meta_info[0], int(meta_info[1]), meta_info[2], meta_info[3], 'kunlun_metadata_db')
            res = conn.sql_with_result(sql)
            return res

        max_cluster_id_sql = "select max(id) from db_clusters ;"
        max_cluster_id = connmy(max_cluster_id_sql)[0][0]
        storage_nodes_info_sql = "select shard_id, member_state, hostaddr, port, user_name, passwd from shard_nodes " \
                                 "where status = 'active' and db_cluster_id = %s;" % max_cluster_id
        # shard_id_sql = "select shard_id from shard_nodes where status = 'active' and db_cluster_id = %s;" % max_cluster_id
        # shard_id = connmy(shard_id_sql)[0]
        storage_nodes_info = connmy(storage_nodes_info_sql)
        storage_nodes_dict = {}
        for i in range(len(storage_nodes_info)):
            key = ''
            tmp = [storage_nodes_info[i][1], storage_nodes_info[i][2], storage_nodes_info[i][3],
                   storage_nodes_info[i][4], storage_nodes_info[i][5]]
            try:
                key = storage_nodes_dict[storage_nodes_info[i][0]]
            except:
                pass
            if not key:
                storage_nodes_dict.update({storage_nodes_info[i][0]: [tmp]})
            else:
                if storage_nodes_info[i][1] == 'source':
                    storage_nodes_dict[storage_nodes_info[i][0]] = [tmp] + storage_nodes_dict[storage_nodes_info[i][0]]
                else:
                    storage_nodes_dict[storage_nodes_info[i][0]] += [tmp]
        master_shard_dict = {}
        for shard_nodes in storage_nodes_dict:
            for shard_node in storage_nodes_dict[shard_nodes]:
                if shard_node[0] == 'source':
                    master_shard_dict.update({shard_nodes: shard_node})
                    continue
        print(storage_nodes_dict)
        errnum = 1
        for shard_num in storage_nodes_dict:
            master_tables = []
            print('正在检查shard %s' % shard_num)
            master_node = master_shard_dict[shard_num]
            for shard_node in storage_nodes_dict[shard_num]:
                conn = connect.My(shard_node[1], int(shard_node[2]), shard_node[3], shard_node[4], dbname)
                tables = conn.sql_with_result("SELECT TABLE_NAME FROM information_schema.tables where "
                                              "TABLE_SCHEMA = '%s'" % dbname)
                if shard_node[1] in master_node and shard_node[2] in master_node:
                    master_tables = tables
                else:
                    if master_tables != tables:
                        print('ERROR: shard %s 主备表数目不一致 -- 主 : %s , 备 : %s' % (
                        shard_num, master_tables, tables))
                        errnum = 0
                        return errnum
                    else:
                        def get_table_contect(tbname):
                            rep_conn = connect.My(shard_node[1], int(shard_node[2]), shard_node[3], shard_node[4],
                                                  dbname)
                            mas_conn = connect.My(master_node[1], int(master_node[2]), master_node[3], master_node[4],
                                                  dbname)
                            rep_txt = rep_conn.sql_with_result('select * from %s;' % tbname)
                            mas_txt = mas_conn.sql_with_result('select * from %s;' % tbname)
                            return mas_txt, rep_txt
                        for tb_name in master_tables:
                            mas_ctxt, rep_ctxt = get_table_contect(tb_name)
                            if mas_ctxt != rep_ctxt:
                                print('ERROR: shard %s 主备 %s 表内容不一致 -- 主 : %s , 备 : %s' % (
                                    shard_num, tb_name, mas_ctxt, rep_ctxt))
                                errnum = 0
                                return errnum
        return errnum
