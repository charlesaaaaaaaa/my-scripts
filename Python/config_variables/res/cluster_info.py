from res.connection import *
from res.getconf import *


class getMetadata():
    def __init__(self):
        self.dbInfo = readcnf().getKunlunInfo()

    def Master(self):
        sql = "select hostaddr, port, user_name, passwd from pg_cluster_meta_nodes where is_master = 't';"
        masterInfo = connPg().pgReturn(sql)
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
        hostInfo = self.Hosts()
        storage_info = {}
        conn = connPg()
        for host in hostInfo:
            sql = 'select hostaddr, port, user_name, passwd from pg_shard_node where hostaddr = \'%s\'' % host
            values = conn.pgReturn(sql)
            tmpDict = {host[0]: values}
            storage_info.update(tmpDict)
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
        Versions = readcnf().getKunlunInfo()['version']
        server_path_info = {}
        conn = connPg()
        dataSql = 'show unix_socket_directories'
        for host in serverInfo:
            hostList = []
            for infos in serverInfo[host]:
                dataDir = conn.pgReturn_other(infos[0], infos[1], infos[2], infos[3], dataSql)[0][0]
                basePath = dataDir.split('/server_datadir')[0]
                baseDir = basePath + '/instance_binaries/computer/' + str(infos[1]) + '/kunlun-server-' + Versions
                dataDir += '/postgresql.conf'
                tmpList = [baseDir, dataDir, infos[1]]
                hostList.append(tmpList)
            tmpDict = {host: hostList}
            server_path_info.update(tmpDict)
        return server_path_info