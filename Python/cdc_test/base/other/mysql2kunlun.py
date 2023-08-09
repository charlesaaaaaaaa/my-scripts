from base.srcTable import klustron
from base.connection import *
from base.api.get import *
from base.api.addDump import post
import subprocess
from base.other.otherOpt import *
from time import sleep
from base.getconf import readcnf
import threading

class fullSync_mysqlToKunlun():
    def __init__(self, dbname):
        self.configDbInfo = readcnf().getConfigDbInfo()
        self.db = dbname
        self.tableName = getMysqlTableName(self.db)

    def getApp(self):
        rmApp = 'rm -rf mydumper ddl2kunlun-linux* && rm -rf mysql2kunlun && mkdir -p mysql2kunlun'
        mydumper = 'wget -q http://zettatech.tpddns.cn:14000/util/main/mydumper > /dev/null 2>&1'
        ddl2kunlun_linux = 'wget -q http://zettatech.tpddns.cn:14000/util/main/ddl2kunlun-linux > /dev/null 2>&1'
        subprocess.run(rmApp, shell=True)
        subprocess.run(mydumper, shell=True)
        subprocess.run(ddl2kunlun_linux, shell=True)
        subprocess.run('chmod 755 ./mydumper ./ddl2kunlun-linux', shell=True)
        subprocess.run('rm -rf wget-log*', shell=True)

    def sysbenchAction(self, action, tables, tableSize):
        mysqlInfo = self.configDbInfo['mysql']
        db = self.db
        if action == 'prepare':
            command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=mysql --mysql-host=%s --mysql-port=%s' \
                                      ' --mysql-user=%s --mysql-password=%s --mysql-db=%s prepare\n' % (tables, tableSize, mysqlInfo['host'], mysqlInfo['port'], mysqlInfo['user'], mysqlInfo['password'], db)
            writeLog('开始灌sysbench数据\n\t' + command)
        elif action == 'cleanup':
            command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=mysql --mysql-host=%s --mysql-port=%s' \
                                      ' --mysql-user=%s --mysql-password=%s --mysql-db=%s cleanup\n' % (tables, tableSize, mysqlInfo['host'], mysqlInfo['port'], mysqlInfo['user'], mysqlInfo['password'], db)
            writeLog('开始清除sysbench数据\n\t' + command)
        elif action == 'run':
            command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=mysql --mysql-host=%s --mysql-port=%s' \
                                  ' --mysql-user=%s --mysql-password=%s --mysql-db=%s run\n' % (tables, tableSize, mysqlInfo['host'], mysqlInfo['port'], mysqlInfo['user'], mysqlInfo['password'], db)
            writeLog('开始sysbench压测\n\t' + command)
        subprocess.run(command, shell=True)
        if action == 'prepare':
            writeLog('sysbench 准备完毕')

    def startMydumper(self):
        db = self.db
        tableName = self.tableName
        self.tableList = tableName
        tableList = self.tableList
        writeLog('table_name= %s' % tableList)
        fullSync_mysqlToKunlun(db).sysbenchAction('cleanup', 2, 10)
        writeLog('休眠60s，待shard备机与主机同步数据完成')
        sleep(60)
        mysqlInfo = self.configDbInfo['mysql']
        command_start_mydumper = './mydumper -h %s -u %s -p %s -P %s -B %s -o ./mysql2kunlun/%s\n' % (mysqlInfo['host'], mysqlInfo['user'], mysqlInfo['password'], mysqlInfo['port'], db, db)
        writeLog('开始运行mydumper\n\t' + command_start_mydumper)
        subprocess.run(command_start_mydumper, shell=True)
        return tableList

    def getBinlogPosition(self):
        db = self.db
        fileContent = readFile('./mysql2kunlun/%s/metadata' % db)
        Log = fileContent.splitlines()[2].split(': ')[1]
        Pos = fileContent.splitlines()[3].split(': ')[1]
        Gtid= fileContent.splitlines()[4].split('GTID:')[1]
        binlog_dict = {'Log': Log, 'Pos': Pos, 'Gtid': Gtid}
        writeLog('当前binlog信息为：%s' % (str(binlog_dict)))
        return binlog_dict

    def startapi(self, tableList):
        configDbInfo = self.configDbInfo
        db = self.db
        binlog_dict = fullSync_mysqlToKunlun(db).getBinlogPosition()
        comp_mysql_protocol_port = klustron.info().metadata()['mysql_protocol_port']
        cdcInfo = readcnf().getCdcInfo()
        try:
            res = post().src_mysql(configDbInfo, binlog_dict, tableList, cdcInfo, comp_mysql_protocol_port)
            writeLog(res)
        except Exception as err:
            writeLog(str(err))

    def reviewDataNum(self):
        db = self.db
        writeLog('休眠60s，等待上下游同步完成')
        sleep(60)
        writeLog('开始检查数据量是否一致\n')
        tableName = self.tableName.split(',')
        doneOrNot = 1
        while doneOrNot != 0:
            doneOrNot = len(tableName)
            for i in tableName:
                sql = 'select count(*) from %s' % i.split('.')[1]
                pgsql = 'set search_path to %s; %s' % (db, sql)
                myRes = connMy().myReturn(db, sql)
                pgRes = connPg().pgReturn('postgres', pgsql)
                try:
                    if myRes[0][0] != pgRes[0][0]:
                        writeLog('%s 数据量上下游不一致: %s -- %s %s\n\t%s\n' % (i, myRes, pgRes, doneOrNot,pgsql))
                    else:
                        doneOrNot -= 1
                except Exception as err:
                    writeLog('无法比对当前上游 %s 及 下游 %s 数据\n\t' % (myRes, pgRes)+ str(err) + '\n')
            sleep(5)
        writeLog('上下游所有表数据量一致\n')

    def reviewAllTable(self):
        writeLog('开始检查所有表数据是否一致\n')
        tableName = self.tableName.split(',')
        db = self.db
        doneOrNot = 0
        for i in range(10):
            doneOrNot = 0
            for ii in tableName:
                sql = 'select * from %s order by id' % ii.split('.')[1]
                pgsql = 'set search_path to %s; %s' % (db, sql)
                myRes = str(list(connMy().myReturn(db, sql))).replace(' ', '')
                pgRes = str(connPg().pgReturn('postgres', pgsql)).replace(' ', '')
                if pgRes != myRes:
                    doneOrNot = 1
                    writeLog('当前%s表不一致，继续检查\n' % ii)
                    writeFile('pg', pgRes)
                    writeFile('my', myRes)
            if doneOrNot == 0:
                writeLog('当前检查所有表上下游一致，通过\n')
                break
            sleep(10)
        if doneOrNot == 1:
            writeLog('failure: 10次检查皆失败，该用例不通过\n')

    def reviewDataRow(self):
        db = self.db
        tableName = self.tableName.split(',')
        whileNum = 0
        sleep(5)
        writeLog('当下游任意表数据量大于源表2分之一时，开始进行下一步')
        # 当任意下游表的数据量小于源表但大于源表3分之一时，进行下一步
        while whileNum == 0:
            for i in tableName:
                sql = 'select count(*) from %s' % i.split('.')[1]
                pgsql = 'set search_path to %s; %s' % (db, sql)
                try:
                    myRes = connMy().myReturn(db, sql)
                    pgRes = connPg().pgReturn('postgres', pgsql)
                    if pgRes[0][0] > int(myRes[0][0] / 2) and pgRes[0][0] <= myRes[0][0]:
                        whileNum = 1
                        break
                except:
                    try:
                        writeLog('对比结果失败 mysql:%s pg:%s' % (myRes, pgRes))
                    except Exception as err:
                        writeLog(str(err))
            sleep(1)

    def killCdc(self):
        db = self.db
        fullSync_mysqlToKunlun(db).reviewDataRow()
        cdcInfo = leader().info()
        cdcUser = readcnf().getCdcInfo()['user']
        cdcMasterHost = cdcInfo.split(':')[0]
        command_killcdc = "ssh %s@%s \"ps -ef | grep cdc | grep -v cdc_test.py | awk '{print \$2}' | xargs kill -9\""% (cdcUser, cdcMasterHost)
        writeLog('找到cdc主为%s, 存在kill主\n%s' % (cdcInfo, command_killcdc))
        subprocess.run(command_killcdc, shell=True)
        writeLog('开始进行下一步')

    def killSourceMysql(self):
        db=self.db
        fullSync_mysqlToKunlun(db).reviewDataRow()
        configDbInfo = self.configDbInfo
        mysqlHost = configDbInfo['mysql']['host']
        mysqlUser = configDbInfo['mysql']['user']
        mysqlpwd = configDbInfo['mysql']['password']
        sockFile = configDbInfo['mysql']['sockfile']
        linuxUserForStartMysql = configDbInfo['mysql']['linuxuserforstartmysql']
        mysqladmin = configDbInfo['mysql']['basedir'] + '/bin/mysqladmin'
        mysqld_safe = configDbInfo['mysql']['basedir'] + '/bin/mysqld_safe'
        defaults_configFile = configDbInfo['mysql']['defaults_configfile']
        command_stopmysql = "ssh %s@%s '%s -u%s -p%s -S %s shutdown'" % (linuxUserForStartMysql, mysqlHost, mysqladmin, mysqlUser, mysqlpwd, sockFile)
        writeLog('现在停止上游mysql并等待25秒\n\t%s\n'% command_stopmysql)
        subprocess.run(command_stopmysql, shell=True)
        sleep(25)
        command_startmysql = "ssh %s@%s 'nohup %s --defaults-file=%s --user=%s &'" % (
            linuxUserForStartMysql, mysqlHost, mysqld_safe, defaults_configFile, linuxUserForStartMysql)
        writeLog('现在开启mysql并等待10秒\n\t%s\n' % command_startmysql)
        startMysql = subprocess.Popen(command_startmysql, shell=True)
        sleep(10)
        startMysql.terminate()
        writeLog('开始进行下一步')

    def killTargetKlustron(self):
        db = self.db
        fullSync_mysqlToKunlun(db).reviewDataRow()
        clusterInfo = klustron.info().clusterInfo()
        cdcUser = readcnf().getCdcInfo()['user']
        times = 1
        writeLog('正在kill掉klustron对应分片的备节点。。。\n')
        for i in range(100):
            for i in clusterInfo:
                if i == 'metadata':
                    continue
                else:
                    klustronHost = clusterInfo[i]['host']
                    klustronPort = clusterInfo[i]['port']
                    command_killklutron = 'ssh %s@%s "ps -ef | grep %s | grep mysql | awk \'{print \$2}\'"' % (cdcUser, klustronHost, klustronPort)
                    if times > len(clusterInfo):
                        writeLog(command_killklutron)
                    subprocess.run(command_killklutron, shell=True)
        writeLog('开始进行下一步')