import multiprocessing
from threading import Thread
from time import sleep
from base.connection import *
from base.other.OPT import *
from base.db.prepare_data import *
from base.getconf import *

class load():
    def __init__(self):
        kunlunInfo = readcnf().getKunlunInfo()
        self.kunlunInfo = kunlunInfo

    def getColumnInfo(self):
        kunlunInfo = self.kunlunInfo
        sql = "select column_name, is_nullable, data_type, column_default, numeric_precision, numeric_scale from information_schema.columns where table_name = 'a500column' order by ordinal_position;"
        res = connPg().pgReturn(kunlunInfo['database'], sql)
        columnDict = {}
        for i in res:
            if i[3] == None:
                value = (i[1], i[2], i[4], i[5])
                tmpDict = {i[0]: value}
                columnDict.update(tmpDict)
        return columnDict

    def getSerialColumnInfo(self):
        res = load().getColumnInfo()
        smallSerial = []
        Serial = []
        bigSerial = []
        for i in res:
            if i[3] != None:
                if i[2] == 'smallint':
                    tmp = (i[0], i[3])
                    smallSerial.append(tmp)
                elif i[2] == 'integer':
                    tmp = (i[0], i[3])
                    Serial.append(tmp)
                elif i[2] == 'bigint':
                    tmp = (i[0], i[3])
                    bigSerial.append(tmp)
        columnDict = {'smallserial': smallSerial, 'serial': Serial, 'bigserial': bigSerial}
        return columnDict

    def genSqlData(self, columnList):
        datas = "("
        times = 1
        typeList = ["int", "integer", "smallint", "bigint", "decimal", "numeric", "real", "double precision",
                    "serial", "bigserial", "money", "character varying(32)", "varchar(32)", "character(32)", "char(32)",
                    "text", "bytea", "boolean", "cidr", "inet", "macaddr", "macaddr8", "Bit(16)", "timestamp",
                    "timestamp without time zone", "timestamp with time zone", "date", "time", "time without time zone",
                    "time with time zone", "text"]
        tmpTypeDataList = {}
        typeLen = len(typeList)
        now = 0
        for i in columnList:
            now += 1
            if now > typeLen:
                break
            try:
                tmpData = typeloader().genData(columnList[i][1])
                tmpList = {columnList[i][1]: tmpData}
                tmpTypeDataList.update(tmpList)
            except Exception as err:
                print(err)
                print(columnList[i][1])
                exit(1)
        for i in columnList:
            now = columnList[i][1]
            tmpData = tmpTypeDataList[now]
            if times == 1:
                datas = datas + str(tmpData)
                times = 0
            else:
                datas = datas + ', ' + str(tmpData)
        datas = datas + ')'
        return datas

    def process_List(self):
        testInfo = readcnf().getTestInfo()
        testprocess = int(testInfo['load_process'])
        sqlNum = int(testInfo['large_table_size'])
        each_process_size = int(sqlNum / testprocess)
        extra_process_size = sqlNum % testprocess
        process_dict = {}
        start_num = 0
        for i in range(testprocess):
            num = i + 1
            processName = 'process_%d' % num
            end_num = start_num + each_process_size
            if num <= extra_process_size:
                end_num += 1
            tmpDict = {processName: [start_num + 1, end_num]}
            start_num = end_num
            process_dict.update(tmpDict)
        return process_dict

    @timer
    def a500_data(self):
        columnList = load().getColumnInfo()
        testInfo = readcnf().getTestInfo()
        kunlunInfo = self.kunlunInfo
        process_list = self.process_List()
        db = kunlunInfo['database']
        batchNum = int(testInfo['load_500_batch_sql'])
        sqlNum = int(testInfo['large_table_size'])
        columns = '('
        times = 1
        global threadTimes
        threadTimes = 0
        for i in columnList:
            if times == 1:
                tmp = '%s' % i
                columns = columns + tmp
                times = 0
            else:
                tmp = '%s' % i
                columns = columns + ', ' + tmp
        def insertTran(batchNum):
            global threadTimes
            threadTimes += 1
            times = 1
            data = ''
            for i in range(batchNum):
                if times == 1:
                    data = str(load().genSqlData(columnList))
                    times = 0
                elif times != 1:
                    data = data + ', ' + str(load().genSqlData(columnList))
            sql = 'insert into a500column%s) values%s;' % (columns, data)
            connPg().pgNotReturn(db, sql)
        def signal_process(cur_process_list, batch_num):
            cur_total_size = cur_process_list[1] - cur_process_list[0] + 1
            if cur_total_size > batch_num:
                insert_times = int(cur_total_size / batch_num)
                extra_size = cur_total_size % batch_num
                if extra_size > 0:
                    insert_times += 1
                for i in range(insert_times):
                    if i == insert_times - 1:
                        insertTran(extra_size)
                    else:
                        insertTran(batch_num)
            else:
                insertTran(cur_process_list)

        l = []
        for process_name in process_list:
            cur_total_size = process_list[process_name][1] - process_list[process_name][0] + 1
            writeLog('%s 共插入 %s 行，%s' % (process_name, cur_total_size, process_list[process_name]))
            p = multiprocessing.Process(target=signal_process, args=(process_list[process_name], batchNum))
            l.append(p)
            p.start()
        for i in l:
            i.join()

    @timer
    def checkDataNum(self):
        global threadTimes
        threadTimes = 0
        selectSql = 'select count(*) from a500column'
        kunlunInfo = readcnf().getKunlunInfo()
        testInfo = readcnf().getTestInfo()
        dbname = kunlunInfo['database']
        large_table_sizes = int(testInfo['large_table_size'])
        current_data_num = int(connPg().pgReturn(dbname, selectSql)[0][0])
        load_batch_sql = int(testInfo['load_500_batch_sql'])
        threads = int(testInfo['load_process'])
        retryNum = int(large_table_sizes - current_data_num)
        columnList = load().getColumnInfo()
        columns = '('
        times = 1
        if large_table_sizes == current_data_num:
            exit(0)
        for i in columnList:
            if times == 1:
                tmp = '%s' % i
                columns = columns + tmp
                times = 0
            else:
                tmp = '%s' % i
                columns = columns + ', ' + tmp
        def insertSql(db, sql):
            global threadTimes
            threadTimes += 1
            connPg().pgNotReturn(db, sql)
            threadTimes -= 1
        while retryNum > 0:
            rangeTimes = int(retryNum / load_batch_sql)
            for i in range(rangeTimes):
                times = 1
                for ii in range(load_batch_sql):
                    if times == 1:
                        data = str(load().genSqlData(columnList))
                        times = 0
                    elif times != 1:
                        data = data + ', ' + str(load().genSqlData(columnList))
                sql = 'insert into a500column%s) values%s;' % (columns, data)
                l = []
                p = multiprocessing.Process(target=insertSql, args=(dbname, sql))
                l.append(p)
                p.start()
            for ii in l:
                ii.join()
            current_data_num = int(connPg().pgReturn(dbname, selectSql)[0][0])
            retryNum = int(large_table_sizes - current_data_num)
