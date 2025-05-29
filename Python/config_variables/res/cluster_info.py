from res.connection import *
from res.getconf import *
import subprocess

class getMetadata():
    def __init__(self):
        self.dbInfo = readcnf().getKunlunInfo()

    def Master(self):
        sql = "select hostaddr, port, user_name, passwd from meta_db_nodes where member_state = 'source';"
        masterInfo = connMeta().myReturn(sql)
        # [hostaddr, port, user_name, passwd]
        return masterInfo

class getStorage():
    def __init__(self):
        self.metaInfo = getMetadata().Master()
        self.db = 'kunlun_metadata_db'

    def Hosts(self):
        sql = 'select distinct(hostaddr) from pg_shard_node;'
        conn = connPg()
        storage_host_info = conn.pgReturn(sql)
        return storage_host_info

    def Infos(self):
        # hostInfo = self.Hosts()
        storage_info = {}
        sql = "select distinct(hostaddr) from shard_nodes where status = 'active';"
        values = connMeta().myReturn(sql)
        for i in values:
            sql = "select hostaddr, port, user_name, passwd from shard_nodes where status = 'active' and hostaddr = '%s'" % i[0]
            res = connMeta().myReturn(sql)
            tmp_dict = {i[0]: res}
            storage_info.update(tmp_dict)
        return storage_info

    def Paths(self):
        db = 'mysql'
        storage_path_dict = {}
        stoarge_info = self.Infos()
        baseSql = 'show variables like "basedir"'
        dataSql = 'show variables like "datadir"'
        for host in stoarge_info:
            hostList = []
            for infos in stoarge_info[host]:
                conn = connMy(infos[0], infos[1], infos[2], infos[3], db)
                baseDir = conn.myReturn(baseSql)[0][1]
                dataDir = conn.myReturn(dataSql)[0][1]
                dataDir += '%s.cnf' % infos[1]
                tmpList = [baseDir, dataDir, infos[1]]
                hostList.append(tmpList)
            tmpDict = {host: hostList}
            storage_path_dict.update(tmpDict)
        return storage_path_dict

class getServer():
    def __init__(self):
        self.metaInfo = getMetadata().Master()
        self.db = 'kunlun_metadata_db'
        sql = 'select kunlun_version();'
        res = connPg().pgReturn(sql)[0][0]
        #self.version = res.split(' ')[0].split('-')[1].replace('-', '.')
        self.version = res.split('-')[1]
        self.sysUser = readcnf().getKunlunInfo()['sys_user']

    def Infos(self):
        #sql =
        meta = self.metaInfo[0]
        db = self.db
        server_info = {}
        hostSql = 'select distinct(hostaddr) from comp_nodes where status = "active"'
        conn = connMy(meta[0], meta[1], meta[2], meta[3], db)
        hostInfo = conn.myReturn(hostSql)
        for host in hostInfo:
            sql = 'select hostaddr, port, user_name, passwd from comp_nodes where status = "active" and hostaddr = "%s"' % host
            server_conn_info = conn.myReturn(sql)
            server_conn_info = list(server_conn_info)
            tmpDict = {host[0]: server_conn_info}
            server_info.update(tmpDict)
        return server_info

    def Paths(self):
        serverInfo = self.Infos()
        Versions = self.version
        server_path_info = {}
        conn = connPg()
        dataSql = 'show data_directory'
        for host in serverInfo:
            hostList = []
            for infos in serverInfo[host]:
                dataDir = conn.pgReturn_other(infos[0], infos[1], infos[2], infos[3], dataSql)[0][0]
                get_basedir = "ssh %s@%s 'ps -ef | grep %s | grep -v grep | grep bin' | " \
                              "grep %s" % (self.sysUser, infos[0], infos[1], dataDir)
                basedir_res = subprocess.Popen(get_basedir, shell=True, stdout=subprocess.PIPE)
                baseDir = str(basedir_res.stdout.readlines()).split(' ')[-3].split('/bin')[0]
                dataDir += '/postgresql.conf'
                tmpList = [baseDir, dataDir, infos[1]]
                hostList.append(tmpList)
            tmpDict = {host: hostList}
            server_path_info.update(tmpDict)
        return server_path_info
