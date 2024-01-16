import psycopg2
from time import sleep
import random
import argparse
from multiprocessing import Process, Value, Manager
import time
import os

try:
    os.remove('./total_result.txt')
except:
    pass

def wFile(tran_mode, res):
    num = 1
    with open("total_result.txt", "a") as F:
        F.write('========\n%s\n========\n'% (tran_mode))
        F.write('|| times || [(单次事务首次查询R1), (首次查询R2), (单次事务首次查询R1与R2之和), (单次事务二次查询R1), (二次查询R2), (单次事务二查询R1与R2之和) ||\n')
        for i in res:
            F.write('|| %d || %s ||\n' % (num, str(i)))
            num = num+1
        F.write('\n')

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
    conn2.commit()
    cur2.close()
    conn2.close()
    return(result2)

def load_data():
    print("# 开始创建表")
    connect_pg1(Host, Port, User, Pwd)
    drop = 'drop table if exists item'
    sql = 'create table item(id int primary key, name text, C1 int)'
    exePg1('y', drop)
    exePg1('y', sql)
    close_pg1('pass', 'commit')

    print("# 载入1000行数据并提交")
    connect_pg1(Host, Port, User, Pwd)
    for i in range(1001):
        ranAge = random.randint(0, 100)
        ranStr = random.choice(['liangzai','is','llc','charles','trn','jgh','fhrq','fhxe','gewb'])
        exePg1('n', "insert into item values(%s, '%s', %d)" % (str(i), ranStr, ranAge))
    close_pg1('pass', 'commit')

def cutLine(Str):
    print('\n========\n%s\n========' % (Str))

def simple_test(tran_mode):
    cutLine('简单测试 -- %s' % (tran_mode))
    print("# 检查%s隔离级别正确性(PG不支持read uncommitted)" % (tran_mode))
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
    set_tm = "set transaction isolation level %s" % (tran_mode)
    show_tm = "show transaction_isolation"
    Pg1Sql1 = 'BEGIN'
    Pg1Sql2 = "update item set name = 'update_%s' where id = %s" % (tran_mode, ranNum)
    connect_pg1(Host, Port, User, Pwd)
    exePg1('y', Pg1Sql1)
    exePg1('y', set_tm)
    exePg1('y', Pg1Sql2)
    print(show_tm)
    cur1.execute(show_tm)
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

def T1Exec(tran_mode):
    connect_pg1(Host, Port, User, Pwd)
    print('3.2)	T1线程，产生一个新的整型的范围在1到100的随机数，在分布式数据库开启事务，扣减R1的C1字段该随机值数值，增加R2的C1字段该随机值数值，提交事务；然后T1线程循环执行此过程；')
    print('<< T1线程对数据 R1=%d && R2=%d 疯狂update中... >>' % (R1Id, R2Id))
    while True:
        RD1 = random.randint(1, 100)#生成1到100的随机数
        setSql = "set transaction isolation level %s" % (tran_mode)
        up1Sql = "update item set C1 = C1-%d where id = %d" % (RD1, R1Id)
        up2Sql = "update item set C1 = C1+%d where id = %d" % (RD1, R2Id)
        exePg1('n', 'begin')
        exePg1('n', setSql)
        exePg1('n', up1Sql)
        exePg1('n', up2Sql)
        exePg1('n', "commit")
        

