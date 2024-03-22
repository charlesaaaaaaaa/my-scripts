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
                    raise warn_log
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

    def show_all_running_sever_nodes(self):
        # 获取正在运行的server nodes
        # 会返回两个列表
        # 第一个列表是正在运行的可以安装计算节点的机器ip
        # 第二个列表是正在运行的可以安装存储节点的机器ip
        meta_master = self.meta_info
        meta_conf = self.meta_conf
        comp_sql = "select hostaddr from server_nodes where machine_type = 'computer' and node_stats = 'running';"
        stor_sql = "select hostaddr from server_nodes where machine_type = 'storage' and node_stats = 'running';"
        def get_sql(sql):
            conn = connect.My(meta_master[0], meta_master[1], meta_conf['user'], meta_conf['pass'], 'kunlun_metadata_db')
            hosts = conn.sql_with_result(sql)
            res = []
            for host in hosts:
                tmp = host[0]
                res.append(tmp)
            return res
        comp_hosts = get_sql(comp_sql)
        stor_hosts = get_sql(stor_sql)
        return comp_hosts, stor_hosts
