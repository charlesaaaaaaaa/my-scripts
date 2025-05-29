from base.db.test.ddl import *

class z1024SelectTest():
    def __init__(self):
        pass

    def ddltran(self):
        writeLog('开始增加索引')
        testcase = createIndex()
        testcase.regularIndex('z1024table_8')
        testcase.uniuqIndex('z1024table_8')
        writeLog('开始增加列')
        testcase = addColumn()
        testcase.strColumn('z1024table_8')
        testcase.numrColumn('z1024table_8')


class a500SelectTest():
    pass