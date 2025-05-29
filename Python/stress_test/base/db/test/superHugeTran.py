import random
import psycopg2
from base.other.OPT import *
from base.connection import *
from base.getconf import *

def genG():
    k, m, g = '', '', ''
    for i in range(1024):
        k = k + 'a'
    for i in range(1024):
        m = m + k
    for i in range(1024):
        g = g + m
    return g

class forSuperHugeTran():
    def __init__(self):
        self.kunlunInfo = readcnf().getKunlunInfo()

    def oneTran_500G(self, tableName):
        text = genG()
        conf = self.kunlunInfo
        conn = psycopg2.connect(host=conf['host'], port=int(conf['port']), user=conf['user'],
                                password=conf['password'], database=conf['database'])
        cur = conn.cursor()
        data = str((10001, text))
        cur.execute('BEGIN;')
        for i in range(500):
            sql = 'insert into %s values%s' % (tableName, data)
            cur.execute(sql)
            print('|%s: %s/500|' % (tableName, str(i + 1)), end='')
        cur.execute('COMMIT;')
        conn.commit()
        cur.close()
        conn.close()
        print('%s 500G done' % tableName)

    def updateTable_t1_t2_forOneCommit(self, tableName):
        db = self.kunlunInfo['database']
        a = random.randint(1, 2)
        if a ==1 :
            sql = 'update from %s set grp = 10001' % tableName
        elif a == 2:
            data = random.choice('asdfqwer')
            num = random.randint(5, 25)
            datas = ''
            for i in range(num):
                datas = datas + data
            sql = 'update from %s set t = %s' % (tableName, datas)
        connPg().pgAutoNotReturn(db, sql)

    def insert1row_10G(self, tableName):
        db = self.kunlunInfo['database']
        i1G = genG()
        i10G = ''
        for i in range(10):
            i10G = i10G + i1G
        grp = 10002
        sql = 'insert into %s values(' % tableName + grp + ', %s)' % i10G
        connPg().pgNotReturn(db, sql)

    def update1rowAnd1000Row_10G(self, tableName):
        db = self.kunlunInfo['database']
        i1G = genG()
        i10G = ''
        for i in range(10):
            i10G = i10G + i1G
        sql = "update from %s where text = '%s'" % (tableName, i10G)
        connPg().pgNotReturn(db, sql)
