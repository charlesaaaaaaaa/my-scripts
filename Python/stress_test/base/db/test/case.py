from base.db.test.ddl import *
from base.db.test.superHugeTran import *
from base.db.test.selectSuperHugeData import *
from base.connection import *
from threading  import Thread

class z1024_test():
    def __init__(self):
        self.tableNameList = ['z1024table_8', 'z1024table_1024']

    def mutilThread(self, case):
        tableNameList = self.tableNameList
        l = []
        for i in tableNameList:
            p = Thread(target=case, args=i)
            l.append(p)
            p.start()

    def cases(self):
        writeLog('Test 1:\n\t一个事务中灌入500GB以上数据，分别到到上述大单表t1和大分区表。')
        def case_one_tran_500g(tableName):
            forSuperHugeTran().oneTran_500G(tableName)
        self.mutilThread(case_one_tran_500g)
        writeLog('Test 2:\n\t单语句autocommit事务分别全量更新t1和t2的某几个列。')
        def case_singalSql_autocommit(tableName):
            forSuperHugeTran().updateTable_t1_t2_forOneCommit(tableName)
        self.mutilThread(case_singalSql_autocommit)
        writeLog('Test 3:\n\ttext字段分别插入1行和更新1行和1000行，其单子段数据量10GB。。')
        def case_test_insert_and_update_10Gdata(tableName):
            forSuperHugeTran().insert1row_10G(tableName)
            forSuperHugeTran().update1rowAnd1000Row_10G(tableName)
        self.mutilThread(case_test_insert_and_update_10Gdata)
        writeLog('Test 4:\n\t给t1/2/3建立索引和唯一索引')
        def case_create_index(tableName):
            createIndex().regularIndex(tableName)
            createIndex().uniuqIndex(tableName)
        self.mutilThread(case_create_index)
        writeLog('Test 5:\n\t给t1/2/3增加一个数值列和一个字符串列')
        def case_add_columns(tableName):
            addColumn().strColumn(tableName)
            addColumn().numrColumn(tableName)
        self.mutilThread(case_add_columns)
        writeLog('Test 6:\n\t使用下述组合产生查询：')
        def case_select_case(tableName):
            superHuge_select(tableName).selectTest(1)
        self.mutilThread(case_select_case)
        writeLog('========\n大集群测试完毕\n========')

class c500_test():
    def __init__(self):
        self.tableName = 'c500column'

    def cases(self):
        tableName = self.tableName
        writeLog('Test 1:\n\t一个事务中灌入500GB以上数据，分别到到上述大单表t1和大分区表。')
        forSuperHugeTran().oneTran_500G(tableName)
        writeLog('Test 2:\n\t单语句autocommit事务分别全量更新t1和t2的某几个列。')
        forSuperHugeTran().updateTable_t1_t2_forOneCommit(tableName)
        writeLog('Test 3:\n\ttext字段分别插入1行和更新1行和1000行，其单子段数据量10GB。。')
        forSuperHugeTran().insert1row_10G(tableName)
        forSuperHugeTran().update1rowAnd1000Row_10G(tableName)
        writeLog('Test 4:\n\t给t1/2/3建立索引和唯一索引')
        createIndex().regularIndex(tableName)
        createIndex().uniuqIndex(tableName)
        writeLog('Test 5:\n\t给t1/2/3增加一个数值列和一个字符串列')
        addColumn().strColumn(tableName)
        addColumn().numrColumn(tableName)
        writeLog('Test 6:\n\t使用下述组合产生查询：')
        rangeTimes = random.randint(50, 200)
        for i in range(rangeTimes):
            superHuge_select(tableName).selectTest(0)
        writeLog('========\n大宽表测试完毕。\n========')

class new_test():
    pass