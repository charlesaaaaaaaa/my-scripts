# -*- coding: utf-8 -*-
import psycopg2
import pymysql
from time import sleep
import random
import argparse

def connect_pg(host, port, user, pwd, db , autocom):
    global conn, cur
    conn = psycopg2.connect(database = db, user = user, host = host, port = port, password = pwd, application_name = 'shards_test')
    if autocom == 'y':
        conn.autocommit = True
    cur = conn.cursor()

def close_pg(fet):
    if fet == 'one':
        key = cur.fetchone()
    elif fet == 'all':
        key = cur.fetchall()
    else :
        pass
    conn.commit()
    cur.close()
    conn.close()

def test():
    print('load 1000 row data ...')
    connect_pg(Host, Port, User, Pwd, Db, 'y')
    for grp in range(1,11):
        for Id in range(1, 101):
            Ids = Id + (grp -1) * 100
            txt = 'testdata%d' % (Ids)
            cur.execute("insert into item values(%d, '%s', %d)" % (Ids, txt, grp))
    close_pg('pass')

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='Kunlun sharding test')
    ps.add_argument('--host', type=str, help='the host of KunlunBase, something like "192.168.100.100"')
    ps.add_argument('--port', type=int, default=47001, help='the port of KunlunBase, default value = 47001')
    ps.add_argument('--user', type=str, default='abc', help='the user of KunlunBase, default value = "abc"')
    ps.add_argument('--password', type=str, default='abc', help = 'the password of Kunlunbase, default values = "abc"')
    ps.add_argument('--db', type=str, default='shard')
    args = ps.parse_args();
    print(args);
    Host = args.host
    Db = args.db
    Port = args.port
    User = args.user;
    Pwd = args.password;
    test()

