import pymysql
import psycopg2
from bin import other_opt

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


def meta_master():
    # 从init配置文件里面获取对应的meta data节点信息
    meta_info_dict_init = other_opt.OtherConf('./conf/init.conf').read('meta_info')
    meta_info_dict, meta_sql_res = {}, []
    # 再把它重新格式化到另一个字典里面去
    for i in meta_info_dict_init:
        tmp_list = str(meta_info_dict_init[i]).replace(' ', '').split(',')
        meta_info_dict[i] = tmp_list
    host, port, user, pwd = meta_info_dict['host'], meta_info_dict['port'], meta_info_dict['user'], meta_info_dict['pass']
    sql = 'select hostaddr, port, user_name, passwd from meta_db_nodes where member_state = "source";'

    def show_meta_master():
        # 初始化并返回一个列表，取第一个元数据节点的选出的主元数据节点，跟其它的元数据节点进行对比
        # 不同的话会被放进这个列表，正常情况下这个列表应该只有一个值
        init_res = []
        for i in range(len(host)):
            try:
                meta_conn = My(host=host[i], port=port[i], user=user[i], password=pwd[i], db='kunlun_metadata_db')
                res = meta_conn.sql_with_res(sql)[0]
                meta_sql_res.append(res)
                if not init_res:
                    init_res.append(res)
                else:
                    if res != init_res:
                        print('存在与当前主元数据节点[%s:%s]不同的主元数据节点[%s:%s], 于节点[%s:%s]检查得出'
                              '' % (init_res[0], init_res[1], res[0], res[1], host[i], port[i]))
                        init_res.append(res)
            except Exception as err:
                print('%s:%s 连接失败，ERROR：%s' % (host[i], port[i], err))
            finally:
                meta_conn.close()
            return init_res
    res_list = show_meta_master()
    return res_list


class meta:
    def __init__(self):
        meta_info = meta_master()[0]
        meta_host, meta_port, meta_user, meta_password = meta_info[0], meta_info[1], meta_info[2], meta_info[3]
        conn = My(host=meta_host, port=int(meta_port), user=meta_user, password=meta_password, db='kunlun_metadata_db')
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

    def all_comps_mysqlport(self):
        sql = "select hostaddr, mysql_port, user_name, passwd from comp_nodes where status = 'active';"
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
