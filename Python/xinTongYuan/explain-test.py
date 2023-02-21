import psycopg2
import pymysql
import random
import argparse
from time import sleep

def connect_pg(host, port, user, pwd):
    global cur, conn
    conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, database='postgres')
    autocommit = True
    cur = conn.cursor()

def close_pg(fet):
    global result
    result = ""
    if fet == 'one':
        result = cur.fetchone()
    elif fet == 'all':
        result = cur.fetchall()
    else :
        pass
    conn.commit()
    cur.close()
    conn.close()
    return result

def connect_mysql(host, port, sql):
    global result
    conn = pymysql.connect(host=host, port=port, user='pgx', passwd='pgx_pwd', database='postgres_$$_explains')
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

def t2str(value):
    global values
    values = str(value)
    values = values.replace('[', '')
    values = values.replace(']', '')
    values = values.replace(',', '')
    values = values.replace('(', '')
    values = values.replace(')', '')
    values = values.replace(' ', '')
    values = values.replace('\'', '')
    return values


def test():
    print("1）	准备一张分片表，并插入部分数据；")
    connect_pg(Host, Port, User, Pwd)
    cur.execute("drop schema  if exists explains CASCADE")
    cur.execute("create schema explains")
    print("create schema explains")
    close_pg('passtable item (id int, name text')
    connect_pg(Host, Port, User, Pwd)
    cur.execute("create table explains.item (id int, name text)")
    print("create table explains.item (id int, name text")
    close_pg('pass')
    print("loading 1000 row data...")
    connect_pg(Host, Port, User, Pwd)
    for i in range(1,1001):
        ranNum = random.randint(15,20)
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        cur.execute("insert into explains.item values(%s, '%s')" % (str(i), ranStr))
    close_pg('pass')
    
    print("\n2）	查询一条跨库语句的执行计划；")
    connect_pg(Host, Port, User, Pwd)
    ranNum = random.randint(1,1001)
    sql = "explain select * from explains.item where id = %s" % (str(ranNum))
    print(sql)
    cur.execute(sql)
    result = close_pg("all")
    print(result)
    seconds = str(result[1:8])
    shardNum = seconds.split(':')[1].split('\\')[0]
    shardNum = t2str(shardNum)
    print("================\n该条sql影响到 shard_%s\n================\n" % (shardNum))

    print("3）	执行这条跨库语句。")
    connect_pg(Host, Port, User, Pwd)
    sql = "select * from explains.item where id = %s" % (str(ranNum))
    print(sql)
    cur.execute(sql)
    result = close_pg("all")
    print(result)

    print("\n现在去shard_%s验证" % (shardNum))
    shardHostSql = 'select hostaddr from pg_shard_node where shard_id = %s' % (shardNum)
    shardPortSql = 'select port from pg_shard_node where shard_id = %s' % (shardNum)
    sqlMy = 'select * from item where id = %s' % (str(ranNum))
    connect_pg(Host, Port, User, Pwd)
    cur.execute(shardHostSql)
    shard_host = cur.fetchone()
    cur.execute(shardPortSql)
    shard_port = cur.fetchone()
    close_pg('pass')
    shard_host = t2str(shard_host)
    shard_port = t2str(shard_port)
    print("%s:%s '%s'" % (shard_host, shard_port, sqlMy))
    resultMy = connect_mysql(shard_host, int(shard_port), sqlMy)
    print(resultMy)
    result = t2str(result)
    resultMy = t2str(resultMy)

    if result == resultMy:
        print("数据相同，验证通过")
    else :
        print("数据不相同，验证失败")

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description="Kunlun explain test")
    ps.add_argument("--host", type=str, help='The host of KunlunBase cluster')
    ps.add_argument("--port", type=int, default=47001, help='the port of KunlunBase cluster, default values: 47001')
    ps.add_argument("--user", type=str, default='abc', help='the user of KunlunBase cluster, default values: "abc"')
    ps.add_argument("--pwd", type=str, default='abc', help='the password of Kunlunbase cluster, default values: "abc"')
    args = ps.parse_args()
    print(args)
    Host = args.host
    Port = args.port
    User = args.user
    Pwd = args.pwd
    test()

