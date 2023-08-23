# -*- coding: utf-8 -*-
from base.other import copyconfig
from base.other.otherOpt import *

global total, times
total = 0
times = 0

def getNum(Times):
    global total, times
    total += 1
    times = times + Times

def mysqlToKlustron():
    from base import test
    from base.other.otherOpt import restartCdcCluster
    res = test.mysqlToKunlun().regular_test()
    getNum(res)
    #res = test.mysqlToKunlun().killCdcMasterWhenCdcIsRunning()
    #getNum(res)
    res = test.mysqlToKunlun().killSourceMysqlWhenCdcIsRunning()
    getNum(res)
    res = test.mysqlToKunlun().killTargeKlustronWherCdcIsRunning()
    getNum(res)
    restartCdcCluster()

def kunlunToMysql():
    from base.test import kunlunToMysql
    from base.other.otherOpt import restartCdcCluster
    res = kunlunToMysql().regular_test()
    getNum(res)
    #res = kunlunToMysql().killCdcMasterWhenCdcIsRunning()
    #getNum(res)
    res = kunlunToMysql().killTargetMysqlWhenCdcIsRunning()
    getNum(res)
    res = kunlunToMysql().killSourceKunlunWhenCdcIsRunning()
    getNum(res)
    restartCdcCluster()

if __name__ == '__main__':
    copyconfig.Mode('regular')
    #copyconfig.Mode('regular')
    mysqlToKlustron()
    kunlunToMysql()
    if total == times:
        writeLog('所有测试成功')
        exit(0)
    else:
        writeLog('有%s条测试失败' % (total - times))
        exit(1)