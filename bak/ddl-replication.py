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

    
    for a in range(4): #check tmp file
        num = 0
        tbName = sysTabName[a]
        print("\n======== " + tbName + " ========\n")
        for i in Cns:

            if i == Cns[-1]:
                pass
            else:
                diff = filecmp.cmp("./ddl-diff/%s%d" %(tbName, num), "./ddl-diff/%s%d" %(tbName, num + 1))
                if diff :
                    print(Cns[num] + 'is the same ' + tbName + ' as ' + Cns[num + 1] + " , success")
                else:
                    print(Cns[num] + 'is not the same ' + tbName + ' as ' + Cns[num + 1] + " , failure")
            num += 1

    num = 0
    dbnum = 1
    for i in ip:
        conn=psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        conn.autocommit = True
        cur=conn.cursor()
        execStmt1 = "select datname  ,encoding ,datcollate, datctype  ,datistemplate ,datallowconn ,datconnlimit ,datlastsysoid ,datfrozenxid ,datminmxid ,dattablespace,datacl from pg_database"
        cur.execute(execStmt1)
        res1 = str(cur.fetchall())
        Res1 = res1.replace(')',')\n')
        cur.close()
        conn.close()

        conn=psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        conn.autocommit = True
        cur=conn.cursor()
        execStmt2 = "select datdba from pg_database where datname = 't%d'" % (dbnum)
        cur.execute(execStmt2)
        res2 = str(cur.fetchall())
        Res2 = res2.replace(')',')\n')
        cur.close()
        conn.close()

        res = "%s \n %s" % (Res2, Res1)
        with open("./ddl-diff/pg_database%d" % (num),"w") as f:
            f.write(res)

        num += 1
        dbnum += 1

    print("\n======== pg_database ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/pg_database%d" %(num), "./ddl-diff/pg_database%d" %(num + 1))
            if diff :
                print(Cns[num] + 'is the same pg_database as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + 'is not the same pg_database as ' + Cns[num + 1] + " , failure")
        num += 1


    num = 0
    for i in ip:
        conn=psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        conn.autocommit = True
        cur=conn.cursor()
        execStmt1 = "select name, id, master_node_id, num_nodes, space_volumn, num_tablets ,db_cluster_id from pg_shard"
        cur.execute(execStmt1)
        res = str(cur.fetchall())
        Res = res1.replace(')',')\n')
        cur.close()
        conn.close()

        with open("./ddl-diff/pg_shard%d" % (num),"w") as f:
            f.write(Res)
        num += 1

    print("\n======== pg_shard_node ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/pg_shard%d" %(num), "./ddl-diff/pg_shard%d" %(num + 1))
            if diff :
                print(Cns[num] + 'is the same pg_shard as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + 'is not the same pg_shard as ' + Cns[num + 1] + " , failure")
        num += 1

    num = 0
    for i in ip:
        conn=psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        conn.autocommit = True
        cur=conn.cursor()
        execStmt1 = "select id, port, shard_id, svr_node_id, ro_weight, user_name,   hostaddr   , passwd from pg_shard_node"
        cur.execute(execStmt1)
        res = str(cur.fetchall())
        Res = res1.replace(')',')\n')
        cur.close()
        conn.close()

        with open("./ddl-diff/pg_shard_node%d" % (num),"w") as f:
            f.write(Res)
        num += 1

    print("\n======== pg_shard ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/pg_shard_node%d" %(num), "./ddl-diff/pg_shard_node%d" %(num + 1))
            if diff :
                print(Cns[num] + 'is the same pg_shard_node as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + 'is not the same pg_shard_node as ' + Cns[num + 1] + " , failure")
        num += 1


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
    global Cns
    Cns = []
    num = 0
    for i in ip:
        Cn="%s:%s" % (i, str(port[num]))
        Cns.append(Cn)
        num += 1
    #print('ip=[' + sip + ']\n' + 'port=' + sport + '\npwd= ' + pwd[0])
    #createDbAndConnect()
    #PrepareTpccAndRunTpcc5Second()
    #cheakAllCnsHasTpccRows()
    checkAllSystemTable()
