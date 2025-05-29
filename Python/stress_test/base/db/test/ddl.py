from base.getconf import *
from base.connection import *
import subprocess
from time import sleep
from threading import Thread

class kill_shard():
    def __init__(self):
        self.conf = readcnf()

    def master(self):
        metaHostSql = "select hostaddr from pg_cluster_meta_nodes where is_master = 't';"
        metaPortSql = "select port from pg_cluster_meta_nodes where is_master = 't';"
        metaHost = connPg().pgReturn('postgres', metaHostSql)[0][0]
        metaPort = connPg().pgReturn('postgres', metaPortSql)[0][0]
        dbHostSql = "select hostaddr from shard_nodes where member_state = 'source' and status = 'active';"
        dbPortSql = "select Port from shard_nodes where member_state = 'source' and status = 'active';"
        conn = connMy(metaHost, metaPort)
        dbPort = conn.myReturn('kunlun_metadata_db', dbPortSql)
        dbHost = conn.myReturn('kunlun_metadata_db', dbHostSql)
        def killShardMaster(host, port):
            command = "ssh kunlun@%s \"ps -ef | grep %s | awk '{print \\$2}' | sed $d | xargs kill -9\"" % (host, port)
            kill = subprocess.Popen(command, shell=True)
            kill.terminate()

        masterNum = len(dbHost)
        writeLog('kill掉shard主')
        for i in range(masterNum):
            l = []
            p = Thread(target=killShardMaster, args=[dbHost[i], dbPort[i]])
            l.append()
            p.start()
        writeLog('等待30s')
        sleep(30)
        sql = 'select count(*) from z1024table_8;'
        cNum = connPg().pgReturn('postgres', sql)
        if cNum:
            writeLog('30秒内可以成功拉走')
        else:
            writeLog('failure: 30s内无法成功拉起')

class createIndex():
    def __init__(self):
        self.db = readcnf().getKunlunInfo()['database']

    def regularIndex(self, tableName):
        colNum = random.randint(1, 3)
        curCol = ''
        curList = []
        colName = ['id', 'grp', 't']
        times = 1
        for i in range(colNum):
            a = random.choice(colName)
            while a in curList:
                a = random.choice(colName)
            if times == 1:
                curCol = a
                times = 0
            else:
                curCol = curCol + ', ' + a
            curList.append(a)
            indexName = '_'.join(curList)
        sql = 'CREATE INDEX %s_%s on %s (%s)  ' % (tableName, indexName, tableName, curCol)
        connPg().pgNotReturn(self.db, sql)

    def uniuqIndex(self, tableName):
        sql = 'CREATE UNIQUE INDEX %s_unique_id on %s (id)' % (tableName, tableName)
        connPg().pgNotReturn(self.db, sql)

class addColumn():
    def __init__(self):
        self.db = readcnf().getKunlunInfo()['database']

    def numrColumn(self, tableName):
        sql = 'ALTER TABLE %s ADD NewColumn_num bigserial' % tableName
        connPg().pgNotReturn(self.db, sql)

    def strColumn(self, tableName):
        sql = 'ALTER TABLE %s ADD NewColumn_text text' % tableName
        connPg().pgNotReturn(self.db, sql)