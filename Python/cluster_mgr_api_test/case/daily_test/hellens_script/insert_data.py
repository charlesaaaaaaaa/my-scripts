#coding=utf-8
import logging
import pymysql
import time
import logging
import random
import argparse
from random import randint
import threading

#随机生成指定长度的整数
def createInt(m):
    range_start = 10**(m-1)
    range_end = (10**m)-1
    random_int = randint(range_start, range_end)
    return random_int

#随机生成日期
def createDate(k):
    a1=(1976,1,1,0,0,0,0,0,0)              #设置开始日期时间元组（1976-01-01 00：00：00）
    a2=(1990,12,31,23,59,59,0,0,0)    #设置结束日期时间元组（1990-12-31 23：59：59）
    start=time.mktime(a1)    #生成开始时间戳
    end=time.mktime(a2)      #生成结束时间戳
    t=random.randint(start,end)    #在开始和结束时间戳中随机取出一个
    date_touple=time.localtime(t)          #将时间戳生成时间元组
    random_date=time.strftime("%Y%m%d",date_touple)  #将时间元组转成格式化字符串（1976-05-21）
    return random_date

#随机生成指定长度的字符串
def createStr(n):
    random_str = ''
    base_str = 'ABCDEFGHIGKLMNOPQRSTUVWXYZabcdefghigklmnopqrstuvwxyz'
    length = len(base_str) - 1
    for i in range(n):
        random_str += base_str[random.randint(0, length)]
    return random_str

#随机生成指定长度的浮点数
def createFloat(Num1,Num2):
    N1 = 0
    N2 = 0
    for i in range(1,Num1-Num2-1):
        N1 = N1 * 10 + randint(0,9)
    for j in range(1,Num2):
        N2 = N2 * 10 + randint(0,9)
    random_num = str(N1) + "."+ str(N2)
    random_float = float(random_num)
    #print(random_float)
    return random_float


def run(hoststr, portstr, size):
    intport = int(portstr)
    conn = pymysql.connect(host=hoststr,port=intport,db='cdmsrc', user='clustmgr',passwd='clustmgr_pwd', charset='utf8')
    cur = conn.cursor()
    #批量插入方法
    s = time.time()
    #data_list = [(i,) for i in range(10)]
    #print(type(data_list))
    data_list = list()
    for i in range(0, size):
        apsdprocod_val = createStr(2)
        #print(apsdprocod_val)
        apsdactno_val = createStr(15)
        apsdtrdat_val = createDate(11)
        apsdjrnno_val = createFloat(10,0)
        apsdseqno_val = createFloat(6,0)
        apsdprdno_val = createStr(19)
        apsdfrnjrn_val = createStr(12)
        apsdtrtm_val = createStr(6)
        apsdvchno_val = createStr(8)
        apsdtrproccod_val = createStr(2)
        apsdtrbk_val = createStr(4)
        apsdtrcod_val = createFloat(6,0)
        apsdtramt_val = createFloat(18,2)
        apsdcshtfr_val = createStr(1)
        apsdrbind_val = createStr(1)
        apsdtraftbal_val = createFloat(18,2)
        apsderrdat_val = createStr(8)
        apsddbktyp_val = createFloat(10,0)
        apsddbkpro_val = createStr(2)
        apsdbatno_val = createStr(2)
        apsddbkno_val = createFloat(10,0)
        apsdaprocod_val = createStr(2)
        apsdaacno_val = createStr(15)
        apsdabs_val = createStr(15)
        apsdrem_val = createStr(45)
        apsdtrchl_val = createStr(4)
        apsdtrfrm_val = createStr(10)
        apsdtrpla_val = createStr(45)
        apsdecind_val = createStr(1)
        apsdprtind_val = createStr(1)
        apsdsup1_val = createStr(4)
        apsdsup2_val = createStr(4)
        id_val = createInt(9)
        #id_val = i
        #print(type(id_val))
        data_list.append((apsdprocod_val, apsdactno_val, apsdtrdat_val,apsdjrnno_val,apsdseqno_val,apsdprdno_val,apsdfrnjrn_val,apsdtrtm_val,apsdvchno_val,apsdtrproccod_val,apsdtrbk_val,apsdtrcod_val,apsdtramt_val,apsdcshtfr_val,apsdrbind_val,apsdtraftbal_val,apsderrdat_val,apsddbktyp_val,apsddbkpro_val,apsdbatno_val,apsddbkno_val,apsdaprocod_val,apsdaacno_val,apsdabs_val,apsdrem_val,apsdtrchl_val,apsdtrfrm_val,apsdtrpla_val,apsdecind_val,apsdprtind_val,apsdsup1_val,apsdsup2_val,id_val))
    sql = "insert into apsd(apsdprocod, apsdactno, apsdtrdat, apsdjrnno,apsdseqno,apsdprdno,apsdfrnjrn,apsdtrtm,apsdvchno,apsdtrproccod,apsdtrbk,apsdtrcod,apsdtramt,apsdcshtfr,apsdrbind,apsdtraftbal,apsderrdat,apsddbktyp,apsddbkpro,apsdbatno,apsddbkno,apsdaprocod,apsdaacno,apsdabs,apsdrem,apsdtrchl,apsdtrfrm,apsdtrpla,apsdecind,apsdprtind,apsdsup1,apsdsup2,id) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    total_count = cur.executemany(sql,data_list)
    conn.commit()
    cur .close()
    conn.close()
    e = time.time()
 
    #print(total_count)
    #print(e-s)
 
 
if __name__ == '__main__':
    db='cdmsrc'
    user='clustmgr'
    passwd='clustmgr_pwd'
    charset='utf8'
    parser = argparse.ArgumentParser(description="insert data for xty testing")
    parser.add_argument('--host', type=str, required=True, help='shard mysql master ip')
    parser.add_argument('--port', type=int, required=True, help='shard mysql master port')
    parser.add_argument('--clusterid', type=int, required=True, help='cluster id')
    parser.add_argument('--thread_num', type=int, required=True, help='connect mysql update thread num')
    #parser.add_argument('--timeout', type=int, required=True, help='run time out')
    parser.add_argument('--size', type=int, help="table_size, default = 1000", default='1000')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO,filename="./insert_data.log",filemode='a',format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s')
    run(args.host,args.port,args.size)       #0.13s
    threads = []
    for i in range(args.thread_num):
        th = threading.Thread(target=run,args=[args.host, args.port, args.size])
        th.start()
        #threads.append(th)
 
