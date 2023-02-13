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
    for i in values:
        try:
            int(i)
        except:
            pass
        finally:
            pass
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
    shardid = t2str(shardid)
    num = 0
    host_list, port_list, sid_list = [], [], []
    
    print("\n1）	新建一张分片表，并插入一定量数据，设法展示或证明数据都分布到各个分片上")
    for i in str(shardid):
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
        host_list.append(Ho)
        port_list.append(Po)
        sid_list.append(Si)
        print("shard_%s node info: %s, %s" % (sid_list[num], host_list[num], port_list[num]))
        num = num + 1

    connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
    cur.execute("drop database if exists shard")
    cur.execute("create database shard")
    close_pg('pass')
    connect_pg(Host, Port, User, Pwd, 'postgres', 'y')
    cur.execute('select count(shard_id) from pg_shard_node')
    shardNum = close_pg('one')
    shardNum = t2str(shardNum)
    shardNum = shardNum.replace('L','')

    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    sql1 = "create table item(id int, name text) partition by Hash(id)"
    print("use shard; \n",sql1)
    cur.execute(sql1)
    for i in range(0, int(shardNum)):
        shard = t2str(sid_list[i])
        shard = int(shard)
        part = "CREATE TABLE item_%s PARTITION OF item FOR VALUES WITH (MODULUS %s, REMAINDER %s) with (shard = %s);" % (str(i), shardNum, str(i), shard)
        cur.execute(part)
        print(part)
    close_pg('pass')

    print('load 1000 row data ...')
    connect_pg(Host, Port, User, Pwd, 'shard', 'y')
    for i in range(1,1001):
        ranNum = random.randint(15,20)
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        cur.execute("insert into item values(%s, '%s')" % (str(i), ranStr))
    close_pg('pass')

    print("\n检查数据是否正确分布,数据是否无误")
    shardTotalDataRow = 0
    shardTip = ""
    num = 0
    sleep(5)
    for i in shardid:
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

    print("\n2）	采用where条件对分片字段过滤，查询单条数据；")
    num = 0
    for i in shardid:
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        tmpHost = t2str(host_list[num])
        tmpPort = int(t2str(port_list[num]))
        sql = "select * from item_%s where name = '%s' limit 1" % (str(num), str(ranStr))
        print("%s: %s : %s "% (tmpHost, tmpPort, sql))
        shardDataRow = connect_my(tmpHost, tmpPort, sql)
        print("result: %s"% (shardDataRow))
        num = num + 1

    print("\n3）	对分片字段范围查询，且排序；")
    num = 0
    for i in shardid:
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        tmpHost = t2str(host_list[num])
        tmpPort = int(t2str(port_list[num]))
        sql = "select * from item_%s where name = '%s' order by id" % (str(num), str(ranStr))
        print("%s: %s : %s "% (tmpHost, tmpPort, sql))
        shardDataRow = connect_my(tmpHost, tmpPort, sql)
        print(shardDataRow)
        num = num + 1

    print("\n4）	对分片字段进行分组查询，并统计各个分组相同值的个数；")
    num = 0
    for i in shardid:
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        tmpHost = t2str(host_list[num])
        tmpPort = int(t2str(port_list[num]))
        sql = "select name, count(name) from item_%s group by name order by name" % (str(num))
        print("%s: %s : %s "% (tmpHost, tmpPort, sql))
        shardDataRow = connect_my(tmpHost, tmpPort, sql)
        print(shardDataRow)
        num = num + 1

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='Kunlun sharding test')
    ps.add_argument('--host', type=str, help='the host of KunlunBase, something like "192.168.100.100"')
    ps.add_argument('--port', type=int, default=47001, help='the port of KunlunBase, default value = 47001')
    ps.add_argument('--user', type=str, default='abc', help='the user of KunlunBase, default value = "abc"')
    ps.add_argument('--password', type=str, default='abc', help = 'the password of Kunlunbase, default values = "abc"')
    args = ps.parse_args();
    print(args);
    Host = args.host
    Port = args.port
    User = args.user;
    Pwd = args.password;
    test()
