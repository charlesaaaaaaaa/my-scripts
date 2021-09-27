#!/usr/bin/python
# -*- coding: utf-8 -*-

import psycopg2
import random

con = psycopg2.connect(database="t1", user="abc", password="abc", host="192.168.0.113", port="8882")
kunlun=con.cursor()

#create table t1(id int primary key, name text not null, age int) no-partition

#create table t1_pt(id int primary key, name text not null, age int) partition by range(id);
#create table t1_pt1 partition of t1_pt for values from (1) to (501);
#create table t1_pt2 partition of t1_pt for values from (501) to (1001);

#kunlun.execute("delete from t1_pt")

for i in range(1,1001):
    agee = random.randint(18,113)
    first_name = ['uyue','ddst','ghi ','iyfp','ggvt','lqyg','nngo','nngo','ovty','ggll','ovty']
    last_name = ['dddd','sksk','vgvb','ktwu','goi ','rkhy','inqg','bjiq','iiic','itiy','wwip']
    last_name_r = random.choice(last_name)
    first_name_r = random.choice(first_name)
    names = first_name_r +' '+ last_name_r
    
    if i % 100 == 0:
        a=i/10
        print '%d%%'% a
    
    kunlun.execute("insert into t1_pt(id, name, age) values({id},'{name}',{age})".format(id = int(i), name = names, age=agee))      #insert data
    kunlun.execute("select count(*) from t1_pt")    

rows = kunlun.fetchall()    #get the total num of data
print("\nnum of data")      #print on screen
print(rows)

con.commit()
kunlun.close()
con.close()
