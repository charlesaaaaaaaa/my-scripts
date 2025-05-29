import time
import psycopg2
import pymysql


class Pg():
    def __init__(self, host, port, user, pwd, db):
        global err
        err = ''
        try:
            self.conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
        except Exception as error:
            # 当连接失败的时候会去检测这个错误是否为要等待的错误，如果是的话则不断等10s，直到这些错误消失
            err = str(error)
            print(err)
            wait_error_list = ['retry in a few seconds', 'the database system is starting up', 'in recovery mode', 'try restarting transaction']
            for err_msg in wait_error_list:
                while err_msg in err:
                    err = ''
                    time.sleep(10)
                    try:
                        self.conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, dbname=db)
                    except Exception as error:
                        err = str(error)
                        print(err)
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


