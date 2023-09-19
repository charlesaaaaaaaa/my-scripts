# -*- coding: utf-8 -*-
from base.other import copyconfig
from base.other.otherOpt import *

succ = []
fail = []

def getNum(res):
    if res[1] == 1:
        succ.append(res[0])
    elif res[1] == 0:
        fail.append(res[0])

def mysqlToKlustron():
    from base import test
    from base.other.otherOpt import restartCdcCluster
    restartCdcCluster()
    res = test.mysqlToKunlun().regular_test()
    getNum(res)
    #res = test.mysqlToKunlun().killCdcMasterWhenCdcIsRunning()
    #getNum(res)
    restartCdcCluster()
    res = test.mysqlToKunlun().killSourceMysqlWhenCdcIsRunning()
    getNum(res)
    restartCdcCluster()
    res = test.mysqlToKunlun().killTargeKlustronWherCdcIsRunning()
    getNum(res)

def kunlunToMysql():
    from base.test import kunlunToMysql
    from base.other.otherOpt import restartCdcCluster
    restartCdcCluster()
    res = kunlunToMysql().regular_test()
    getNum(res)
    #res = kunlunToMysql().killCdcMasterWhenCdcIsRunning()
    #getNum(res)
    restartCdcCluster()
    res = kunlunToMysql().killTargetMysqlWhenCdcIsRunning()
    getNum(res)
    restartCdcCluster()
    res = kunlunToMysql().killSourceKunlunWhenCdcIsRunning()
    getNum(res)

if __name__ == '__main__':
    copyconfig.Mode('regular')
    #copyconfig.Mode('regular')
    mysqlToKlustron()
    kunlunToMysql()
    totalCaseNum = len(succ) + len(fail)
    print('======== 测试结果 ========')
    if totalCaseNum == len(succ):
        writeLog('所有测试成功')
        res = 0
    else:
        writeLog('有%s条测试失败' % (len(fail)))
        res = 1
    print('当前的成功项：%s' % succ)
    print('当前的失败项: %s' % fail)
    print('======== 测试结果 ========')
    exit(res)
