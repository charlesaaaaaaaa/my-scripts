import subprocess
from time import sleep
import json
import argparse
import os
import psycopg2
import pymysql

def readJsonFile():
    OpenCluster=open(install, encoding='utf-8')
    ReadCluster=json.loads(OpenCluster.read())

    CompTotal=ReadCluster['cluster']['comp']['nodes']
    global insBin, serDat
    insBin = ReadCluster['instance_binaries']
    serDat = ReadCluster['server_datadir']
        

    # get cluster info
    global CompIp, CompPwd, CompPort, CompDir, CompUser
    
    CompIp, CompPwd, CompPort, CompDir, CompUser = [], [], [], [], []

    for i in CompTotal: # get computing node info
        ip=i['ip']
        port=i['port']
        #datadir=i['datadir']
        user=i['user']
        pwd=i['password']
        CompPwd.append(pwd)
        CompIp.append(ip)
        CompPort.append(port)
        #CompDir.append(datadir)
        CompUser.append(user)

    try:
        OpenConf=open(config,encoding='utf-8') # get computing conf info
        ReadConf=json.loads(OpenConf.read())
    except:
        print="========================================================================"
        print("\n\n%s\n--------- open configuration file %s fail, please check --------\n%s\n" % (printe, config,printe))
    finally:
        pass
    
    global Compkeys, Compvalues, Medakeys, Medavalues, Datakeys, Datavalues

    CompConf=ReadConf['comp'][0] # get data&metadata conf info
    MedaConf=ReadConf['metadata'][0]
    DataConf=ReadConf['storage'][0]

    Compkeys=list(CompConf.keys())
    Compvalues=list(CompConf.values())
    Medakeys=list(MedaConf.keys())
    Medavalues=list(MedaConf.values())
    Datakeys=list(DataConf.keys())
    Datavalues=list(DataConf.values())
    global CompNum, sCompNum, MedaNum, DataNum, compNums
    CompNum=len(Compkeys)
    sCompNum = str(CompNum)
    MedaNum=len(Medakeys)
    DataNum=len(Datakeys)
    compNums = 0
    for i in CompTotal:
        compNums = compNums + 1

    try:
        os.remove('config.sh')
    except:
        pass
    finally:
        pass

def pgconn(host, port, user, pwd, sql):
    global lists
    conn = psycopg2.connect(database = 'postgres', user = user, host = host, port = port, password = pwd)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(sql)
    lists = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

def wFile(stmt):
    of=open('config.sh','a')
    of.write("#%s\n\n" % (stmt))
    of.close()

def WFile(stmt, es):
    of=open('config.sh','a')
    if es == 'y':
        of.write("echo %s\n" % (stmt))
    elif es == 'n':
        of.write('%s\n\n' % (stmt))
        of.write("")
    of.close()

def myconn(host, port, sql):
    global tmpVars
    conn = pymysql.connect(host = host, user = "pgx",port = int(port), password = "pgx_pwd", database = "mysql")
    cursor = conn.cursor()
    cursor.execute(sql)
    tmpVars = cursor.fetchone()
    cursor.close()
    conn.close()

def varPort():
    global port
    port = []
    for row in lists:
        srow = (str(row))
        srow = srow.replace('(','')
        srow = srow.replace(',)','')
        srow = int(srow)
        port.append(srow)

def varHost():
    global host
    host = []
    for row in lists:
        srow = (str(row))
        srow = srow.replace('\'','')
        srow = srow.replace('(','')
        srow = srow.replace(',)','')
        host.append(srow)

def chInfo(stmt):
    stmt = '\n========================================================================\n%s...\n========================================================================\n'% (stmt)
    print(stmt)

def configComp():
    chInfo('setting Computing_nodes')
    # setting computing node ========================================================================
    CIPN = 0
    for i in CompIp:
        for a in range(0, CompNum):
            if Compvalues[a] :
                SCompkeys = ''.join(Compkeys[a])
                SCompvalues = str(Compvalues[a])
                SCompIp = ''.join(CompIp[CIPN])
                SCompPort = str(CompPort[CIPN])
                
                num = 0
                BashStmt = "ssh %s@%s \'echo %s = %s >> %s/%s/postgresql.conf\'" % (defuser, SCompIp, SCompkeys, SCompvalues, serDat, SCompPort)
                num = num + 1

                WFile(BashStmt, 'y')
                WFile(BashStmt, 'n')
            
            else:
                err = 'Computing node' + SCompIp + ':' + SCompPort + 'parameter :"' + SCompkeys + '" values is null'
                print(err)

        stmt = "ssh %s@%s \'%s/%s/kunlun-server-%s/bin/pg_ctl reload -D %s/%s\'" % (defuser, SCompIp, insBin, SCompPort, version, serDat, SCompPort)

        WFile(stmt, 'y')
        WFile(stmt, 'n')
        CIPN+=1

    subprocess.run("bash ./config.sh",shell=True)

