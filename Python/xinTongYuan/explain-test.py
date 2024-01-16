import random
import pymysql
import argparse
import psycopg2
from time import sleep

def connect_pg(host, port, user, pwd, db):
    global cur, conn
    conn = psycopg2.connect(host=host, port=port, user=user, password=pwd, database=db)
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

def connect_mysql(host, port, db, sql):
    global result
    conn = pymysql.connect(host=host, port=port, user='pgx', passwd='pgx_pwd', database=db)
    cur = conn.cursor()
    cur.execute(sql)
    result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

def test():
    print("1）  准备一张分片表，并插入部分数据；")
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute("drop database if exists explaindb")
    cur.execute("create database explaindb")
    close_pg('n')
    connect_pg(Host, Port, User, Pwd, 'explaindb')
    sql="create table test(a int, b text) partition by hash(a)"
    cur.execute(sql)
    print(sql)
    for i in range(6):
        sql = "create table test_%s partition of test for values with (MODULUS 6, REMAINDER %s)" % (i, i)
        cur.execute(sql)
        print(sql)
    close_pg('n')
    print('loading data')
    connect_pg(Host, Port, User, Pwd, 'explaindb')
    for i in range(1, 1001):
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        ranInt = random.randint(99, 1000)
        sql = "insert into test values(%s, '%s%s')" % (i, ranStr, ranInt)
        cur.execute(sql)
    close_pg('n')
    print("\n2）        查询一条跨库语句的执行计划；")
    ranNum = random.randint(1, 1001)
    connsql = 'create extension if not exists dblink;'
    connsql1 = "select dblink_connect('conn1', concat('hostaddr=%s port=%s dbname=%s user=%s password=%s', inet_server_port()));" % (Host, Port,'explaindb', User, Pwd)
    selectsql = "select * from dblink('conn1', 'explain select * from test where a = %s') as t1(a text);" % (ranNum)
    sql = "%s %s %s" % (connsql, connsql1, selectsql)
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute(connsql)
    print(connsql)
    print(connsql1)
    cur.execute(connsql1)
    print(selectsql)
    cur.execute(selectsql)
    ress = close_pg('all')
    for i in ress:
        for ii in i:
            if '_$$_' in ii:
                res = ii
                break
    print(res)
    shardNum = res.split(':')[1][1]
    tableName = res.split('.')[3][1:7]
    print("================\n该条sql影响到 shard_%s, 表名为：%s\n================\n" % (shardNum, tableName))

    print("3）  执行这条跨库语句。")
    selectsql = "select * from dblink('conn1', 'select * from test where a = %s') as t1(a int, b text);" % (ranNum)
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute(connsql)
    cur.execute(connsql1)
    print(selectsql)
    cur.execute(selectsql)
    pgres = close_pg('one')
    print(pgres)

    #找到元数据主
    hostaddr = "select hostaddr from pg_cluster_meta_nodes where is_master = 't'"
    port = "select port from pg_cluster_meta_nodes where is_master = 't'"
    clusterid = "select cluster_id from pg_cluster_meta_nodes where is_master = 't'"
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute(hostaddr)
    metahostaddr = close_pg('one')[0]
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute(port)
    metaport = close_pg('one')[0]
    connect_pg(Host, Port, User, Pwd, 'postgres')
    cur.execute(clusterid)
    clusterid = close_pg('one')[0]
    #去元数据上找对应shard的主存储节点
    dbhostaddr = "select hostaddr from shard_nodes where db_cluster_id = %s and shard_id = %s and member_state = 'source';" % (clusterid, shardNum)
    dbport = "select port from shard_nodes where db_cluster_id = %s and shard_id = %s and member_state = 'source';" % (clusterid, shardNum)
    storage_host = connect_mysql(metahostaddr, metaport, 'kunlun_metadata_db', dbhostaddr)[0][0]
    sharage_port = connect_mysql(metahostaddr, metaport, 'kunlun_metadata_db', dbport)[0][0]
    print("\n现在去 shard_%s 主节点 %s:%s 的 %s表 检查数据是否存在" % (shardNum, storage_host, sharage_port, tableName))
    
    #查找对应数据
    sql = "select * from %s where a = %s" % (tableName, ranNum)
    print(sql)
    myres = connect_mysql(storage_host, sharage_port, 'explaindb_$$_public', sql)[0]
    print(myres)
    if pgres == myres:
        print('\n== 数据相同，验证通过')
    else:
        print('\n== 数据不相同，验证失败')
        exit(1)
    
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

