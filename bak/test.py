import json
import string
import psycopg2
import subprocess
from time import sleep

f=open('install_nomgr.json',encoding='utf-8')
a=json.loads(f.read())

total_comp = a['cluster']['comp']['nodes']
c=0
ip=[]
port=[]
for i in total_comp:
    comp_ip=i['ip']
    comp_port=i['port']
    ip.append(comp_ip)
    port.append(comp_port)
    exec("port%s = i['port']" % c)
    c+=1

def check_connect(): #cheak all host and port connection, make sure connect success!
    for i in ip:
        for p in port:
            print('connect to %s:%s' % (i, p))
            conn = psycopg2.connect(database="postgres", user="abc", password="abc", host=i, port=p)
            print('connect successful!')
            cur = conn.cursor()
            conn.autocommit = True
            cur.close()
            conn.close()

def create_database():
    n=0
    for i in total_comp:
        na=n+1
        conn = psycopg2.connect(database="postgres", user="abc", password="abc", host=ip[n], port=port[n])
        print('create database t%i on %s:%s' % (na,ip[n],port[n]) )
        cur = conn.cursor()
        conn.autocommit = True
        dbname="t%i" % (na)
        CreateDb=""" 
            CREATE DATABASE {};
            """ .format(dbname)
        cur.execute(CreateDb)
        print('success!')
        cur.close()
        conn.close()
        sleep(3)
        n=n+1


def prepare_data(): #prepareing tpcc data
    n=0
    for i in total_comp:
        na=n+1
        subprocess.run("/home/charles/File/python/sysbench-tpcc-cus/prepare.sh %s %s t%i " % (ip[n], port[n],na), shell=True)
        print('prepare data on %s:%s/t%i success!'% (ip[n], port[n],na) )
        n=n+1


print('\n=== check connection ===\n')
check_connect()
print('\n=== create database ===\n')
create_database()
#print('\n=== prepare data ===\n')
#prepare_data()
