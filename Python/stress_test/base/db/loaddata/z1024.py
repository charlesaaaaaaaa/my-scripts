from base.connection import *
from base.getconf import *
from threading import Thread
import threading
from base.other.OPT import *
from time import sleep

class z1024load():
    def __init__(self):
        testInfo = readcnf().getTestInfo()
        self.testInfo = testInfo

    def createRow(self, tableName, totalNum):
        #该函数是用来产生insert的sql的
        datas = ''
        gTimes = 1
        totalNum = int(totalNum)
        def create():
            data = ()
            strRow = ''
            str = random.choice('abcdefghijklmnopqrstuvwxyz')
            #strTmp = '%s%s%s%s-%s%s%s%s-%s%s%s%s-%s%s%s%s-%s%s%s%s-' % (
            #    str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str)
            strTmp = '%s%s%s%s-' % (str, str, str, str)
            strTmp1 = '%s%s%s%s%s' % (strTmp, strTmp, strTmp, strTmp, strTmp)
            strTmp = '%s%s%s%s%s' % (strTmp1, strTmp1, strTmp1, strTmp1, strTmp1)
            #for i in range(50):
            for i in range(10):
                strRow = strRow + strTmp
            grp = random.randint(1, 1000)
            row = (grp, strRow)
            data = data + (row,)
            return data
        for i in range(totalNum):
            data = str(create()[0])
            if gTimes == 1:
                datas = data
                gTimes = 0
            else:
                datas = datas + ', ' + data
        insertSql = 'insert into %s(grp, t) values%s' % (tableName, datas)
        insertSql = insertSql + ';'
        return insertSql

    def batchInsert(self, tableName, totalNum):
        totalNum = int(totalNum)
        dbname = readcnf().getKunlunInfo()['database']
        insertSql = z1024load().createRow(tableName, totalNum)
        connPg().pgNotReturn(dbname, insertSql)

    def checkLoadNum(self, tableName, totalNum, batchNum):
        dbname = readcnf().getKunlunInfo()['database']
        sql = 'select count(*) from %s' % tableName
        currentDataNum = connPg().pgReturn(dbname, sql)[0][0]
        print(tableName, currentDataNum)
        leftDataNum = totalNum - currentDataNum
        if leftDataNum > 0:
            print('当前少 %s 行数据于 % 表' % (leftDataNum, tableName))
        while leftDataNum > 0:
            rangeTimes = int(leftDataNum / batchNum)
            extraSize = leftDataNum % batchNum
            writeLog('开始灌前 %s, 共 %s 行数据，当前db为 %s' % (tableName, totalNum, dbname))
            if extraSize > 0:
                rangeTimes += 1
                for i in range(rangeTimes):
                    if i == rangeTimes - 1:
                        startNum = totalNum - extraSize - (batchNum * (rangeTimes - i + 1))
                        endNum = totalNum
                    else:
                        startNum = totalNum - extraSize - (batchNum * (rangeTimes - i + 1))
                        endNum = totalNum - extraSize - (batchNum * (rangeTimes - i))
                    insertSql = z1024load().createRow(tableName, totalNum)
                    connPg().pgNotReturn(dbname, insertSql)
            currentDataNum = int(connPg().pgReturn(dbname, sql)[0][0])
            leftDataNum = totalNum - currentDataNum

    def create_table_postion(self, totalCount, pratList, startTableNum):
        # 这个是根据8个分区表对应的子分区表数量与总分区表的占比而决定每个表的数据量
        # 得出所有子分区表平均数
        all = 0
        for i in pratList:
            all += i
        each_son_partition_num = int(totalCount / all)
        extra_son_partition_num = totalCount % all
        # 算出所有表的行数及其在总行数对应的位置
        table_position_dict = {}
        table_num = 0
        curTable_startNum = startTableNum - 1
        for i in pratList:
            table_num += 1
            table_name = 'z1024table_%s' % table_num
            if i < extra_son_partition_num:
                table_rowNum = each_son_partition_num * i + i
                extra_son_partition_num -= i
            elif i > extra_son_partition_num:
                table_rowNum = each_son_partition_num * i + extra_son_partition_num
                extra_son_partition_num = 0
            elif extra_son_partition_num == 0:
                table_rowNum = each_son_partition_num * i
            tmpList = [curTable_startNum + 1, table_rowNum + curTable_startNum]
            curTable_startNum += table_rowNum
            tmpDict = {table_name: tmpList}
            table_position_dict.update(tmpDict)
        return table_position_dict

    def create_table_postion_avg(self, totalCount, mode):
        table_position_dict = {}
        cur_start_num = 0
        if mode == 'middle':
            # 这个就是第9个分区表到1022个表的情况，共1014个表，其中有510个是单表
            eachTable_size = int(totalCount / 1014)
            extra_eachTable_size = totalCount % 1014
            for i in range(9, 1023):
                tableName = 'z1024table_%s' % i
                extra_times = i - 8
                if extra_eachTable_size >= extra_times:
                    curTable_size = eachTable_size + 1
                else:
                    curTable_size = eachTable_size
                cur_end_num = curTable_size + cur_start_num
                tmp_dict = {tableName: [cur_start_num, cur_end_num]}
                cur_start_num = cur_end_num
                table_position_dict.update(tmp_dict)
        elif mode == 'last':
            testInfo = self.testInfo
            table1024_table1_size = int(testInfo['table1024_table1_size'])
            table1024_table2_size = int(testInfo['table1024_table2_size'])
            table_position_dict = {'z1024table_1023': [0, table1024_table1_size], 'z1024table_1024': [table1024_table1_size, table1024_table1_size + table1024_table2_size]}
        #print(table_position_dict)
        return table_position_dict

    def thread_range(self, totalCount, threads, table_position_dict, startNum):
        each_thread_rowNum = int(totalCount / threads)
        extra_thread_rowNum = totalCount % threads
        ## 得出所有线程数各要灌多少数据量
        thread_range_dict = {}
        curThread_startNum = 0
        ## 先算出所有thread负责的数据范围
        for i in range(1, threads + 1):
            threadName = "thread_%s" % i
            if i <= extra_thread_rowNum:
                thread_rowNum = each_thread_rowNum + 1
            else:
                thread_rowNum = each_thread_rowNum
            tmpList = [curThread_startNum + 1, thread_rowNum + curThread_startNum]
            tmpDict = {threadName: tmpList}
            thread_range_dict.update(tmpDict)
            curThread_startNum += thread_rowNum
        #print(thread_range_dict)
        ## 再根据前面得出的所有表的范围得出所有线程负责的范围及表
        threads_dict = {}
        curTable_num = startNum
        for i in range(1, threads + 1):
            first_dict = {}
            second_dict = {}
            thread_name = 'thread_%s' % i
            curTable_name = 'z1024table_%s' % curTable_num
            curThread_startNum = thread_range_dict[thread_name][0]  # thread初始位置应该是thread最小位置
            curThread_maxNum = thread_range_dict[thread_name][1]
            curMax_tableRange = table_position_dict[curTable_name][1]
            while curThread_maxNum > curMax_tableRange:
                curThread_endNum = curMax_tableRange
                tmpDict = {curTable_name: [curThread_startNum, curThread_endNum]}
                #if curTable_num < len(table_position_dict):
                curTable_num += 1
                curTable_name = 'z1024table_%s' % curTable_num
                second_dict.update(tmpDict)
                curMax_tableRange = table_position_dict[curTable_name][1]
                curMin_tableRange = table_position_dict[curTable_name][0]
                curThread_startNum = curMin_tableRange
            first_dict.update(second_dict)
            curMax_tableRange = table_position_dict[curTable_name][1]
            curMin_tableRange = table_position_dict[curTable_name][0]
            if curThread_maxNum <= curMax_tableRange and curThread_maxNum >= curMin_tableRange:
                curThread_startNum = curThread_startNum
                curThread_endNum = curThread_maxNum
                tmpDict = {curTable_name: [curThread_startNum, curThread_endNum]}
                second_dict.update(tmpDict)
            first_dict.update(second_dict)
            tmpDict = {thread_name: first_dict}
            threads_dict.update(tmpDict)
        return threads_dict

    @timer
    def load_data(self):
        testInfo = self.testInfo
        global Thread_Times
        Thread_Times = 0
        partList = [16, 64, 256, 1024, 2048, 4096, 8192, 16384]
        pre8_totalCount = int(testInfo['table1024_pre8table_size'])
        threads = int(testInfo['load_threads'])
        table1024_table1_size = int(testInfo['table1024_table1_size'])
        table1024_table2_size = int(testInfo['table1024_table2_size'])
        batch_num = int(testInfo['load_1024_batch_sql'])
        last2_totalCount = table1024_table1_size + table1024_table2_size
        middle_totalCount = int(testInfo['table1024_total_size']) - pre8_totalCount - last2_totalCount
        pre8_table_position_list = self.create_table_postion(pre8_totalCount, partList, 1)
        middle_table_position_list = self.create_table_postion_avg(middle_totalCount, 'middle')
        last2_table_position_list = self.create_table_postion_avg(last2_totalCount, 'last')
        pre8_threads_list = self.thread_range(pre8_totalCount, threads, pre8_table_position_list, 1)
        middle_thread_list = self.thread_range(middle_totalCount, threads, middle_table_position_list, 9)
        lase2_thread_list = self.thread_range(last2_totalCount, threads, last2_table_position_list, 1023)

        def insert_data(threadName, thread_Table_list, batchNum):
            global Thread_Times
            Thread_Times += 1
            for table_name in thread_Table_list:
                totalSize = int(thread_Table_list[table_name][1]) - int(thread_Table_list[table_name][0]) + 1
                total_insert_times = int(totalSize / batchNum)
                extra_insert_size = totalSize % batchNum
                writeLog('%s 准备 %s 共 %s 行, %s' % (threadName, table_name, totalSize,  thread_Table_list[table_name]))
                if extra_insert_size > 0:
                    total_insert_times += 1
                for table_insert_times in range(total_insert_times):
                    if table_insert_times == total_insert_times - 1:
                        self.batchInsert(table_name, extra_insert_size)
                    else:
                        self.batchInsert(table_name, batchNum)
            Thread_Times -= 1

        for i in range(3):
            if i == 0:
                curThread_list = pre8_threads_list
            elif i == 1:
                curThread_list = middle_thread_list
            elif i == 2:
                curThread_list = lase2_thread_list
            for thread_name in curThread_list:
                    l = []
                    p = Thread(target=insert_data, args=[thread_name, curThread_list[thread_name], batch_num])
                    l.append(p)
                    p.start()
                    while Thread_Times >= threads:
                        sleep(0.01)