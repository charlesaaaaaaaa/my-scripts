from base.other.mysql2kunlun import fullSync_mysqlToKunlun
from base.other.kunlun2mysql import fullSync_kunlunToMysql
from base.connection import *
from time import sleep

class mysqlToKunlun():
    def __init__(self):
        pass

    def createDatabase(self, dbname):
        drop = 'drop database if exists %s' % (dbname)
        pgdrop = 'drop schema if exists %s CASCADE' % (dbname)
        sql = 'create database if not exists %s' % (dbname)
        pgsql = 'create schema if not exists %s' % (dbname)
        connMy().myNotReturn('mysql', drop)
        connPg().pgNotReturn('postgres', pgdrop)
        connMy().myNotReturn('mysql', sql)
        connPg().pgNotReturn('postgres', pgsql)

    def regular_test(self):
        # 获取app -- 清理sysbench数据（如果有的话）-- sysbench prepare -- 开启mydumper /
        # 获取binlog位置信息 -- 启动api -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'mysqltokunlun'
        mysqlToKunlun().createDatabase(dbname)
        fullSync_mysqlToKunlun(dbname).getApp()
        fullSync_mysqlToKunlun(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_mysqlToKunlun(dbname).startMydumper()
        fullSync_mysqlToKunlun(dbname).getBinlogPosition()
        #startMydumper里面已经存在cleanup动作了，所以不用再cleanup了
        fullSync_mysqlToKunlun(dbname).startapi(tableList)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_mysqlToKunlun(dbname).reviewDataNum()
        res = fullSync_mysqlToKunlun(dbname).reviewAllTable()
        return res

    def killCdcMasterWhenCdcIsRunning(self):
        # 清理sysbench数据（如果有的话）-- sysbench prepare -- 开启mydumper -- 获取binlog位置信息
        # 启动api -- kill掉主cdc -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'mysqltokunlun_killcdc'
        mysqlToKunlun().createDatabase(dbname)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_mysqlToKunlun(dbname).startMydumper()
        fullSync_mysqlToKunlun(dbname).getBinlogPosition()
        fullSync_mysqlToKunlun(dbname).startapi(tableList)
        # startMydumper里面已经存在cleanup动作了，所以不用再cleanup了
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_mysqlToKunlun(dbname).killCdc()
        fullSync_mysqlToKunlun(dbname).reviewDataNum()
        res = fullSync_mysqlToKunlun(dbname).reviewAllTable()
        return res

    def killSourceMysqlWhenCdcIsRunning(self):
        # 清理sysbench数据（如果有的话）-- sysbench prepare -- 开启mydumper -- 获取binlog位置信息
        # 启动api -- kill掉源mysql -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'mysqltokunlun_killmysql'
        mysqlToKunlun().createDatabase(dbname)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_mysqlToKunlun(dbname).startMydumper()
        fullSync_mysqlToKunlun(dbname).getBinlogPosition()
        fullSync_mysqlToKunlun(dbname).startapi(tableList)
        # startMydumper里面已经存在cleanup动作了，所以不用再cleanup了
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_mysqlToKunlun(dbname).killSourceMysql()
        fullSync_mysqlToKunlun(dbname).reviewDataNum()
        res = fullSync_mysqlToKunlun(dbname).reviewAllTable()
        return res

    def killTargeKlustronWherCdcIsRunning(self):
        # 清理sysbench数据（如果有的话）-- sysbench prepare -- 开启mydumper -- 获取binlog位置信息
        # 启动api -- kill掉下游klustron的分片备节点-- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'mysqltokunlun_killklustron'
        mysqlToKunlun().createDatabase(dbname)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_mysqlToKunlun(dbname).startMydumper()
        fullSync_mysqlToKunlun(dbname).getBinlogPosition()
        fullSync_mysqlToKunlun(dbname).startapi(tableList)
        # startMydumper里面已经存在cleanup动作了，所以不用再cleanup了
        fullSync_mysqlToKunlun(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_mysqlToKunlun(dbname).killTargetKlustron()
        fullSync_mysqlToKunlun(dbname).reviewDataNum()
        res = fullSync_mysqlToKunlun(dbname).reviewAllTable()
        return res

class kunlunToMysql():
    def __init__(self):
        pass

    def createDatabase(self, dbname):
        drop = 'drop database if exists %s_$$_public' % (dbname)
        pgdrop = 'drop database if exists %s' % (dbname)
        sql = 'create database if not exists %s_$$_public' % (dbname)
        pgsql = 'create database if not exists %s' % (dbname)
        connMy().myNotReturn('mysql', drop)
        connPg().pgNotReturn('postgres', pgdrop)
        connMy().myNotReturn('mysql', sql)
        connPg().pgNotReturn('postgres', pgsql)

    def regular_test(self):
        # 获取app -- 清理sysbench数据（如果有的话）-- sysbench prepare /
        # 开启mydumper -- 启动api -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'kunluntomysql'
        kunlunToMysql().createDatabase(dbname)
        fullSync_kunlunToMysql(dbname).getApp()
        fullSync_kunlunToMysql(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_kunlunToMysql(dbname).startMydumper()
        fullSync_kunlunToMysql(dbname).startApi(tableList)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_kunlunToMysql(dbname).reviewDataNum()
        res = fullSync_kunlunToMysql(dbname).reviewAllTable()
        return res

    def killCdcMasterWhenCdcIsRunning(self):
        # 获取app -- 清理sysbench数据（如果有的话）-- sysbench prepare /
        # 开启mydumper -- 启动api -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'kunluntomysql'
        kunlunToMysql().createDatabase(dbname)
        fullSync_kunlunToMysql(dbname).getApp()
        fullSync_kunlunToMysql(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_kunlunToMysql(dbname).startMydumper()
        fullSync_kunlunToMysql(dbname).startApi(tableList)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_kunlunToMysql(dbname).killCdc()
        fullSync_kunlunToMysql(dbname).reviewDataNum()
        res = fullSync_kunlunToMysql(dbname).reviewAllTable()
        return res

    def killTargetMysqlWhenCdcIsRunning(self):
        # 获取app -- 清理sysbench数据（如果有的话）-- sysbench prepare /
        # 开启mydumper -- 启动api -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'kunluntomysql'
        kunlunToMysql().createDatabase(dbname)
        fullSync_kunlunToMysql(dbname).getApp()
        fullSync_kunlunToMysql(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_kunlunToMysql(dbname).startMydumper()
        fullSync_kunlunToMysql(dbname).startApi(tableList)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_kunlunToMysql(dbname).killTargetMysql()
        fullSync_kunlunToMysql(dbname).reviewDataNum()
        res = fullSync_kunlunToMysql(dbname).reviewAllTable()
        return res

    def killSourceKunlunWhenCdcIsRunning(self):
        # 获取app -- 清理sysbench数据（如果有的话）-- sysbench prepare /
        # 开启mydumper -- 启动api -- 等待60s -- 检查数据总量 -- 检查所有表是否一致
        dbname = 'kunluntomysql'
        kunlunToMysql().createDatabase(dbname)
        fullSync_kunlunToMysql(dbname).getApp()
        fullSync_kunlunToMysql(dbname).sysbenchAction('cleanup', 2, 10)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10)
        tableList = fullSync_kunlunToMysql(dbname).startMydumper()
        fullSync_kunlunToMysql(dbname).startApi(tableList)
        fullSync_kunlunToMysql(dbname).sysbenchAction('prepare', 2, 10000)
        fullSync_kunlunToMysql(dbname).killSourceKlustron()
        fullSync_kunlunToMysql(dbname).reviewDataNum()
        res = fullSync_kunlunToMysql(dbname).reviewAllTable()
        return res