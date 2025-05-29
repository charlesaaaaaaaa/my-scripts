import random
from threading import Thread
from time import sleep
from base.connection import *
from base.getconf import *
import time
from base.other.OPT import *

class a500Columns():
    def __init__(self):
        #smallserial不测了，容易到3w多后失败
        typeList = ["int", "integer", "smallint", "bigint", "decimal", "numeric", "real", "double precision",
                    "serial", "bigserial", "money", "character varying(32)", "varchar(32)", "character(32)", "char(32)",
                    "text", "bytea", "boolean", "cidr", "inet", "macaddr", "macaddr8", "Bit(16)", "timestamp",
                    "timestamp without time zone", "timestamp with time zone", "date", "time", "time without time zone",
                    "time with time zone", "text"]
        self.typeList = typeList
        self.kunlunInfo = readcnf().getKunlunInfo()

    @timer
    def create500ColumnTable(self):
        typeList = self.typeList
        kunlunInfo = self.kunlunInfo
        listNum = 1
        notNum = 0
        cannotUnique = ["smallint", "boolean", "date", "time", "time without time zone", "time with time zone", "real", "Bit(16)"]
        insType = ["character varying(32)", "varchar(32)", "character(32)", "char(32)", "double precision", "numeric"]
        createSql = 'create table a500column(id bigserial PRIMARY KEY'
        dbSql = 'create database if not exists %s' % (kunlunInfo['database'])
        connPg().pgNotReturn('postgres', dbSql)
        large_table_column_num = int(readcnf().getTestInfo()['large_table_column_num'])
        for i in range(1, large_table_column_num):
            columnNum = i + 1
            columnType = typeList[listNum]
            if i < len(typeList):
                if typeList[i] in cannotUnique:
                    #tmpColumn = ', column_%s %s' % (columnNum, typeList[i])
                    tmpColumn = ', c%s %s' % (columnNum, typeList[i])
                    createSql = createSql + tmpColumn
                else:
                    #tmpColumn = ', column_%s %s UNIQUE' % (columnNum, typeList[i])
                    tmpColumn = ', c%s %s UNIQUE' % (columnNum, typeList[i])
                    createSql = createSql + tmpColumn
            else:
                if notNum == 0:
                    #tmpColumn = ', column_%s %s NOT NULL' % (columnNum, columnType)
                    tmpColumn = ', c%s %s NOT NULL' % (columnNum, columnType)
                    if columnType == 'int':
                        #tmpColumn = ', column_%s %s UNIQUE NOT NULL' % (columnNum, columnType)
                        tmpColumn = ', c%s %s UNIQUE NOT NULL' % (columnNum, columnType)
                    createSql = createSql + tmpColumn
                else:
                    #tmpColumn = ', column_%s %s' % (columnNum, columnType)
                    if columnType in insType and i > 200:
                        columnType = 'text'
                    tmpColumn = ', c%s %s' % (columnNum, columnType)
                    createSql = createSql + tmpColumn
                listNum += 1
                if columnType == typeList[-1]:
                    listNum = 0
                    notNum = 1
        createSql = '%s);' % createSql
        writeLog(createSql)
        connPg().pgNotReturn(kunlunInfo['database'], createSql)
        sleep(10)

