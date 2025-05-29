# -*- coding: utf-8 -*-
import psycopg2
#from mysql import connector
import pymysql
from time import sleep 
import random
import argparse
#import yaml
#import subprocess

def connect_pg(host, port, user, pwd, db , autocom):
    global conn, cur
    conn = psycopg2.connect(database = db, user = user, host = host, port = port, password = pwd, application_name = 'shards_test')
    if autocom == 'y':
        conn.autocommit = True
    cur = conn.cursor()

def close_pg(fet):
    global key
    if fet == 'one':
        key = cur.fetchone()
    elif fet == 'all':
        key = cur.fetchall()
    else :
        pass
    conn.commit()
    cur.close()
    conn.close()
    return key

def t2str(value):
    values = str(value)
    values = values.replace('[', '')
    values = values.replace(']', '')
    values = values.replace(',', '')
    values = values.replace('(', '')
    values = values.replace(')', '')
    values = values.replace(' ', '')
    values = values.replace('\'', '')
    return values

def write_yaml(key, values, names):
    wy = open(names, 'a')
    if values == 'NULL':
        wy.write("%s:", key)
    else :
        wy.wirte("  %s: %s", key, values)
    wy.close()

def connect_my(sHost, iPort, sql):
    conn = pymysql.connect(host=sHost, port=iPort , database='shard_$$_public', user='pgx', password='pgx_pwd')
    cur = conn.cursor()
    cur.execute(sql)
    tmpVar = cur.fetchall()
    cur.close()
    conn.close()
    return tmpVar

