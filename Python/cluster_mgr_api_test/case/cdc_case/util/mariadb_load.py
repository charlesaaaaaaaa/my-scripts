#import psycopg2
import pymysql
import argparse
import random
import multiprocessing

class OPT:
    def __init__(self):
        pass

    def randdate(self):
        year = random.randint(1971, 2023)
        month = random.randint(1, 12)
        bigMonth = (1, 3, 5, 7, 8, 10, 12)
        smallMonth = (4, 6, 9, 11)
        if year % 4 == 0 and year % 400 != 0:
            if month == 2:
                day = random.randint(1, 29)
            elif month in bigMonth:
                day = random.randint(1, 31)
            elif month in smallMonth:
                day = random.randint(1, 30)
        else:
            if month == 2:
                day = random.randint(1, 28)
            elif month in bigMonth:
                day = random.randint(1, 31)
            elif month in smallMonth:
                day = random.randint(1, 30)
        if month < 10:
            month = '0' + str(month)
        if day < 10:
            day = '0' + str(day)
        randate = '%s-%s-%s' % (year, month, day)
        return randate

    def randstr(self, per):
        res = ''
        for i in range(per):
            a = random.choice('abcdefghijklmnopqrstuvwxyzQWERTYUIOPASDFGHJKLZXCVBNM1234567890')
            res = res + a
        return res

    def randtime(self):
        hours = random.randint(0, 23)
        if hours < 10:
            hours = '0' + str(hours)
        mins = random.randint(0, 59)
        if mins < 10:
            mins = '0' + str(mins)
        seconds = random.randint(0, 59)
        if seconds < 10:
            seconds = '0' + str(seconds)
        ns = random.randint(0, 999)
        times = '%s:%s:%s.%s' % (hours, mins, seconds, ns)
        #times = '%s:%s:%s' % (hours, mins, seconds)
        return times

    def randtimez(self):
        timez = ["NZDT", "NZST", "NZT", "AESST", "CST", "CADT", "SADT", "EST", "LIGT", "CAST", "WDT", "JST", "KST",
                 "CCT",
                 "EETDST", "CETDST", "EET", "IST", "MEST", "METDST", "BST", "CET", "MET", "WETDST", "GMT", "WET", "WAT",
                 "NDT", "ADT", "NFT", "NST", "AST", "EDT", "CDT", "EST", "CST", "MDT", "MST", "PDT", "PST"]
        times = self.randtime()
        randTimez = random.choice(timez)
        timez = '%s %s' % (times, randTimez)
        return timez

    def randtimestamp(self):
        dates = self.randdate()
        times = self.randtime()
        randts = dates + ' ' + times
        return randts

    def randtimestampz(self):
        dates = self.randdate()
        zones = self.randtimez()
        timestampz = dates + ' ' + zones
        return timestampz

    def randMac(self):
        res = ":".join(["%02x" % x for x in map(lambda x: random.randint(0, 255), range(6))])
        return res

    def randnet(self):
        resList = []
        for i in range(4):
            parts = str(random.randint(0, 255))
            resList.append(parts)
        res = '.'.join(resList)
        return res

    def randbit(self, per):
        res = ''
        for i in range(per):
            tmp = random.randint(0, 1)
            res = res + str(tmp)
        return res


def random_num(dataType):
    res = ''
    if dataType == 'integer' or dataType == 'int':
        res = random.randint(-2147483648, 2147483647)
    elif dataType == 'smallint' or dataType == "MEDIUM INT":
        res = random.randint(-32768, 32767)
    elif dataType == 'bigint':
        res = random.randint(-9223372036854775808, 9223372036854775807)
    elif 'numeric' in dataType:
        res = '%.2f' % random.uniform(0, 10 ** 5)
    elif 'float' in dataType:
        res = '%.2f' % random.uniform(0, 10 ** 5)
    elif dataType == 'real':
        res = '%.2f' % random.uniform(0, 10 ** 5 - 1)
    elif dataType == 'double precision':
        res = '%.2f' % random.uniform(0, 10 ** 16 - 1)
    elif dataType == 'money':
        res = '%.2f' % random.uniform(-92233720368547758.08, +92233720368547758.07)
    elif "char" in dataType:
        res = OPT().randstr(32)
        res = "'%s'" % res
    elif 'text' in dataType or 'TEXT' in dataType:
        res = OPT().randstr(100)
        res = "'%s'" % res
    elif dataType == 'date':
        res = OPT().randdate()
        res = "'%s'" % res
    elif dataType == 'time' or dataType == "time without time zone":
        res = OPT().randtime()
        res = "'%s'" % res
    elif dataType == "time with time zone":
        res = OPT().randtimez()
        res = "'%s'" % res
    elif dataType == "timestamp" or dataType == "timestamp without time zone":
        res = OPT().randtimestamp()
        res = "'%s'" % res
    elif dataType == "timestamp with time zone":
        res = OPT().randtimestampz()
        res = "'%s'" % res
    elif dataType == "macaddr" or dataType == "macaddr8":
        res = OPT().randMac()
        res = "'%s'" % res
    elif dataType == "cidr" or dataType == "inet":
        res = OPT().randnet()
        res = "'%s'" % res
    elif dataType == "boolean":
        res = random.choices(('TRUE', 'FALSE'))[0]
    elif dataType == "bytea":
        res = str(OPT().randstr(16))
        res = "'%s'" % res
    elif dataType == "bit":
        res = OPT().randbit(16)
        res = "'%s'" % res
    elif 'BLOB' in dataType or 'blob' in dataType:
        res = OPT().randbit(100)
        res = "'%s'" % res
    return res


