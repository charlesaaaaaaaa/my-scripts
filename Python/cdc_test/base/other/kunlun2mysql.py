from base.srcTable.klustron import info
import subprocess
from base.other.otherOpt import *
from base.getconf import readcnf
from base.api.get import *
from base.srcTable import klustron
from base.api import addDump
from base.connection import *
from time import sleep

class fullSync_kunlunToMysql():
    def __init__(self, dbname):
        self.configDbInfo = readcnf().getConfigDbInfo()
        self.db = dbname
        self.tableName = getKlustronTableName(self.db)

    def getApp(self):
        rmApp = 'rm -rf mydumper ddl2kunlun-linux* && rm -rf kunlun2mysql && mkdir -p kunlun2mysql'
        mydumper = 'wget -q http://zettatech.tpddns.cn:14000/util/main/mydumper > /dev/null 2>&1'
        ddl2kunlun_linux = 'wget -q http://zettatech.tpddns.cn:14000/util/main/ddl2kunlun-linux > /dev/null 2>&1'
        subprocess.run(rmApp, shell=True)
        subprocess.run(mydumper, shell=True)
        subprocess.run(ddl2kunlun_linux, shell=True)
        subprocess.run('chmod 755 ./mydumper ./ddl2kunlun-linux', shell=True)
        subprocess.run('rm -rf wget-log*', shell=True)

    def sysbenchAction(self, action, tables, tableSize):
        klustronInfo = self.configDbInfo['klustron']
        db = self.db
        if action == 'prepare':
            command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=pgsql --pgsql-host=%s --pgsql-port=%s' \
                                      ' --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s prepare\n' % (tables, tableSize, klustronInfo['host'], klustronInfo['port'], klustronInfo['user'], klustronInfo['password'], db)
            writeLog('开始灌sysbench数据\n\t' + command)
        elif action == 'cleanup':
            command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=pgsql --pgsql-host=%s --pgsql-port=%s' \
                      ' --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s cleanup\n' % (
                      tables, tableSize, klustronInfo['host'], klustronInfo['port'], klustronInfo['user'], klustronInfo['password'], db)
            writeLog('开始清除sysbench数据\n\t' + command)
        elif action == 'run':
            command = command = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=pgsql --pgsql-host=%s --pgsql-port=%s' \
                                      ' --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s run\n' % (tables, tableSize, klustronInfo['host'], klustronInfo['port'], klustronInfo['user'], klustronInfo['password'], db)
            writeLog('开始sysbench压测\n\t' + command)
        subprocess.run(command, shell=True)
        if action == 'prepare':
            writeLog('sysbench 准备完毕')

    def getStorageDict(self):
        clusterInfo = klustron.info().clusterInfo()
        storageDict = {}
        for i in clusterInfo:
            if i == 'metadata':
                continue
            else:
                tmpdict = {'host': clusterInfo[i]['host'], 'port': clusterInfo[i]['port'], 'user': clusterInfo[i]['user'], 'password': clusterInfo[i]['password']}
                shardDict = {i: tmpdict}
                storageDict.update(shardDict)
        return storageDict

    def startMydumper(self):
        db = self.db
        tableList = self.tableName
        storageDict = fullSync_kunlunToMysql(db).getStorageDict()
        fullSync_kunlunToMysql(db).sysbenchAction('cleanup', 2, 10)
        for i in storageDict:
            command_start_mydumper = './mydumper -h %s -u %s -p %s -P %s -B %s_\$\$_public -o ./kunlun2mysql/%s_%s\n' % (storageDict[i]['host'], storageDict[i]['user'], storageDict[i]['password'],storageDict[i]['port'], db, db, i)
            writeLog('开始运行mydumper\n\t' + command_start_mydumper)
            subprocess.run(command_start_mydumper, shell=True)
        return tableList

    def get_shard_params(self):
        db = self.db
        shard_params = {}
        storageDict = fullSync_kunlunToMysql(db).getStorageDict()
        for i in storageDict:
            shradId = i.split('_')[1]
            command_mkdir = './kunlun2mysql/%s_%s' % (db, i)
            fileContent = readFile('%s/metadata' % (command_mkdir))
            Log = fileContent.splitlines()[8].split(': ')[1]
            Pos = fileContent.splitlines()[9].split(': ')[1]
            Gtid= fileContent.splitlines()[10].split('GTID:')[1]
            tmpdict = {"shard_id": shradId, "dump_hostaddr": storageDict[i]['host'], "dump_port": str(storageDict[i]['port']), "binlog_file": Log, "binlog_pos": Pos, "gtid_set": Gtid}
            shardDict = {i: tmpdict}
            shard_params.update(shardDict)
        return shard_params

    def startApi(self, tableList):
        db = self.db
        shard_params = fullSync_kunlunToMysql(db).get_shard_params()
        writeLog('等待30s，等kunlun主备同步完成')
        sleep(30)
        addDump.post().src_klustron(tableList, shard_params)

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
                mysqlDatabase = i.split('.')[0]
                pgsql = 'select count(*) from %s' % i.split('.')[1]
                mysql = 'select count(*) from %s' % i.split('.')[1]
                myRes = connMy().myReturn(mysqlDatabase, mysql)
                pgRes = connPg().pgReturn(db, pgsql)
                try:
                    if myRes[0][0] != pgRes[0][0]:
                        writeLog('%s 数据量上下游不一致: %s -- %s %s\n\t%s\n' % (i, myRes, pgRes, doneOrNot, pgsql))
                    else:
                        doneOrNot -= 1
                except Exception as err:
                    writeLog('无法比对当前上游 %s 及 下游 %s 数据\n\t' % (myRes, pgRes) + str(err) + '\n')
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
                mysql = 'select * from %s order by id' % ii.split('.')[1]
                pgsql = 'select * from %s order by id' % (ii.split('.')[1])
                myres = connMy().myReturn('%s' % ii.split('.')[0], mysql)
                pgres = connPg().pgReturn(db, pgsql)
                if myres == -1:
                    writeLog('当前获取下游mysql出错，请检查对应数据库\n%s' % mysql)
                    sleep(10)
                    continue
                myRes = str(list(myres)).replace(' ', '')
                pgRes = str(pgres).replace(' ', '')
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
                pgsql = 'select count(*) from %s' % i.split('.')[1]
                mysql = 'select count(*) from %s' % i.split('.')[1]
                try:
                    myRes = connMy().myReturn(db, mysql)
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
        fullSync_kunlunToMysql(db).reviewDataRow()
        cdcInfo = leader().info()
        cdcUser = readcnf().getCdcInfo()['user']
        cdcMasterHost = cdcInfo.split(':')[0]
        command_killcdc = "ssh %s@%s \"ps -ef | grep cdc | grep -v cdc_test.py | awk '{print \$2}' | xargs kill -9\""% (cdcUser, cdcMasterHost)
        writeLog('找到cdc主为%s, 存在kill主\n%s' % (cdcInfo, command_killcdc))
        subprocess.run(command_killcdc, shell=True)
        writeLog('开始进行下一步')

    def killTargetMysql(self):
        db=self.db
        fullSync_kunlunToMysql(db).reviewDataRow()
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

    def killSourceKlustron(self):
        db = self.db
        fullSync_kunlunToMysql(db).reviewDataRow()
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

#print(fullSync_kunlunToMysql('kunluntomysql').startApi())
