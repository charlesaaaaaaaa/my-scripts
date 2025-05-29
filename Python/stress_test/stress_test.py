from base.db.prepare_data import *
from base.db.loaddata.a500 import *
from base.db.create import *
from base.connection import *
from base.db.loaddata.z1024 import *
from base.other.OPT import *
from base.getconf import *
from base.db.test.superHugeTran import *
from base.db.test.case import *
from time import sleep

@timer
def create_table():
    writeLog('\n=========\n开始创建1024张分区表\n========')
    z1024Partition().create1024Table()
    writeLog('\n========\n开始创建1张极限大宽表\n========')
    a500Columns().create500ColumnTable()

@timer
def loadData():
    writeLog('\n========\n开始准备1024张分区表数据\n========')
    z1024load().load_data()
    writeLog('\n========\n开始准备极限大宽表数据\n========')
    load().genLoadSql()
    load().checkDataNum()

def test():
    z1024_test().cases()
    #c500_test().cases()

@timer
def super_huge_cluster():
    writeLog('\n=========\n开始创建1024张分区表\n========')
    z1024Partition().create1024Table()
    sleep(1800)
    writeLog('\n========\n开始准备1024张分区表数据\n========')
    z1024load().load_data()
    #writeLog('\n========\n开始测试1024张分区表\n========')
    #z1024_test().cases()

@timer
def super_huge_table():
    writeLog('\n========\n开始创建1张极限大宽表\n========')
    a500Columns().create500ColumnTable()
    writeLog('\n========\n开始准备极限大宽表数据\n========')
    load().a500_data()
    load().checkDataNum()
    #writeLog('\n========\n开始测试极限大宽表\n========')
    #c500_test().cases()

if __name__ == '__main__':
    #super_huge_cluster()
    super_huge_table()