def configData():
    #setting Metadata nodes ========================================================================
    chInfo('setting Metadatas')
    n = 0
    for i in Medakeys:
        hostSql = 'select hostaddr from pg_cluster_meta_nodes'
        portSql = 'select port from pg_cluster_meta_nodes'

        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], portSql)
        varPort()
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], hostSql)
        varHost()

        num = 0
        for hosts in host:
            stmt = 'set global %s = %s' % (i, str(Medavalues[n]))
            wf = 'mysql -h %s -P %s -upgx -ppgx_pwd "%s"' % (hosts, port[num], stmt)
            print(wf)
            myconn(hosts, port[num], stmt)
            wFile(wf)
            num = num + 1

        n = n + 1
    
    chInfo('setting Datanodes')
    #setting Datanodes ========================================================================
    n = 0
    for i in Datakeys:
        hostSql = 'select hostaddr from pg_shard_node'
        portSql = 'select port from pg_shard_node'
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], portSql)
        varPort()
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], hostSql)
        varHost()
        num = 0
        for hosts in host:
            stmt = 'set global %s = %s' % (i, str(Datavalues[n])) 
            wf = 'mysql -h %s -P %s -upgx -ppgx_pwd "%s"' % (hosts, port[num], stmt)
            print(wf)
            myconn(hosts, port[num], stmt)
            wFile(wf)

            num = num + 1

        n = n + 1

def Verdata():
    chInfo('check data_nodes')
    n = 0
    for i in Datakeys:
        hostSql = 'select hostaddr from pg_shard_node'
        portSql = 'select port from pg_shard_node'
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], portSql)
        varPort()
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], hostSql)
        varHost()
        num = 0
        sql = "show variables like '%s';" % (i)
        print('========\n' + sql + '\n========')
        
        for hosts in host:
            showKeys = "show variables like '%s' " % (i)
            wf = 'mysql -h %s -P %s -upgx -ppgx_pwd "%s"' % (hosts, port[num], showKeys)
            myconn(hosts, port[num], showKeys)
            print('mysql -h %s -P %s : %s' % (hosts, port[num], tmpVars[1]))
            srcConfigure = str(Datavalues[n])
            dstVariables = str(tmpVars[1])
            if srcConfigure != dstVariables:
                print(srcConfigure != dstVariables)
            num = num + 1

        n = n + 1

    chInfo('check meta_nodes')
    n = 0
    for i in Medakeys:
        hostSql = 'select hostaddr from pg_cluster_meta_nodes'
        portSql = 'select port from pg_cluster_meta_nodes'
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], portSql)
        varPort()
        pgconn(CompIp[0], CompPort[0], CompUser[0], CompPwd[0], hostSql)
        varHost()
        num = 0
        print("========\nshow variables like '%s';\n========" % (i))
        for hosts in host:
            showKeys = "show variables like '%s' " % (i)
            wf = 'mysql -h %s -P %s -upgx -ppgx_pwd "%s"' % (hosts, port[num], showKeys)
            myconn(hosts, port[num], showKeys)
            print('mysql -h %s -P %s : %s' % (hosts, port[num], tmpVars[1]))
            srcConfigure = str(Medavalues[n])
            dstVariables = str(tmpVars[1])
            if srcConfigure != dstVariables:
                print(srcConfigure != dstVariables)
            num = num + 1

        n = n + 1

    #subprocess.run("bash ./config.sh",shell=True)

def Vercomp():
    chInfo('check comp_nodes')
    for i in range(0, compNums):
        print('========\npsql -h %s -p %s -d postgres\n========' % (CompIp[i], CompPort[i]))

        for var in Compkeys:
            sql = 'show %s;' % (var)
            pgconn(CompIp[i], CompPort[i], CompUser[i], CompPwd[i], sql)
            tmpVar = str(lists)
            tmpVar = tmpVar.replace("[('", '')
            tmpVar = tmpVar.replace("',)]", '')
            print('%s = %s' % (var, tmpVar))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Configure')
    parser.add_argument('--defuser', type = str, default = 'kunlun', help = 'User')
    parser.add_argument('--version', type = str, default = '0.9.3', help = 'Version of computer node')
    parser.add_argument('--install', type = str, default = './install.json', help = 'The original configuration file for the Kunlun_cluster')
    parser.add_argument('--config', type = str, default = './configure.json', help = 'the configuration file')
    parser.add_argument('--component', type = str, default = 'all', help = 'all, server, storage')
    args = parser.parse_args()
    print (args)

    defuser = args.defuser
    install = args.install
    config = args.config
    version = args.version
    component = args.component
    readJsonFile()
    if component == 'all':
        configComp()
        configData()
        Verdata()
        Vercomp()
    elif component == 'server':
        configComp()
        Vercomp()
    elif component == 'storage':
        configData()
        Verdata()

    #subprocess.run("bash ./config.sh",shell=True)


