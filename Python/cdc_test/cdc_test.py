# -*- coding: utf-8 -*-
from base.other import copyconfig

def mysqlToKlustron():
    from base import test
    from base.other.otherOpt import restartCdcCluster
    restartCdcCluster()
    test.mysqlToKunlun().regular_test()
    test.mysqlToKunlun().killCdcMasterWhenCdcIsRunning()
    test.mysqlToKunlun().killSourceMysqlWhenCdcIsRunning()
    test.mysqlToKunlun().killTargeKlustronWherCdcIsRunning()

def kunlunToMysql():
    from base.test import kunlunToMysql
    from base.other.otherOpt import restartCdcCluster
    restartCdcCluster()
    kunlunToMysql().regular_test()
    kunlunToMysql().killCdcMasterWhenCdcIsRunning()
    kunlunToMysql().killTargetMysqlWhenCdcIsRunning()
    kunlunToMysql().killSourceKunlunWhenCdcIsRunning()

if __name__ == '__main__':
    copyconfig.Mode('regular')
    #copyconfig.Mode('regular')
    mysqlToKlustron()
    kunlunToMysql()
