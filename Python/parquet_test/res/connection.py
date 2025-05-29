import pymysql
import psycopg2
from res.read_conf import *


class My:
    def __init__(self, host, port, user, password, db):
        self.conn = pymysql.connect(host=host, port=int(port), user=user, password=password, database=db)
        self.cur = self.conn.cursor()

    def sql(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        conn.commit()

    def sql_with_res(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        return res

    def close(self):
        conn = self.conn
        cur = self.cur
        cur.close()
        conn.close()


class meta:
    def __init__(self):
        conf = conf_info()
        meta_host = conf['meta_host']
        meta_port = conf['meta_port']
        meta_user = conf['meta_user']
        meta_passwoed = conf['meta_pass']
        conn = My(host=meta_host, port=int(meta_port), user=meta_user, password=meta_passwoed, db='kunlun_metadata_db')
        res = conn.sql_with_res('select hostaddr, port, user_name, passwd from meta_db_nodes where member_state = "source";')[0]
        conn.close()
        self.meta_master = My(host=res[0], port=res[1], user=res[2], password=res[3], db='kunlun_metadata_db')

    def get_info(self, sql):
        res = self.meta_master.sql_with_res(sql)
        self.meta_master.close()
        return res

    def all_comps(self):
        sql = "select hostaddr, port, user_name, passwd from comp_nodes where status = 'active';"
        res = self.get_info(sql)
        return res

    def kunlun_version(self):
        sql = "select distinct(nodemgr_bin_path) from server_nodes;"
        res = self.get_info(sql)
        version_list = []
        for i in res:
            tmp_list = str(i[0]).split('/')
            for tmp_str in tmp_list:
                if 'kunlun-node-manager-' in tmp_str:
                    tmp_version = tmp_str.split('kunlun-node-manager-')[1]
                    version_list.append(tmp_version)
        version_len = len(version_list)
        diff_times = 0
        if version_len > 1:
            for i in range(0, version_len - 1):
                if version_list[i] != version_list[i+1]:
                    diff_times += 1
        if diff_times == 0:
            return version_list[0]
        else:
            return 0

    def all_server_host(self):
        sql = "select distinct(hostaddr) from server_nodes where hostaddr != 'pseudo_server_useless';"
        res = self.get_info(sql)
        return res

    def all_meta_format(self):
        # 返回 192.168.0.129:59301,192.168.0.129:59304,192.168.0.129:59307
        sql = "select hostaddr, port from meta_db_nodes;"
        tmp = self.get_info(sql)
        res = ''
        for i in tmp:
            host_port = '%s:%s' % (i[0], i[1])
            if res:
                res += ',%s' % host_port
            else:
                res = host_port
        return res

    def all_cluster_id(self):
        sql = "select id from db_clusters where status = 'inuse';"
        res = self.get_info(sql)
        return res

    def shard_id(self, cluster_id):
        sql = "select distinct(shard_id) from shard_nodes where status = 'active' and db_cluster_id = %s;" % cluster_id
        res = self.get_info(sql)[0][0]
        return res


class pgsql:
    def __init__(self, node_info_list, db):
        node_info = node_info_list
        self.conn = psycopg2.connect(host=node_info[0], port=int(node_info[1]), user=node_info[2], password=node_info[3], dbname=db)
        self.cur = self.conn.cursor()

    def sql(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        conn.commit()

    def sql_with_res(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        return res

    def close(self):
        conn = self.conn
        cur = self.cur
        cur.close()
        conn.close()
