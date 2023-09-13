import random

import pymysql
import psycopg2
from bin.getconf import readcnf
import time

def writeLog(content):
    Today = time.strftime("%Y-%m-%d")
    logName = 'log-%s.log' % Today
    nowTime = time.asctime(time.localtime(time.time())) + ' '
    content = '\n' + nowTime + content
    filePath = './log/' + logName
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
            cur.close()
            conn.close()
        except Exception as err:
            writeLog('psycopg2 failure: ' + '\n\t' + str(err))
            retry_times = int(readcnf().getTestInfo()['retry_times'])
            mark_num = random.randint(1, 100000)
            for i in range(retry_times):
                try:
                    conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'],
                                            password=conf['password'], database=dbname)
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    break
                except Exception as err:
                    writeLog('psycopg2 failure: %s 第 %s 重试' % (mark_num, i+1) + '\n\t' + str(err))
                    if i == retry_times - 1:
                        writeLog('当前sql失败 %s' % mark_num)

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
            cur.close()
            conn.close()
            return res
        except Exception as err:
            #writeLog('psycopg2 failure:' + sql + '\n\t' + str(err))
            writeLog('psycopg2 failure: ' + str(err))
            return -1

    def pgAutoNotReturn(self, dbname, sql):
        conf = self.conf
        self.dbname = dbname
        self.sql = sql
        try:
            conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['password'],
                                    database=dbname)
            conn.autocommit()
            cur = conn.cursor()
            cur.execute(sql)
            conn.commit()
            cur.close()
            conn.close()
        except Exception as err:
            writeLog('psycopg2 failure: ' + '\n\t' + str(err))
            retry_times = int(readcnf().getTestInfo()['retry_times'])
            mark_num = random.randint(1, 100000)
            for i in range(retry_times):
                try:
                    conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'],
                                            password=conf['password'], database=dbname)
                    cur = conn.cursor()
                    cur.execute(sql)
                    conn.commit()
                    cur.close()
                    conn.close()
                    break
                except Exception as err:
                    writeLog('psycopg2 failure: %s 第 %s 重试' % (mark_num, i + 1) + '\n\t' + str(err))
                    if i == retry_times - 1:
                        writeLog('当前sql失败 %s' % mark_num)


class connMy():
    def __init__(self, Host, Port):
        self.Host = Host
        self.Port = Port
#
#     def myNotReturn(self, dbname, sql):
#         conf = self.conf
#         try:
#             conn = pymysql.connect(host=conf['host'], port=int(conf['port']), user=conf['user'], password=conf['password'],
#                                     database=dbname)
#             cur = conn.cursor()
#             cur.execute(sql)
#             conn.commit()
#         except Exception as err:
#             writeLog('pymysql failure: ' + sql + '\n\t' + str(err))
#         finally:
#             cur.close()
#             conn.close()
#
    def myReturn(self, dbname, sql):
        host = self.Host
        port = self.Port
        try:
            conn = pymysql.connect(host=host, port=port, user='pwd', password='pgx_pgx',
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
#
#     def myConn(self, conf, dbname, sql):
#         try:
#             conn = pymysql.connect(host=conf['host'], port=int(conf['port']), user=conf['user'], password=conf['password'],
#                                     database=dbname)
#             cur = conn.cursor()
#             cur.execute(sql)
#             res = cur.fetchall()
#             conn.commit()
#             return res
#         except Exception as err:
#             writeLog('pymysql failure: ' + sql + '\n\t' + str(err))
#             return -1
#         finally:
#             cur.close()
#             conn.close()