def insert_process(column_list, host, port, user, pwd, dbname, start_num, end_num):
    first, columns = 0, ''
    for i in column_list:
        if 'serial' not in i[1]:
            if first == 0:
                columns += i[0]
                first = 1
            else:
                columns += ', %s' % i[0]


    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=dbname, autocommit=True)
    cur = conn.cursor()
    range_times = end_num - start_num + 1
    for i in range(range_times):
        sql = 'insert into %s(%s) value(' % (tbname, columns)
        first = 1
        id = start_num + i
        for column in column_list:
            if 'serial' not in column_list:
                if first == 1:
                    tmp_vlaue = str(id)
                    first = 0
                else:
                    tmp = str(random_num(column[1]))
                    tmp_vlaue = ', %s' % tmp
                sql += tmp_vlaue
        sql += ');'
        cur.execute(sql)
    cur.close()
    conn.close()

def load(threads, host, port, user, pwd, dbname, table_size):
    # "timestamp",
    column_types = ["int", "integer", "smallint", "bigint", "numeric(10,2)", "real", "double precision",
                    "character varying(32)", "varchar(32)", "character(32)", "char(32)", "float(8,2)",
                    "text", "boolean", "date", "time", "text", "TINYBLOB", "BLOB", "MEDIUMBLOB", "LONGBLOB", "TINYTEXT",
                    "MEDIUMTEXT", "LONGTEXT"]
    #column_types = ["int", "text"]
    column_list, num = [], 1
    for i in column_types:
        if i == column_types[0]:
            tmp = ('id', i)
        else:
            num += 1
            tmp = ('c%s' % num, i)
        column_list.append(tmp)
    create_var = ''
    for i in column_list:
        if i == column_list[0]:
            tmp = '%s %s primary key' % (i[0], i[1])
        else:
            tmp = ', %s %s' % (i[0], i[1])
        create_var += tmp

    drop_sql = "drop table if exists %s;" % tbname
    create_sql = 'create table if not exists %s(%s);' % (tbname, create_var)
    conn = pymysql.connect(host=host, port=port, user=user, password=pwd, database=dbname, autocommit=True)
    cur = conn.cursor()
    if create_table == 'Y' or create_table == 'y':
        cur.execute(drop_sql)
    cur.execute(create_sql)
    try:
        show_id_sql = 'select max(id) from %s;' % tbname
        cur.execute(show_id_sql)
        the_latest_id = cur.fetchone()[0]
        if not the_latest_id:
            the_latest_id = 0
    except Exception as err:
        the_latest_id = 0
        print(err)
    conn.commit()
    cur.close()
    conn.close()
    lis = []
    print('起始id为%s' % the_latest_id)
    for i in range(threads):
        each_table_size = table_size // threads
        start_num = i * each_table_size + 1 + the_latest_id
        end_num = (i + 1) * each_table_size + the_latest_id
        p = multiprocessing.Process(target=insert_process, args=(column_list, host, port, user, pwd, dbname, start_num, end_num))
        p.start()
        lis.append(p)
    for i in lis:
        i.join()

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='')
    ps.add_argument('--type', default='mysql', type=str, help='[mysql]|[pgsql]')
    ps.add_argument('--host', type=str, default='127.0.0.1')
    ps.add_argument('--port', type=str, default='13306')
    ps.add_argument('--user', type=str, default='root')
    ps.add_argument('--pwd', type=str, default='root')
    ps.add_argument('--dbname', type=str, default='mysql')
    ps.add_argument('--threads', type=int, default=1)
    ps.add_argument('--table_size', type=int, default=10000)
    ps.add_argument('--tbname', type=str, default='test1')
    ps.add_argument('--create_table', type=str, default='n', help='[n]|[y]')
    args = ps.parse_args()
    types = args.type
    host = args.host
    port = int(args.port)
    user = args.user
    pwd = args.pwd
    dbname = args.dbname
    threads = args.threads
    table_size = args.table_size
    tbname = args.tbname
    create_table = args.create_table
    load(threads=threads, table_size=table_size, host=host, port=port, user=user, pwd=pwd, dbname=dbname)