def T2Exec(tran_mode):
    global singleResultList, TotalResultList, T2Times
    singleResultList, TotalResultList = [], []
    T2Times = 0
    setSql = "set transaction isolation level %s" % (tran_mode)
    R1Sql = "select C1 from item where id = %d" % (R1Id)
    R2Sql = "select C1 from item where id = %d" % (R2Id)
    sumSql = "select (%s)+(%s)" % (R1Sql, R2Sql)
    connT2 = psycopg2.connect(host=Host, port=Port, user=User, password=Pwd, database='postgres')
    autocommit = False
    curT2 = connT2.cursor()
    print('3.3) T2线程，休眠0.1秒，开启事务，查询R1与R2行的C1字段及其和并记录结果，休眠0.1秒，查询R1与R2行的C1字段及其和并记录结果，提交事务；>然后T2线程循环执行此过程1000次;')
    while T2Times != 1000:
        sleep(0.1)
        curT2.execute('begin')
        curT2.execute(setSql)
        curT2.execute(R1Sql)
        R1C1v1 = curT2.fetchone()
        curT2.execute(R2Sql)
        R2C1v1 = curT2.fetchone()
        curT2.execute(sumSql)
        C1Sum1 = curT2.fetchone()
        sleep(0.1)
        curT2.execute(R1Sql)
        R1C1v2 = curT2.fetchone()
        curT2.execute(R2Sql)
        R2C1v2 = curT2.fetchone()
        curT2.execute(sumSql)
        C1Sum2 = curT2.fetchone()
        curT2.execute('commit')
        singleResultList = [R1C1v1, R2C1v1, C1Sum1, R1C1v2, R2C1v2, C1Sum2]
        TotalResultList.append(singleResultList)
        T2Times = T2Times + 1
        print('\r当前查询次数 %d/1000' % (T2Times), end='')
    connT2.commit()
    curT2.close()
    connT2.close()
    T2tims = ['%d'%(T2Times)]
    T2Tim.append(T2tims)
    totalResultList.extend(TotalResultList)

