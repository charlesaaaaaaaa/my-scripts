from base.connection import *
from base.getconf import *
import random

class superHuge_select():
    def __init__(self, tableName):
        self.kunlunInfo = readcnf().getKunlunInfo()
        self.tableName = tableName
        sql = "select column_name, data_type, is_nullable from information_schema.columns where table_name = '%s' " \
              "and column_default == null order by ordinal_position;" % tableName
        indexSql = "select indexdef from pg_indexes where tablename = '%s';" % tableName
        self.columns = connPg().pgReturn(self.kunlunInfo['database'], sql)
        self.indexs = connPg().pgReturn(self.kunlunInfo['database'], indexSql)

    def uniqueOrNot(self):
        columndict = self.columns
        indexList = self.indexs
        unique = []
        not_unique = []
        for i in indexList:
            uniqueColumnName = str(i).split('(')[2].split(' ')[0]
            unique.append(uniqueColumnName)
        for i in columndict:
            if i[0] not in unique:
                not_unique.append(i[0])
        res = {'unique': unique, "not_unique": not_unique}
        return res

    #获取sql前面要筛选的列，及是否要进行聚合操作
    def columns_aggOrNot(self):
        global idList
        tableName = self.tableName
        uniqueDict = superHuge_select(tableName).uniqueOrNot()
        kunlunInfo = self.kunlunInfo
        sql = 'select id from %s' % tableName
        idList = connPg().pgReturn(kunlunInfo['database'], sql)
        #opt = random.randint(0, 3)
        opt = 3
        #0是选择全部列，1是不进行聚合查询， 2、3是进行聚合查询
        if opt == 0:
            columns = '*'
        elif opt == 1:
            tmpcolumnList = uniqueDict['unique'] + uniqueDict['not_unique']
            if len(tmpcolumnList) > 500:
                rangeTimes = random.randint(10, 500)
            else:
                rangeTimes = random.randint(1, len(tmpcolumnList))
            column = []
            for i in range(rangeTimes):
                tmpcolumn = random.choice(tmpcolumnList)
                tmpcolumnList.remove(tmpcolumn)
                while tmpcolumn in column:
                    tmpcolumn = random.choice(tmpcolumnList)
                column.append(tmpcolumn)
            columns = ','.join(column)
        else:
            tmpcolumnList = uniqueDict['unique'] + uniqueDict['not_unique']
            columnType = self.columns
            print(uniqueDict)
            rangeTimes = random.randint(1, len(uniqueDict['not_unique']))
            column = []
            for i in range(rangeTimes):
                tmpcolumn = random.choice(tmpcolumnList)
                tmpcolumnList.remove(tmpcolumn)
                numericType = ['bigint', 'integer', 'smallint', 'numeric', 'real', 'double precision', 'money']
                a=0
                for row in columnType:
                    if tmpcolumn in row:
                        if row[1] in numericType:
                            tmp = ['AVG', 'COUNT', 'MAX', 'MIN', 'SUM']
                        else:
                            tmp = ['COUNT', 'MAX', 'MIN']
                        break
                    else:
                        a += 1
                random_agg = random.choice(tmp)
                curcolumn = '%s(%s)' % (random_agg, tmpcolumn)

                while curcolumn in column:
                    curcolumn = random.choice(tmpcolumnList)
                column.append(curcolumn)
            columns = ','.join(column)
        return columns

    def where(self, num, grpNum):
        kunlunInfo = self.kunlunInfo
        tableName = self.tableName
        tmpsql = 'select id from %s' % tableName
        idList = connPg().pgReturn(kunlunInfo['database'], tmpsql)
        randomId = random.choice(idList)[0]
        if num == 0:
            opt = random.randint(0, 6)
            if opt == 0:
                whereSql = 'where id = %s' % randomId
            elif opt == 1 or opt == 2 or opt == 3:
                whereSql = 'where id > %s' % randomId
            else:
                whereSql = 'where id < %s' % randomId
        else:
            length = len(idList)
            opt = random.randint(0, length - num)
            startNum = opt
            endNum = opt + num
            startId = idList[startNum][0]
            endId = idList[endNum][0]
            whereSql = 'where id between %s and %s' % (startId, endId)
        if grpNum != 0:
            whereSql = 'where grp = %s' % grpNum
        return whereSql

    def getSQL(self, num, grpNum):
        #num 和 grpNum只有有一个不是0，或者两个都是0
        #num 不为0时，会产生num行的数据的查询sql， 为0且grpNum为0时，在 = < > 三种比较符中随机选择其中一个
        #grpNum不为0时，则where只选择grp列值为grpNum的数据， 为0则不选择grp列的值
        tableName = self.tableName
        uniqueDict = self.uniqueOrNot()
        whereOrnot = random.randint(0, 2)
        groupOrnot = random.randint(0, 2)
        orderOrnot = random.randint(0, 2)
        selectColumn = self.columns_aggOrNot()
        if selectColumn != '*':
            selectList = selectColumn.replace(')','').replace('MAX(', '').replace('AVG(','').replace('MIN(','')\
                .replace('COUNT(','').replace('SUM(','').split(',')
        sql = ''
        if whereOrnot != 0 and num == 0:
            sql = self.where(0, 0)
        elif num != 0:
            sql = self.where(num, 0)
        elif num == 0 and whereOrnot == 0:
            sql = ''
        if grpNum != 0:
            sql = self.where(0, grpNum)
        if groupOrnot != 0:
            uniqueList = uniqueDict['unique'] + uniqueDict['not_unique']
            groupSql = ' group by '
            if selectList:
                groupRangeTimes = random.randint(1, len(selectList))
            else:
                if len(uniqueList) > 100:
                    groupRangeTimes = random.randint(1, 100)
                else:
                    groupRangeTimes = random.randint(1, len(uniqueList))
            for i in range(groupRangeTimes):
                if selectList:
                    column = random.choice(selectList)
                    selectList.remove(column)
                else:
                    column = random.choice(uniqueList)
                    uniqueList.remove(column)
                if i == 0:
                    groupSql = groupSql + column
                else:
                    groupSql = groupSql + ', ' + column
            sql = sql + groupSql
        if orderOrnot != 0:
            uniqueList = uniqueDict['unique'] + uniqueDict['not_unique']
            orderList = selectColumn.split(',')
            orderSql = ' order by '
            if orderList:
                orderRangeTimes = random.randint(1, len(selectList))
            else:
                if len(uniqueList) > 100:
                    orderRangeTimes = random.randint(1, 100)
                else:
                    orderRangeTimes = random.randint(1, len(uniqueList))
            for i in range(orderRangeTimes):
                if orderList:
                    column = random.choice(orderList)
                    orderList.remove(column)
                else:
                    column = random.choice(uniqueList)
                    uniqueList.remove(column)
                if i == 0:
                    orderSql = orderSql + column
                else:
                    orderSql = orderSql + ', ' + column
            sql2 = sql + orderSql
            sql = 'select %s from %s %s  ' % (selectColumn, tableName, sql2)
        return sql

    def selectTest(self, grpOrNot):
        kunlunInfo = self.kunlunInfo
        dbname = kunlunInfo['database']
        if grpOrNot == 1:
            num = 0
        else:
            num = random.randint(0, 1)
            if num == 1:
                num = random.choice([1000000, 100000000])
        sql = self.getSQL(num, grpOrNot)
        res = connPg().pgReturn(dbname, sql)
