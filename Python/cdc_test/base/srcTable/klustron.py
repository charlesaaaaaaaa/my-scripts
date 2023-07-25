from base.connection import connPg as pg
from base.connection import connMy as my
from base.getconf import readcnf
from base.other.otherOpt import *
from configparser import ConfigParser
import subprocess

class info():
    def __init__(self):
        self.conf = readcnf().getConfigDbInfo()

    def metadata(self):
        con = pg()
        sql = "select hostaddr, port, user_name, passwd from pg_cluster_meta_nodes where is_master = 't'"
        info = con.pgReturn('postgres', sql)[0]
        dictInfo = {'host': info[0], 'port': info[1], 'user': info[2], 'password': info[3]}
        sql = 'show mysql_port'
        mysql_protocol_port = con.pgReturn('postgres', sql)[0][0]
        mysqlPort = {'mysql_protocol_port': mysql_protocol_port}
        Info = dict(mysqlPort, **dictInfo)
        writeLog('当前metadata信息为\n\t%s\n' % Info)
        return Info

    def clusterInfo(self):
        metaConf = info.metadata(self)
        standbyNodeInfo = {'metadata': metaConf}
        con = my()
        sql = "select distinct(shard_id) from shard_nodes"
        shard_id = con.myConn(metaConf, 'kunlun_metadata_db', sql)
        for i in shard_id:
            shardId = 'shard_%s' % i
            sql = 'select hostaddr, port, user_name, passwd from shard_nodes where shard_id = %s and member_state = "replica" limit 1' % i
            signalNodeInfo = con.myConn(metaConf, 'kunlun_metadata_db', sql)[0]
            dictInfo = {'host': signalNodeInfo[0], 'port': signalNodeInfo[1], 'user': signalNodeInfo[2], 'password': signalNodeInfo[3]}
            nodeInfo = {shardId : dictInfo}
            standbyNodeInfo = dict(standbyNodeInfo, **nodeInfo)
        writeLog('当前metadata及存储节点信息为\n\t%s\n' % standbyNodeInfo)
        return standbyNodeInfo

    def getMetadataList(self):
        con = pg()
        sql = "select hostaddr, port, user_name, passwd from pg_cluster_meta_nodes"
        info = con.pgReturn('postgres', sql)
        metadataList = ''
        for i in info:
            tmpList = '%s:%s,' % (i[0], i[1])
            metadataList = metadataList + tmpList
        metadataList = metadataList.strip(',')
        writeLog('当前metadata db为： %s' % metadataList)
        return metadataList

    def clusterName(self):
        con = pg()
        sql = "select name from db_clusters limit 1"
        infos = info().metadata()
        cluName = my().myConn(infos, 'kunlun_metadata_db', sql)[0][0]
        writeLog('当前cluster_name 为：%s' % cluName)
        return cluName
