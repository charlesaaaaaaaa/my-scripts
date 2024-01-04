import psycopg2
import pymysql
import subprocess
from base.get_conf import *

class dbs():
    def __init__(self, types, db):
        # types = 1, klustron; types = 2: create sql for klustron
        # types = 0, otherdb
        self.types = types
        self.db = db
        self.p = ''
        dbtype = get_variables().dbtype()
        self.dbtype = dbtype
        if types == 2:
            self.conf = getconf(1)
        else:
            self.conf = getconf(types)
        host, port, pwd, user = self.conf['host'], self.conf['port'], self.conf['pass'], self.conf['user']
        if types == 2:
            self.conn = 'psql postgres://%s:%s@%s:%s/%s -c' % (user, pwd, host, port, db)
        if types == 1:
            self.conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, database=db)
            self.cur = self.conn.cursor()
        if types == 0:
            if dbtype == 'pgsql':
                self.conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, database=db)
                self.cur = self.conn.cursor()
            elif dbtype == 'mysql':
                self.conn = pymysql.connect(host=host, port=int(port), user=user, password=pwd, database=db)
                self.cur = self.conn.cursor()

    def commit(self):
        self.conn.commit()

    def execsql_res(self, sql):
        types = self.types
        db = self.db
        conf = getconf(types)
        host, port, pwd, user = conf['host'], conf['port'], conf['pass'], conf['user']
        if types == 1:
            dbtype = get_variables().dbtype()
            conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, database=db)
            cur = conn.cursor()
            cur.execute(sql)
            res = cur.fetchall()
            return res

    def execsql(self, sql):
        # if '$$' in sql:
        #     sql = str(sql).replace('$$', '\\$\\$')
        if '$' in sql:
            sql = str(sql).replace('$', '\\$')
        type = str(sql).split()[0]
        if self.types == 2 and type == 'select' or self.types == 2 and type == 'SELECT':
            print(sql)
            sql = "%s \"%s\"" % (self.conn, sql)
            p = subprocess.Popen(sql, shell=True, stdout=subprocess.PIPE)
            out = p.stdout.readlines()
            return out
        elif self.types == 2 and type != 'select' or self.types == 2 and type != 'SELECT':
            print(sql)
            sql = "%s \"%s\"" % (self.conn, sql)
            try:
                p = subprocess.Popen(sql, shell=True, stdout=subprocess.PIPE)
            except Exception as err:
                if 'cannot copy from foreign table' in err:
                    print(err)
                else:
                    exit(1)
            return p.stdout.read()
        else:
            #print('%s, %s' % (self.types, sql))
            print('Converted SQL statement by this script: %s' % sql)
            try:
                self.cur.execute(sql)
                self.conn.commit()
                return dbs(self.types, self.db)
            except Exception as err:
                print('%s ERROR: %s' % (self.dbtype, err))

    def execsql_noprint(self, sql):
        type = str(sql).split()[0]
        if self.types == 2 and type == 'select' or self.types == 2 and type == 'SELECT':
            sql = "%s \"%s\"" % (self.conn, sql)
            p = subprocess.Popen(sql, shell=True, stdout=subprocess.PIPE)
            try:
                out = p.stdout.readlines()[2].decode("utf-8")
                out = out.replace(' ', '')
                out = out.replace('\n', '')
                return out
            except:
                return 'done'

    def getres(self, sql):
        try:
            self.cur.execute(sql)
            res = self.cur.fetchall()
            self.conn.commit()
            return res
        except Exception as err:
            print('%s ERROR: %s' % (self.dbtype, err))

    def autocomm(self):
        self.conn.autocommit

    def close(self):
        self.cur.close()
        self.conn.close()

class run_sql():
    def __init__(self):
        pass

    def get_mysql_primary_key(self, db, tablename):
        sql = "SELECT column_name FROM INFORMATION_SCHEMA.`KEY_COLUMN_USAGE` WHERE table_name='%s' AND constraint_name='PRIMARY';" % tablename
        conn = dbs(0, db)
        res = conn.getres(sql)[0][0]
        return res

    def get_all_column(self, db, tablename):
        sql = 'DESC %s' % tablename
        conn = dbs(0, db)
        conn.execsql(sql)
        res = conn.getres()
        column_list = []
        for key in res:
            column_list.append(key[1])
        return column_list