def test():
    connect_pg(Host, Port, User, Pwd, 'postgres' , 'y')
    cur.execute("select distinct(shard_id) from pg_shard_node order by shard_id");
    shardid = close_pg('all')
    shardid = len(shardid)
    num = 0
    host_list, port_list, sid_list = [], [], []
    
    print("\n1）	新建一张分片表，并插入一定量数据，设法展示或证明数据都分布到各个分片上")
    for i in range(shardid): #现在就是在查找对应的shard主节点，把对应的信息放到数组里面好后面拿取
        connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
        connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
        Hos = 'select hostaddr from pg_shard_node where shard_id = (select distinct(shard_id) from pg_shard_node order by shard_id limit '+ str(num) + ',1) limit 1'
        Por = 'select port from pg_shard_node where shard_id = (select distinct(shard_id) from pg_shard_node order by shard_id limit %s,1) limit 1' % (str(num))
        Sid = 'select shard_id from pg_shard_node where shard_id = (select distinct(shard_id) from pg_shard_node order by shard_id limit %s,1) limit 1' % (str(num))
        cur.execute(Hos)
        Ho = close_pg('one')
        connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
        cur.execute(Por)
        Po = close_pg('one')
        connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
        cur.execute(Sid)
        Si = close_pg('one')
        if Si == None:
            print('shard_id == None')
        else :
            host_list.append(Ho)
            port_list.append(Po)
            sid_list.append(Si)
        print("shard_%s node info: %s, %s" % (sid_list[num], host_list[num], port_list[num]))
        num = num + 1
    print(sid_list)
    
    print("创建klustron分区表及增加数据")
    connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
    cur.execute("drop database if exists shard")
    cur.execute("create database shard")
    close_pg('pass')
    connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
    cur.execute('select count(distinct(shard_id)) from pg_shard_node')
    shardNum = close_pg('one')
    shardNum = t2str(shardNum)
    shardNum = shardNum.replace('L','')
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    sql1 = "create table item(id int, name text, grp int) partition by range(grp)" #创建分区表，以id为分片字段
    print("use shard; \n%s" % (sql1))
    cur.execute(sql1)
    for i in range(0, int(shardNum)):
        shard = t2str(sid_list[i])
        shard = int(shard)
        timNum = 5 * i
        part = "CREATE TABLE item_%s PARTITION OF item FOR VALUES FROM (%d) TO (%d) with (shard = %s);" % (str(i), 1+timNum, 6+timNum, shard) ##创建分区表
        cur.execute(part)
        print('kunlun:%s' % (part))
    close_pg('pass')

    print('load 1000 row data ...')
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    tmp_range = int(shardNum) * 5 + 1
    for grp in range(1, tmp_range):
        for Id in range(1, 101):
            Ids = Id + (grp -1) * 100
            txt = 'testdata%d' % (Ids)
            cur.execute("insert into item values(%d, '%s', %d)" % (Ids, txt, grp))
    close_pg('pass')
    
    print("创建pg分区表及增加数据")
    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'postgres', 'y')
    cur.execute("drop database if exists shard")
    cur.execute("create database shard")
    close_pg('pass')
    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'shard', 'y')
    sql1 = "create table item(id int, name text, grp int) partition by range(grp)"
    print(sql1)
    cur.execute(sql1)
    for i in range(0, int(shardNum)):
        timNum = 5 * i
        part = "CREATE TABLE item_%s PARTITION OF item FOR VALUES FROM (%d) TO (%d);" % (str(i), 1+timNum, 6+timNum)
        cur.execute(part)
    close_pg('pass')

    print('load 1000 row data ...')
    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'shard', 'y')
    tmp_range = int(shardNum) * 5 + 1
    for grp in range(1, tmp_range):
        for Id in range(1, 101):
            Ids = Id + (grp -1) * 100
            txt = 'testdata%d' % (Ids)
            a = "insert into item values(%d, '%s', %d)" % (Ids, txt, grp)
            cur.execute(a)
    close_pg('pass')

    print("\n检查klustron数据是否正确分布,数据是否无误")
    shardTotalDataRow = 0
    shardTip = ""
    num = 0
    for i in range(shardid):
        tmpHost = t2str(host_list[num])
        tmpPort = int(t2str(port_list[num]))
        shardDataRow = connect_my(tmpHost, tmpPort, 'select count(*) from item_%s' % (str(num)))
        shardDataRow = t2str(shardDataRow)
        shardTotalDataRow = shardTotalDataRow + int(shardDataRow);
        if num == 0:
            shardTip = "shard_%s" % (str(num+1))
            print("%s: %s: shard_%s: item_%s = %s" % (tmpHost, tmpPort, t2str(sid_list[num]), str(num), str(shardDataRow)))
            num = num + 1
        else :
            shardTip = "%s + shard_%s" % (shardTip, str(num+1))
            print("%s: %s: shard_%s: item_%s = %s" % (tmpHost, tmpPort, t2str(sid_list[num]), str(num), str(shardDataRow)))
            num = num + 1
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    cur.execute("select count(*) from item")
    pgTotal = close_pg('one')
    pgTotal = t2str(pgTotal)
    print("KunlunServer: select count(*) from item: %s" % pgTotal)
    print("KunlunStorage:%s = %s"% (shardTip, shardTotalDataRow))

    print("(分片字段grp：每100个数据分一组。如grp=1，id列从1到100，grp=2，id列101到200)\n2）	采用where条件对分片字段过滤，查询单条数据；")
    num = 0
    ranInt = random.randint(1, tmp_range - 1)
    ran100 = random.randint(1, 100)
    ran1000 = random.randint(1, (tmp_range - 1) * 100)
    sql = "select * from item where grp = %d limit 1 offset %d" % (ranInt, ran100)
    print('%s:%s : %s:' % (Host, Port, sql))
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    cur.execute(sql)
    shardDataRow2 = close_pg('one')
    print("klustron: \n%s"% (str(shardDataRow2)))

    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'shard', 'y')
    cur.execute(sql)
    pgShardDataRow2 = close_pg('one')
    print("pg: \n%s" % (str(pgShardDataRow2)))

    print("\n3）	对分片字段范围查询，且排序;")
    ranInt = random.randint(1, 10)
    sql = "select * from item where id BETWEEN %d and %d order by id" % (ran1000 - 3, ran1000)
    print("%s: %s : %s "% (tmpHost, tmpPort, sql))
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    cur.execute(sql)
    shardDataRow3 = close_pg('all')
    print('klustron: \n%s' % (str(shardDataRow3)))

    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'shard', 'y')
    cur.execute(sql)
    pgShardDataRow3 = close_pg('all')
    print('pg: \n%s' % (str(pgShardDataRow3)))

    print("\n4）	对分片字段进行分组查询，并统计各个分组相同值的个数;")
    sql = "select grp, count(grp) from item group by grp order by grp"
    print("%s: %s : %s "% (tmpHost, tmpPort, sql))
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    cur.execute(sql)
    shardDataRow1 = close_pg('all')
    print('klustron: \n%s' % (str(shardDataRow1)))

    connect_pg(srcHost, srcPort, srcUser, srcPwd, 'shard', 'y')
    cur.execute(sql)
    pgShardDataRow1 = close_pg('all')
    print('pg: \n%s' % (str(pgShardDataRow1)))
    
if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='Kunlun sharding test')
    ps.add_argument('--host', type=str, help='the host of KunlunBase, something like "192.168.100.100"')
    ps.add_argument('--port', type=int, default=47001, help='the port of KunlunBase, default value = 47001')
    ps.add_argument('--user', type=str, default='abc', help='the user of KunlunBase, default value = "abc"')
    ps.add_argument('--password', type=str, default='abc', help = 'the password of Kunlunbase, default values = "abc"')
    ps.add_argument('--srchost', type=str, help='源pg，进行对比的pg host')
    ps.add_argument('--srcport', type=int, default=47001, help='源pg，进行对比的pg port')
    ps.add_argument('--srcuser', type=str, default='abc', help='源pg，进行对比的pg user')
    ps.add_argument('--srcpassword', type=str, default='abc', help = '源pg，进行对比的pg password')
    args = ps.parse_args();
    print(args);
    Host = args.host
    Port = args.port
    User = args.user;
    Pwd = args.password;
    srcHost = args.srchost
    srcPort = args.srcport
    srcUser = args.srcuser
    srcPwd = args.srcpassword
    test()
