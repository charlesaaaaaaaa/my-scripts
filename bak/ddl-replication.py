from time import sleep
import json
import argparse
import psycopg2
import subprocess
import filecmp

def readJsonFile():
    Comp = open(File,encoding = 'utf-8')
    CompLoad = json.loads(Comp.read())
    totalComp = CompLoad['cluster']['comp']['nodes']
    c = 0
    
    global ip
    global port
    global sip 
    global sport
    global user
    global name
    global pwd
    
    ip = []
    port = []
    user = []
    name = []
    pwd = []
    
    for i in totalComp:
        CompIp = i['ip']
        CompPort = i['port']
        CompUser = i['user']
        CompName = i['name']
        CompPwd = i['password']
        ip.append(CompIp)
        port.append(CompPort)
        user.append(CompUser)
        name.append(CompName)
        pwd.append(CompPwd)
    sip = ', '.join(ip)
    sport = str(port)
    #print('ip=[' + sip + ']')
    #print('port=' + sport)
    return(ip, port, sip, sport)

def createDbAndConnect():
    num = 0
    for i in ip:
        dbnum = num + 1
        conn = psycopg2.connect(database = 'postgres', user = user[num], host = ip[num], port = port[num], password = pwd[num] )
        cur = conn.cursor()
        conn.autocommit = True
        dbname="t%i" % (dbnum)
        CreateDb="""
            CREATE DATABASE {};
            """ .format(dbname)
        cur.execute(CreateDb)
        print('create Database {} success!' .format(dbname))
        cur.close()
        conn.close()

        conn = psycopg2.connect(database = dbname, user = user[num], host = ip[num], port = port[num], password = pwd[num] )
        print('connect database {} success!' .format(dbname))
        conn.close()
        sleep(3)
        num += 1

def PrepareTpccAndRunTpcc5Second():
    bak = 'cp ../Tools/sysbench-tpcc/tpcc.lua ../Tools/sysbench-tpcc/tpcc.luabak'
    path = 'path=`cd ../Tools/sysbench-tpcc/ && pwd`'
    bak2 = 'cp $path/prepare.sh $path/prepare.shbak && cp $path/tpcc_common.lua $path/tpcc_common.luabak && cp $path/run.sh $path/run.shbak'
    inTc = 'sed -i "s/sleep(30)/--sleep(30)/" $path/tpcc_common.lua && sed -i "s@./tpcc.lua@$path/tpcc.lua@" $path/prepare.sh && sed -i "s@./tpcc.lua@$path/tpcc.lua@" $path/run.sh'
    lineTp = 'sed -i "' + '20i package.path =\\"$path/tpcc_common.lua\\"..\\";..\\\\?.lua\\"' + '" ../Tools/sysbench-tpcc/tpcc.lua'
    line = "%s && %s && %s && %s && %s " % (path, bak ,bak2, inTc, lineTp)
    subprocess.run(line, shell=True)

    num = 0
    for i in ip:
        dbnum = num + 1
        print('======== run TPCC on %s:%s ========' % (i, port[num]))
        runLine = "bash ../Tools/sysbench-tpcc/prepare.sh %s %s t%d %s %s 1 1 1 5 > log.log &" % (i, port[num], dbnum, user[num], pwd[num])
        subprocess.run(runLine, shell = True)
        sleep(55)
        subprocess.run('bash ../Tools/sysbench-tpcc/run.sh 1 > log.log & ', shell = True)
        sleep(5)
        num += 1

    filebak='mv ../Tools/sysbench-tpcc/prepare.shbak ../Tools/sysbench-tpcc/prepare.sh && mv ../Tools/sysbench-tpcc/tpcc_common.luabak ../Tools/sysbench-tpcc/tpcc_common.lua && mv ../Tools/sysbench-tpcc/tpcc.luabak ../Tools/sysbench-tpcc/tpcc.lua && mv ../Tools/sysbench-tpcc/run.shbak mv ../Tools/sysbench-tpcc/run.sh && rm log.log '
    subprocess.run(filebak, shell = True)

def checkAllSystemTable():
    sysTabName = ["pg_proc","pg_namespace","pg_index","pg_cluster_meta_nodes"]
    num = 0
    subprocess.run('mkdir -p ./ddl-diff', shell = True)
    for a in ip: #generate tmp file
        for i in range(4):
            conn=psycopg2.connect(database = 'postgres', user = user[num], host = ip[num], port = port[num], password = pwd[num])
            cur=conn.cursor();
            sysTab=sysTabName[i]
            execStmt = "select * from %s" % (sysTab)
            cur.execute(execStmt)
            result = str(cur.fetchall())
            result_log = result.replace(')',')\n')

            with open("./ddl-diff/%s%s" %(sysTab, num), 'w') as f:
                f.write(result_log)
            cur.close()
            conn.close()
        num += 1

    num = 0
    for i in ip: #check tmp file
        for i in range(5):
            pass
            

def cheakAllCnsHasTpccRows():
    TpccTabName = ['history1', 'customer1', 'district1', 'item1', 'order_line1', 'orders1', 'stock1','warehouse1']
    num = 0
    dbnum = 1 
    for i in ip:
        for a in TpccTabName:
            db = "t%d" % (dbnum)
            conn = psycopg2.connect(database = db, user = user[num], host = i, port = port[num], password = pwd[num])
            cur = conn.cursor();
            execStmt = "select * from %s limit 1" % (a)
            cur.execute(execStmt)
            print("\n======== check" + i + ':' + str(port[num]) + '/' + db + ' table:' + a + " success ========" )
            print(cur.fetchall())
            cur.close()
            conn.close()
        num += 1
        dbnum += 1



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'this script is use to test ddl replication!')
    parser.add_argument('--config', type=str, default = 'install.json', help = 'the configuration file of Kunlun_Cluster')
    args = parser.parse_args()
    File = args.config
    readJsonFile()
    print('ip=[' + sip + ']\n' + 'port=' + sport + '\npwd= ' + pwd[0])
    #createDbAndConnect()
    #PrepareTpccAndRunTpcc5Second()
    cheakAllCnsHasTpccRows()
    checkAllSystemTable()
