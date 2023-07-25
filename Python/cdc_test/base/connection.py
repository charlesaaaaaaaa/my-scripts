import pymysql
import psycopg2
from base.getconf import readcnf
import time

def writeLog(content):
    Today = time.strftime("%Y-%m-%d")
    logName = 'log-%s.log' % Today
    nowTime = time.asctime(time.localtime(time.time())) + ' '
    content = nowTime + content
    with open('.location.txt', 'r') as fi:
        logPath = fi.readlines()[1].split('=')[1]
    fi.close()
    filePath = logPath.replace('file', logName)
    with open(filePath, 'a') as f:
        f.write(content)
    f.close()

class connPg():
    def __init__(self):
        self.conf = readcnf().getKunlunInfo()

    def pgNotReturn(self, dbname, sql):
        conf = self.conf
        self.dbname = dbname
        self.sql    = sql
        try:
            conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['password'], database=dbname)
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as err:
            writeLog('psycopg2 failure:' + sql+ '\n\t' + str(err))
        finally:
            cur.close()
            conn.close()

    def pgReturn(self, dbname, sql):
        conf = self.conf
        self.dbname = dbname
        self.sql    = sql
        try:
            conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['password'],
                                    database=dbname)
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            conn.commit()
            return res
        except Exception as err:
            writeLog('psycopg2 failure:' + sql + '\n\t' + str(err))
            return -1
        finally:
            cur.close()
            conn.close()

class connMy():
    def __init__(self):
        self.conf = readcnf().getMysqlInfo()

    def myNotReturn(self, dbname, sql):
        conf = self.conf
        try:
            conn = pymysql.connect(host=conf['host'], port=int(conf['port']), user=conf['user'], password=conf['password'],
                                    database=dbname)
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
        except Exception as err:
            writeLog('pymysql failure: ' + sql + '\n\t' + str(err))
        finally:
            cur.close()
            conn.close()

    def myReturn(self, dbname, sql):
        conf = self.conf
        try:
            conn = pymysql.connect(host=conf['host'], port=int(conf['port']), user=conf['user'], password=conf['password'],
                                    database=dbname)
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            conn.commit()
            return res
        except Exception as err:
            writeLog('pymysql failure: ' + sql + '\n\t' + str(err))
            return -1
        finally:
            cur.close()
            conn.close()

    def myConn(self, conf, dbname, sql):
        try:
            conn = pymysql.connect(host=conf['host'], port=int(conf['port']), user=conf['user'], password=conf['password'],
                                    database=dbname)
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            conn.commit()
            return res
        except Exception as err:
            writeLog('pymysql failure: ' + sql + '\n\t' + str(err))
            return -1
        finally:
            cur.close()
            conn.close()