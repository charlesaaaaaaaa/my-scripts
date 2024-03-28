import psycopg2
import pymysql

class Pg():
    def __init__(self, host, port, user, pwd, db):
        self.conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
        self.conn.autocommit = True
        self.cur = self.conn.cursor()

    def ddl_sql(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        conn.commit()

    def sql_with_result(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return res

    def close(self):
        conn = self.conn
        cur = self.cur
        #conn.commit()
        cur.close()
        conn.close()

class My():
    def __init__(self, host, port, user, pwd, db):
        self.conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=db)
        self.cur = self.conn.cursor()

    def ddl_sql(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        conn.commit()

    def sql_with_result(self, sql):
        conn = self.conn
        cur = self.cur
        cur.execute(sql)
        res = cur.fetchall()
        conn.commit()
        cur.close()
        conn.close()
        return res

    def close(self):
        conn = self.conn
        cur = self.cur
        #conn.commit()
        cur.close()
        conn.close()


