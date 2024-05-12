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

class connPg():
    def __init__(self):
        self.conf = readcnf().getKunlunInfo()

    def pgNotReturn(self, sql):
        conf = self.conf
        conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['pwd'], database='postgres')
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()

    def pgReturn(self, sql):
        conf = self.conf
        conn = psycopg2.connect(host=conf['host'], port=conf['port'], user=conf['user'], password=conf['pwd'],
                                database='postgres')
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

class connMy():
    def __init__(self, Host, Port, User, Pwd, Db):
        self.Host = Host
        self.Port = Port
        self.User = User
        self.Pwd = Pwd
        self.Db = Db

    def myNotReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=self.Port, user=self.User, password=self.Pwd,database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        conn.commit()

    def myReturn(self, sql):
        conn = pymysql.connect(host=self.Host, port=self.Port, user=self.User, password=self.Pwd,database=self.Db)
        cur = conn.cursor()
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        conn.close()
        return res