def full_test(trans_mode):
    global R1Id, R2Id, curT1, curT2
    #T2Times = 0
    cutLine('充分测试 -- %s' % (trans_mode))
    R1Id = random.randint(1, 1000)
    R2Id = random.randint(1, 1000)
    while R1Id == R2Id : #当两个随机数相同时R2Id再随机一次，直到两个随机数不相等
        R2Id = random.randint(1, 1000)
    #把id列与随机数相同的数据的c1列值改成0
    print('<< 生产随机id：R1 = %d; R2 = %d >>' % (R1Id, R2Id))
    updateR1C1 = 'update item set C1 = 0 where id = %d' % (R1Id)
    updateR2C1 = 'update item set C1 = 0 where id = %d' % (R2Id)
    selectR1C1 = 'select C1 from item where id = %d'% (R1Id)#这一行是为了获取当c1值为0时，psycopg2返回的值，就是该行后三行的chTmpValue这个变量
    print('正在初始化对应数据\n%s\n%s' % (updateR1C1, updateR2C1))
    connect_pg2(Host, Port, User, Pwd, updateR1C1)
    chTmpValue = connect_pg2(Host, Port, User, Pwd, selectR1C1)
    connect_pg2(Host, Port, User, Pwd, updateR2C1)
    T1 = Process(target=T1Exec, args=(('%s' %trans_mode),))
    T2 = Process(target=T2Exec, args=(('%s' %trans_mode),))
    T1.start()
    sleep(0.2)
    T2.start()
    sleep(10)
    while True: 
        if str(T2Tim) == "[['1000']]":
            T1.terminate()
            T2.terminate()
            break
        else:
            sleep(1)
            continue
    listNum = 1
    wrgNum = 0
    print('\n--------\n检查%s汇总结果\n--------' % (trans_mode))
    print('检查所有R1、R2之和是否为0')
    for sumNum in totalResultList:
        if sumNum[2] != chTmpValue[0] or sumNum[5] != chTmpValue[0]:
            wrgNum = wrgNum+1
            print('第%d次事务查询，其R1、R2值："%s" : %s'% (listNum, sumNum[0], sumNum[1]))
            listNum = listNum + 1
        elif sumNum[5] != chTmpValue[0]:
            wrgNum = wrgNum+1
            print('第%d次事务查询，其R1、R2值："%s" : %s'% (listNum, sumNum[3], sumNum[4]))
            listNum = listNum + 1
    if wrgNum != 0:
        print('<< 本次检查中，有%d组R1与R2之和不为0的结果，与预期不符合 >>' % (wrgNum))
    else :
        print('<< 本次检查中，所有R1及R2之和都为0，与预期符合 >>')

    print('<< 检查R1值与R2值是否符合预期结果 >>')
    listNum = 0
    errNum = 0
    if trans_mode == 'repeatable read' or trans_mode == 'serializable':
        print('2.3)	在repeatable read与serializable的情况下，T2线程在事务中的读取，一次都不出现字段和不为0的现象，并且一次都不出现一个事务中两次查询R1的C1字段值发生变化的现象，可能并且应该出现，两个事务之间查询到的R1的C1字段值发生变化，若满足则repeatable read隔离级别大概率正确。')
        while listNum > 1000:
            if listNum == 0:
                R1Fro = totalResultList[listNum][0]
                R2Fro = totalResultList[listNum][3]
                if R1Fro != R2Fro:
                    print('第1次事务查询中，R1值%s和R2值%s不同，fail！'% (R1Fro, R2Fro))
                    errNum = errNum + 1
                listNum = listNum + 1
                
            else:
                R1Bak = totalResultList[listNum][0]
                R2Bak = totalResultList[listNum][3]
                if R1Fro != R2Fro:
                    print('第%s次事务查询中，R1值%s和R2值%s不同，fail！' % (listNum, R1Fro, R2Fro))
                    errNum = errNum + 1
                elif R1Bak != R2Bak:
                    print('第%s次事务查询中，R1值%s和R2值%s不同，fail！' % (listNum+1, R1Fro, R2Fro))
                    errNum = errNum + 1
                if R1Bak == R1Fro:
                    print("第%d次查询R1行C1值和第%d次R1行C1值相同，失败" %(listNum, listNum+1))
                    errNum = errNum + 1
                elif R2Bak == R2Fro:
                    print("第%d次查询R2行C1值和第%d次R2行C1值相同，失败" %(listNum, listNum+1))
                    errNum = errNum + 1
                R1Fro = R1Bak
                R2Fro = R2Bak
                listNum = listNum+1
        if errNum == 0:
            print('<< 当前充分测试所有R1及R2的C1值的汇总结果与预期相符 >>')
        else :
            print('<< 当前充分测试失败，请检查 >>')
        wFile(trans_mode, totalResultList)

    else:
        print('2.2)	在read commited的情况下，T2线程在事务中的读取，一次都不出现字段和不为0的现象，可能并且应该出现一个事务中两次查询R1的C1字段值发生变化，若满足则read commited隔离级别大概率正确。')
        while listNum > 1000:
            R1C1v = totalResultList[listNum][0]
            R2C1v = totalResultList[listNum][3]
            if R1Fro == R1Bak:
                print('第%d次查询中，R1行C1列值%s与R2行C1列值%s相同, fail' % (listNum+1, R1C1v, R2C1v))
                errNum = errNum + 1
            listNum = listNum+1
        if errNum == 0:
            print('<< 当前充分测试所有R1及R2的C1值的所有汇总结果与预期相符 >>')
        else :
            print('<< 当前充分测试失败，请检查 >>')
        wFile(trans_mode, totalResultList)

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
    total_start_time = time.time()
    load_data()
    tranList = ['read uncommitted', 'read committed', 'repeatable read', 'serializable']
    #tmpTranList = ['read committed', 'repeatable read', 'serializable']
    tmpTranList = ['read committed', 'repeatable read']
    print('\n因不支持read uncommitted隔离级别，故充分测试跳过该隔离级别')
    for simple_transaction_mode in tranList:
        simple_test(simple_transaction_mode)

    for full_transaction_mode in tmpTranList:
        startTime = time.time()
        T2Tim = Manager().list()
        totalResultList = Manager().list()
        end_target = full_test(full_transaction_mode)
        endTime = time.time()
        print('<< 本次充分测试%s使用了 %.2f 秒 >>' % (full_transaction_mode, endTime - startTime))
    Drop_Table()
    total_end_time = time.time()
    print('<< 本次测试一共用了 %.2f 秒 >>' % (total_end_time - total_start_time))
