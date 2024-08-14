import random

import pymysql
import psycopg2
from res.getconf import readcnf
import time

def writeLog(content):
    Today = time.strftime("%Y-%m-%d")
    logName = 'log-%s.log' % Today
    nowTime = time.asctime(time.localtime(time.time())) + ' '
    content = nowTime + content + '\n'
    filePath = './log/' + logName
    with open(filePath, 'a') as f:
        f.write(content)
    f.close()

# class connPg():
#     def __init__(self):
#         self.conf = readcnf().getKunlunInfo()
#
#     def pgNotReturn(self, sql):
#         conf = self.conf
#         conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['pwd'], database='postgres')
#         cur = conn.cursor()
#         cur.execute(sql)
#         conn.commit()
#         cur.close()
#         conn.close()
#
#     def pgReturn(self, sql):
#         conf = self.conf
#         conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['pwd'],
#                                 database='postgres')
#         cur = conn.cursor()
#         cur.execute(sql)
#         res = cur.fetchall()
#         conn.commit()
#         cur.close()
#         conn.close()
#         return res
#
#     def pgReturn_other(self, host, port, user, password, sql):
#         conn = psycopg2.connect(host=host, port=int(port), user=user, password=password, database='postgres')
#         cur = conn.cursor()
#         cur.execute(sql)
#         res = cur.fetchall()
#         conn.commit()
#         cur.close()
#         conn.close()
#         return res


class connMy():
    def __init__(self, Host, Port, User, Pwd, Db):
        self.Host = Host
        self.Port = Port
        self.User = User
        self.Pwd = Pwd
        self.Db = Db

    def myNotReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=int(self.Port), user=self.User, password=self.Pwd,database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    def myReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=int(self.Port), user=self.User, password=self.Pwd,database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        conn.close()
        return res


class connMeta():
    def __init__(self):
        self.conf = readcnf().getKunlunInfo()
        self.Host = self.conf['meta_host']
        self.Port = self.conf['meta_port']
        self.User = self.conf['meta_user']
        self.Pwd = self.conf['meta_pass']
        self.Db = 'kunlun_metadata_db'

    def myNotReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=int(self.Port), user=self.User, password=self.Pwd, database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    def myReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=int(self.Port), user=self.User, password=self.Pwd, database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        conn.close()
        return res


class connPg():
    def __init__(self):
        self.conf = readcnf().getKunlunInfo()
        sql = 'select hostaddr, port, user_name, passwd from comp_nodes where status = "active" limit 1;'
        try:
            self.pg_info = connMeta().myReturn(sql)[0]
        except:
            print("未获取到有效的集群节点信息，请检查当前元数据节点 [%s:%s] 下是否存在klustron集群" % (self.conf['meta_host'],
                  self.conf['meta_port']))
            exit(0)

    def pgNotReturn(self, sql):
        conf = self.pg_info
        conn = psycopg2.connect(host=conf[0], port=conf[1], user=conf[2], password=conf[3], database='postgres')
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    def pgReturn(self, sql):
        conf = self.pg_info
        conn = psycopg2.connect(host=conf[0], port=conf[1], user=conf[2], password=conf[3], database='postgres')
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return res

    def pgReturn_other(self, host, port, user, password, sql):
        conn = psycopg2.connect(host=host, port=int(port), user=user, password=password, database='postgres')
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return res