class z1024Partition():
    def __init__(self):
        self.kunlunInfo = readcnf().getKunlunInfo()
        #self.partiNum = [2, 3, 4, 5, 6, 7, 8, 10]

    @timer
    def create1024Table(self):
        global threadTimes
        threads = readcnf().getTestInfo()['load_threads']
        kunlunInfo = self.kunlunInfo
        #partiNum = [2, 3, 4, 5, 6, 7, 8, 10]
        partiNum = [16, 64, 256, 1024, 2048, 4096, 8192, 16384]
        curPartitionTotalNum = 1
        curPartitionNum = 1
        pre8TableRowNum = 0
        pre8ListNum = 0
        threadTimes = 0
        dbSql = 'create database if not exists %s' % (kunlunInfo['database'])
        connPg().pgNotReturn('postgres', dbSql)
        for i in partiNum:
            pre8TableRowNum += i
        def createPartitionTable(tableNum, totalPartitionTableNum, curPartitionTable):
            global threadTimes
            threadTimes += 1
            sql = "create table z1024table_%s_%s partition of z1024table_%s for values with " \
                  "(MODULUS %s, REMAINDER %s);" % (
                  tableNum, curPartitionTable, tableNum, totalPartitionTableNum, curPartitionTable)
            connPg().pgNotReturn(kunlunInfo['database'], sql)
            threadTimes -= 1

        writeLog('创建前8个主分区表。。。')
        for i in range(1, 9):  # 创建前8个表
            createSql = 'create table if not exists z1024table_%s(id bigserial, grp int, t text) partition by hash(id);' % i
            connPg().pgNotReturn(kunlunInfo['database'], createSql)
        writeLog('%s 开始创建子分区表' % time.asctime(time.localtime(time.time())))
        writeLog('%s 开始创建 z1024table_%s 子分区表, 共有 %s 张子分区表' % (
        time.asctime(time.localtime(time.time())), pre8ListNum, partiNum[pre8ListNum]))
        while curPartitionTotalNum <= pre8TableRowNum:  # 先创建前8个表的分区表
            l = []
            p = Thread(target=createPartitionTable, args=[pre8ListNum + 1, partiNum[pre8ListNum], curPartitionNum - 1])
            l.append(p)
            p.start()
            if curPartitionTotalNum == pre8TableRowNum:
                break
            if curPartitionNum == partiNum[pre8ListNum]:
                curPartitionNum = 0
                pre8ListNum += 1
                curProgress = curPartitionTotalNum / pre8TableRowNum
                print(
                    '\r%s 所有 z1024table_%s 子分区表创建完成, 开始创建 z1024table_%s 子分区表, 共有 %s 张子分区表\n' % (
                    time.asctime(time.localtime(time.time())), pre8ListNum, pre8ListNum, partiNum[pre8ListNum]),
                    end='')
                print('\r%s 当前进度 %.3f%%' % (time.asctime(time.localtime(time.time())), curProgress * 100), end='')
            curPartitionTotalNum += 1
            curPartitionNum = curPartitionNum + 1
            while threadTimes >= int(threads):
                sleep(0.1)
            doneTims = curPartitionTotalNum - threadTimes
            if doneTims % 20 == 0:
                curProgress = curPartitionTotalNum / pre8TableRowNum
                print('\r%s 当前进度 %.3f%%' % (time.asctime(time.localtime(time.time())), curProgress * 100), end='')
        curProgress = curPartitionTotalNum / pre8TableRowNum
        print('\r所有 z1024table_8 子分区表创建完成\n', end='')
        print('%s 当前进度 %.3f%%' % (time.asctime(time.localtime(time.time())), curProgress * 100))

        # 开始创建后面的1016张表
        def create1016PartitionTable(tableNum, totalPartitionTableNum):
            global threadTimes
            threadTimes += 1
            createSql = 'create table if not exists z1024table_%s(id bigint, grp int, t text) partition by hash(id);' % tableNum
            connPg().pgNotReturn(kunlunInfo['database'], createSql)
            writeLog('%s 开始创建 z1024table_%s 子分区表，共 %s 张子分区表' % (
                time.asctime(time.localtime(time.time())), tableNum, partitionTableNum))
            for i in range(totalPartitionTableNum):
                sql = "create table z1024table_%s_%s partition of z1024table_%s for values with " \
                      "(MODULUS %s, REMAINDER %s);" % (tableNum, i, tableNum, totalPartitionTableNum, i)
                connPg().pgNotReturn(kunlunInfo['database'], sql)
            threadTimes -= 1
            writeLog('%s z1024table_%s 创建完毕' % (time.asctime(time.localtime(time.time())), tableNum))

        def create512TableAfter(tableNum):
            global threadTimes
            threadTimes += 1
            createSql = 'create table if not exists z1024table_%s(id bigint, grp int, t text)' % tableNum
            writeLog('%s 开始创建 z1024table_%s 常规表' % (time.asctime(time.localtime(time.time())), tableNum))
            connPg().pgNotReturn(kunlunInfo['database'], createSql)
            threadTimes -= 1
            writeLog('%s z1024table_%s 创建完毕' % (time.asctime(time.localtime(time.time())), tableNum))

        writeLog('%s 开始创建后面1016张分区表' % time.asctime(time.localtime(time.time())))
        num = 1
        for tableNum in range(9, 1025):
            l = []
            if tableNum <= 512:
                partitionTableNum = random.randint(2, 16)
                p = Thread(target=create1016PartitionTable, args=[tableNum, partitionTableNum])
                l.append(p)
                p.start()
            else:
                p = Thread(target=create512TableAfter, args=[tableNum])
                l.append(p)
                p.start()
            while threadTimes > int(threads):
                sleep(0.05)