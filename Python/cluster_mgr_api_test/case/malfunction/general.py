from base.api.get import *
from base.api.post import *
from base.other.connect import *
from base.other.getconf import *
from base.other.info import *
from base.other.sys_opt import *
import subprocess

class test_step:
    def __init__(self):
        self.meta_master_info = master().metadata()
        self.meta_conf = getconf.get_conf_info().klustron_metadata()

    def meta_sql(self, sql, result_or_not):
        meta_master_info = self.meta_master_info
        conn = connect.My(meta_master_info[0], int(meta_master_info[1]), meta_master_info[2], meta_master_info[3]
                          , 'mysql')
        if result_or_not == '0':
            conn.ddl_sql(sql)
        elif result_or_not == '1':
            res = conn.sql_with_result(sql)
            conn.close()
            return res

    def Create_cluster(self, shard, shard_nodes, comps, num, other_paras, delay_time):
        # 创建一个集群
        nick_name = 'mulfunction_%s' % num
        res = cluster_setting(delay_time).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=shard,
                                              nodes=shard_nodes,
                                              comps=comps, max_storage_size=1024, max_connections=2000,
                                              cpu_limit_node='quota', innodb_size=1024, cpu_cores=8,
                                              rocksdb_block_cache_size_M=1024, fullsync_level=1,
                                              data_storage_MB=1024, log_storage_MB=1024,
                                              other_paras_dict=other_paras)
        return res

    def restart_meta_master(self):
        # 重启 meta_data 集群主节点
        meta_master_info = self.meta_master_info
        print('当前meta_data集群主节点是 -- [%s: %s]' % (meta_master_info[0], meta_master_info[1]))
        ssh_str = "ssh %s@%s 'ps -ef | grep %s | grep basedir' | grep default" % \
                  (self.meta_conf['sys_user'], meta_master_info[0], meta_master_info[1])
        basedir_res = subprocess.Popen(ssh_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = basedir_res.communicate()
        print(str(stdout.decode()))
        basedir = str(stdout.decode()).split('basedir=')[1].split(' ')[0]
        print('其basedir是 -- [%s]\n\t正在重启主节点 ... ' % basedir)
        basedir += '/dba_tools'
        restart_str = "ssh %s@%s 'cd %s && ps -ef | grep %s | awk '{print \\$2}' | xargs kill -9 ; bash startmysql.sh %s'"\
                      % (self.meta_conf['sys_user'], meta_master_info[0], basedir, meta_master_info[1], meta_master_info[1])
        print(restart_str)
        subprocess.run(restart_str, shell=True)

    def set_meta_master_only(self):
        # 设置 meta_data 集群主节点 为 只读
        meta_master_info = self.meta_master_info
        set_sql = 'set global super_read_only = ON;'
        get_sql = "show variables like 'super_read_only';"
        old_value = self.meta_sql(get_sql, 1)[0][1]
        print('当前主节点 [%s:%s] super_read_only 为 [%s]' % (meta_master_info[0], meta_master_info[1], old_value))
        print('开始设置: sql = [%s]' % set_sql)
        self.meta_sql(set_sql, 0)
        new_value = self.meta_sql(set_sql, 1)[0][1]
        print('当前主节点 [%s:%s] super_read_only 为 [%s]' % (meta_master_info[0], meta_master_info[1], new_value))
        if old_value == 'OFF' and new_value == 'ON':
            print('设置成功！')
            return 0
        else:
            print('设置失败！')
            return 1



