import subprocess
from time import sleep
from base.getconf import readcnf
from base.connection import connPg, connMy
from base.getconf import readcnf
import time

def writeFile(file, content):
    with open(file, 'a') as f:
        f.write(content)

def readFile(file):
    with open(file, 'r') as f:
        content = f.read()
    return content

def readFileLine(file, line):
    with open(file, 'r') as f:
        content = f.readline(line)
    return content

def writeLog(content):
    Today = time.strftime("%Y-%m-%d")
    logName = 'log-%s.log' % Today
    nowTime = time.asctime(time.localtime(time.time())) + ' '
    content = '\n' + nowTime + content
    with open('.location.txt', 'r') as fi:
        logPath = fi.readlines()[1].split('=')[1]
    fi.close()
    filePath = logPath.replace('file', logName)
    with open(filePath, 'a') as f:
        f.write(content)
    f.close()

def getMysqlTableName(database):
    sql = 'show tables'
    tables = connMy().myReturn(database, sql)
    tableList = ''
    for i in tables:
        db_tableName = '%s.%s' % (database, i[0])
        if tableList == '':
            tableList = db_tableName
        else:
            tableList = tableList + ',' + db_tableName
    #writeLog('当前所有源表为：%s' % tableList)
    return tableList

def getKlustronTableName(database):
    sql = "select tablename from pg_tables where schemaname = 'public'"
    tableList = ''
    tables = connPg().pgReturn(database, sql)
    for i in tables:
        db_tableName = '%s_$$_public.%s' % (database, i[0])
        if tableList == '':
            tableList = db_tableName
        else:
            tableList = tableList + ',' + db_tableName
    return tableList

def restartCdcCluster():
    cdcInfo = readcnf().getCdcInfo()
    host = list(cdcInfo['host'].replace(' ', '').split(','))
    cdcUser = cdcInfo['user']
    startCdc = cdcInfo['base'] + '/bin && bash start_kunlun_cdc.sh'
    stopCdc = cdcInfo['base'] + '/bin && bash stop_kunlun_cdc.sh'
    rmCdcData = cdcInfo['base'] + '/data && rm -rf *'
    for i in range(int(cdcInfo['nodenum'])):
        command_stopCdc = 'ssh %s@%s "cd %s"' % (cdcUser, host[i], stopCdc)
        subprocess.Popen(command_stopCdc, shell=True)
    sleep(2)
    for i in range(int(cdcInfo['nodenum'])):
        command_rmCdcData = 'ssh %s@%s "cd %s"' % (cdcUser, host[i], rmCdcData)
        subprocess.Popen(command_rmCdcData, shell=True)
    for i in range(int(cdcInfo['nodenum'])):
        command_startCdc = 'ssh %s@%s "cd %s"' % (cdcUser, host[i], startCdc)
        subprocess.Popen(command_startCdc, shell=True)

# print(getKlustronTableName('kunluntomysql'))