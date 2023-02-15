import psycopg2
import random
import argparse

def connect_pg1(host, port, user, pwd):
    global conn1, cur1
    conn1 = psycopg2.connect(host=host, port=port, user=user, password=pwd, database='postgres')
    autocommit = False
    cur1 = conn1.cursor()

def exePg1(opt, sql):
    if opt == 'y':
        print(sql)
    cur1.execute(sql)

def close_pg1(fet, opt):
    global result1
    result1 = ""
    if fet == "one":
        result1 = cur1.fetchone()
    elif fet == 'all':
        result1 = cur1.fetchall()
    else:
        pass
    if opt == 'commit':
        conn1.commit()
    elif opt == 'rollback':
        conn1.rollbak()
    cur1.close()
    conn1.close()
    return(result1)

def connect_pg2(host, port, user, pwd, sql):
    global result2
    conn2 = psycopg2.connect(host=host, port=port, user=user, password=pwd, database='postgres')
    autocommit = True
    cur2 = conn2.cursor()
    result2 = ""
    cur2.execute(sql)
    try:
        result2 = cur2.fetchall()
    except:
        result2 = "NULL"
    finally:
        pass
    conn2.close()
    cur2.close()
    conn2.close()
    return(result2)

def load_data():
    print("# 开始创建表")
    connect_pg1(Host, Port, User, Pwd)
    drop = 'drop table if exists item'
    sql = 'create table item(id int, name text)'
    exePg1('y', drop)
    exePg1('y', sql)
    close_pg1('pass', 'commit')

    print("# 载入1000行数据并提交")
    connect_pg1(Host, Port, User, Pwd)
    for i in range(1001):
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        exePg1('n', "insert into item values(%s, '%s')" % (str(i), ranStr))
    close_pg1('pass', 'commit')

def Read_uncommit():
    print("# 检查Read Uncommit隔离级别正确性(PG不支持)")
    print("### 事务二随机查询数据")
    ranNum = random.randint(1, 1001)
    sql2 = "select * from item where id = %s" % (ranNum)
    print(sql2)
    result2_1 = connect_pg2(Host, Port, User, Pwd, sql2)
    if str(result2_1) == '[]':
        print("未读取到对应数据！")
    else:
        print("读取到了数据：%s" % (result2_1))
    
    print("### 事务一修改刚刚查询的数据但不提交")
    set_RU = "set transaction isolation level read uncommitted"
    show_RU = "show transaction_isolation"

    Pg1Sql1 = 'BEGIN'
    Pg1Sql2 = "update item set name = 'update' where id = %s" % (ranNum)
    connect_pg1(Host, Port, User, Pwd)
    exePg1('y', Pg1Sql1)
    exePg1('y', set_RU)
    exePg1('y', Pg1Sql2)
    print(show_RU)
    cur1.execute(show_RU)
    tx_level = cur1.fetchone()
    print("### 当前事务一隔离级别是：%s" % (str(tx_level)))
    print("### 事务二现在查询相同数据")
    print(sql2)
    result2_2 = connect_pg2(Host, Port, User, Pwd, sql2)
    if result2_1 == result2_2:
        print("old: %s | new: %s\n 数据相同" % (result2_1, result2_2))
    else :
        print("old: %s | new: %s\n 数据不相同，失败" % (result2_1, result2_2))

    print("### 事务一提交修改后的数据")
    close_pg1('pass', 'commit')
    print("### 事务二再次查询相同数据")
    print(sql2)
    result2_3 = connect_pg2(Host, Port, User, Pwd, sql2)
    if result2_2 == result2_3:
        print("old: %s | new: %s\n 数据相同, 失败" % (result2_2, result2_3))
    else :
        print("old: %s | new: %s\n 数据不相同，成功" % (result2_2, result2_3))

def Serializable():
    pass   

def Drop_Table():
    dropSql = 'drop table if exists item'
    connect_pg2(Host, Port, User, Pwd, dropSql)

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description = "Kunlun transaction mode test")
    ps.add_argument("--host", type=str, help="Kunlunbase computing node host")
    ps.add_argument("--port", default=47001, type=int, help="KunlunBase computing node port, default value = 57001")
    ps.add_argument("--user", type=str, default='abc', help="KunlunBase computing node user,default value = 'abc'")
    ps.add_argument("--pwd", type=str, default='abc', help = "KunlunBase computing node password, default value = 'abc'")
    args = ps.parse_args()
    Host = args.host
    Port = args.port
    User = args.user
    Pwd = args.pwd
    print(args)
    load_data()
    Read_uncommit()

    Drop_Table()
