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
    getNum(test.mysqlToKunlun().regular_test())
    restartCdcCluster()
    getNum(test.mysqlToKunlun().killSourceMysqlWhenCdcIsRunning())
    restartCdcCluster()
    getNum(test.mysqlToKunlun().killTargeKlustronWherCdcIsRunning())
    restartCdcCluster()
    getNum(test.mysqlToKunlun().killShardMasterWhenCdcIsRunning())
    restartCdcCluster()
    getNum(test.mysqlToKunlun().killCdcMasterWhenCdcIsRunning())

def kunlunToMysql():
    from base.test import kunlunToMysql
    from base.other.otherOpt import restartCdcCluster
    restartCdcCluster()
    getNum(kunlunToMysql().regular_test())
    restartCdcCluster()
    getNum(kunlunToMysql().killTargetMysqlWhenCdcIsRunning())
    restartCdcCluster()
    getNum(kunlunToMysql().killSourceKunlunWhenCdcIsRunning())
    restartCdcCluster()
    getNum(kunlunToMysql().killShardMasterWhenCdcIsRunning())
    restartCdcCluster()
    getNum(kunlunToMysql().killCdcMasterWhenCdcIsRunning())

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
