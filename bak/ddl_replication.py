from time import sleep
import json
import argparse
import psycopg2
import subprocess
import filecmp
import linecache

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
    global ids
    
    ip = []
    ids = []
    port = []
    user = []
    name = []
    pwd = []
    
    for i in totalComp:
        CompId = i['id']
        CompIp = i['ip']
        CompPort = i['port']
        CompUser = i['user']
        CompName = i['name']
        CompPwd = i['password']
        ids.append(CompId)
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

def TemplateGetResult(Stmt, genFile):
    num = 0
    for i in ip:
        conn=psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        conn.autocommit = True
        cur=conn.cursor()
        cur.execute(Stmt)
        res = str(cur.fetchall())
        Res = res.replace(')',')\n')
        cur.close()
        conn.close()

        with open("./ddl-diff/%s%d" % (genFile, num),"w") as f:
            f.write(Res)
        num += 1

def TemplateFilecmp(tableName):
    print("\n======== " + tableName + " ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/%s%d" %(tableName, num), "./ddl-diff/%s%d" %(tableName, num + 1))
            if diff :
                print(Cns[num] + ' is the same as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + ' is not the same as ' + Cns[num + 1] + " , failure")
        num += 1

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
                    print(Cns[num] + ' is the same as ' + Cns[num + 1] + " , success")
                else:
                    print(Cns[num] + ' is not the same as ' + Cns[num + 1] + " , failure")
            num += 1
######################
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
                print(Cns[num] + ' is the same as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + ' is not the same as ' + Cns[num + 1] + " , failure")
        num += 1
#########################

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

    print("\n======== pg_shard ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/pg_shard%d" %(num), "./ddl-diff/pg_shard%d" %(num + 1))
            if diff :
                print(Cns[num] + ' is the same as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + ' is not the same as ' + Cns[num + 1] + " , failure")
        num += 1
############################
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

    print("\n======== pg_shard_node ========\n")
    num = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else:
            diff = filecmp.cmp("./ddl-diff/pg_shard_node%d" %(num), "./ddl-diff/pg_shard_node%d" %(num + 1))
            if diff :
                print(Cns[num] + ' is the same as ' + Cns[num + 1] + " , success")
            else:
                print(Cns[num] + ' is not the same as ' + Cns[num + 1] + " , failure")
        num += 1

def Checkpg_cluster_meta(): #check pg_cluster_meta and id/compName
    TemplateGetResult('select cluster_id, cluster_master_id, ha_mode, cluster_name from pg_cluster_meta', 'pg_cluster_meta')
    TemplateGetResult('select comp_node_id from pg_cluster_meta','id')
    TemplateGetResult('select comp_node_name from pg_cluster_meta','name')
    TemplateFilecmp('pg_cluster_meta')
    num = 0
    for i in ip:
        ida = '[(' + str(ids[num]) + ',)\n]'
        namea = "[('" + str(name[num]) + "',)\n]"
        with open("./ddl-diff/cid%d" % (num),'w') as f:
            f.write(ida)
        with open("./ddl-diff/cname%d" % (num),'w') as f:
            f.write(namea)
        num += 1

    num = 0
    for i in Cns:
        diff = filecmp.cmp("./ddl-diff/id%d" %(num), "./ddl-diff/cid%d" %(num))
        if diff :
            pass
        else:
            print('Cns Cinfigure file id :' + str(ids[num]) + ' is not the same as pg_cluster_meta/comp_node_id, failure')
        num += 1

    num = 0
    for i in Cns:
        diff = filecmp.cmp("./ddl-diff/name%d" %(num), "./ddl-diff/cname%d" %(num))
        if diff :
            pass
        else:
            print('Cns Cinfigure file name :' + str(ids[num]) + ' is not the same as pg_cluster_meta/comp_node_name name, failure')
        num += 1

def Check_pg_class(): # relpages, relallvisible
    stmt1='select relname, relnamespace, reltype, reloftype, relowner, relam, relfilenode, reltablespace, reltuples, reltoastrelid, relhasindex, relisshared, relpersistence, relkind, relnatts, relchecks, relhasoids, relhasrules, relhastriggers, relhassubclass, relrowsecurity, relforcerowsecurity, relispopulated, relreplident, relispartition, pad1, pad2, relshardid, relrewrite, relfrozenxid, relminmxid, relacl, reloptions, relpartbound from pg_class;'
    TemplateGetResult(stmt1, 'pg_class')
    TemplateFilecmp('pg_class')

def Check_pg_ddl_log_progress():
    stmt1 = 'select dbid from pg_ddl_log_progress'
    TemplateGetResult(stmt1, 'pg_ddl_log_progress')
    TemplateFilecmp('pg_ddl_log_progress')
    
    num = 0
    execStmt1 = "select ddl_op_id from pg_ddl_log_progress"
    execStmt2 = "select max_op_id_done_local from pg_ddl_log_progress"
    
    for i in ip:
        conn = psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        cur = conn.cursor()
        cur.execute(execStmt1)
        opid = cur.fetchall()
        cur.close()
        conn.close()

        conn = psycopg2.connect(database = 'postgres', user = user[num], host = i, port = port[num], password = pwd[num])
        cur = conn.cursor()
        cur.execute(execStmt2)
        maxid = cur.fetchall()
        cur.close()
        conn.close()

        values = str(opid + maxid)
        values = values.replace(',), ','\n')
        values = values.replace('[','')
        values = values.replace('(','')
        values = values.replace(',)]','')

        with open("./ddl-diff/Cns%s" % num, 'w') as f:
            f.write(values)
        count = len(open("./ddl-diff/Cns%s" % num, 'rU').readlines())
        num += 1
    
    #现在是把所有节点的pg_ddl_log_process的第二列和第三列的值给取出来一个个进行对比
    #如果节点1的value1和节点2的值出现相同的则和节点3对比，如果和其它节点比都没有问题
    #则换节点1的其它值与其它节点的值进行对比
    #节点1对比完就换节点2进行对比
    #直到所有的节点都对比完成
    timenum = 0 #找出所有节点的个数
    for times in ip:
        timenum += 1
    filenum = 0
    for a in range(timenum): #以节点个数循环
        count = len(open("./ddl-diff/Cns%s" % filenum, 'rU').readlines()) #检查当前节点的值个数
        filenum += 1
        for line in range(1, count + 1): # 开始查找被对比的节点的当前值
            thisline = linecache.getline("./ddl-diff/Cns%s" % (a), line)
            for otherfile in range(timenum): # 再以节点所有数量为循环
                flag = False
                for otherline in range(1, count +1): # 找到要对比节点的当前值，然后与被对比的节点的值进行对比
                    otherlines = linecache.getline("./ddl-diff/Cns%s" % (otherfile) , otherline)
                    if otherlines == thisline :
                        flag = True
                        break
                    else:
                        pass
                        
                if flag:
                    pass
                else :
                    print("CN%s table:pg_ddl_log_process values === %s === can not find with Cn%s, failure \n" %(a, thisline, otherfile)) ;
    
    #这一步是对比第一个节点的最后一列，最后一列一定是与另一个节点值相反，其他节点则和第一个节点相同
    TemplateGetResult('select ddl_op_id from pg_ddl_log_progress','opid') #遍历所有节点然后各查询一次select语句，然后写到以opid开头的文件里
    TemplateGetResult('select max_op_id_done_local from pg_ddl_log_progress','maxid') #遍历所有节点然后各查询一次select语句，然后写到以maxid开头的文件里
    num = 0
    for i in ip:
    #每个节点各生成一个最后记录ddl_op_id列和max_op_id_done_local列最后一行的临时文件
        with open("./ddl-diff/opid%s" % (num), 'r') as f:
            opLine = f.readlines()
        sopLine = str(opLine)
        a = ",)\\n', ']']"
        b = ",)\\n', ', ("
        sopLine = sopLine.replace(a,'')
        sopLine = sopLine.replace(b,'\n')
        f.close()
        
        with open("./ddl-diff/opid%s" % (num), 'w') as f:
            f.write(sopLine)
        f.close()

        with open("./ddl-diff/opid%s" % (num), 'r') as f:
            opline = f.readlines()
            opLastLine = opline[-1]

        
        with open("./ddl-diff/maxid%s" % (num), 'r') as f:
            maxLine = f.readlines()
        smaxLine = str(maxLine)
        a = ",)\\n', ']']"
        b = ",)\\n', ', ("
        smaxLine = smaxLine.replace(a,'')
        smaxLine = smaxLine.replace(b,'\n')
        f.close()

        with open("./ddl-diff/maxid%s" % (num), 'w') as f:
            f.write(smaxLine)
        f.close()

        with open("./ddl-diff/maxid%s" % (num), 'r') as f:
            maxline = f.readlines()
            maxLastLine = maxline[-1]

        #opLastLine = linecache.getline("./ddl-diff /opid%s" % (num), -2)
        #maxLastLine = linecache.getline("./ddl-diff/maxid%s" % (num), -2)
        #print(" %s\n%s\n " % (opLastLine, maxLastLine))
        LastLine = "%s\n%s\n" % (opLastLine, maxLastLine)
        print(LastLine)
        with open("./ddl-diff/lastline%s" % (num), 'w') as f:
            f.write(LastLine)
        num += 1

    # 将生成的存有节点信息的临时文件0和其它刚生成的临时文件相比
    num = 0
    cnum = 0
    for i in Cns:
        if i == Cns[-1]:
            pass
        else :
            filenow = "./ddl-diff/lastline%s" % (0)
            filelater = "./ddl-diff/lastline%s" % (num + 1)
            print(filenow, filelater)
            diff = filecmp.cmp(filenow, filelater)
            if diff:
                pass
                num +=1
            else : #如果文件不一致，则cnum +1
                cnum += 1
                opid1 = linecache.getline(filenow , 1)
                maxid1 = linecache.getline(filenow, 2)
                opid2 = linecache.getline(filelater, 1)
                maxid2 = linecache.getline(filelater, 2)
                if opid1 == maxid2 and maxid1 == opid2:
                    pass
                    num += 1
                else : #如果不一致的两个文件内容不符合文件1的值1 = 文件2 并且 文件1的值2 == 文件2的值1，则cnum + 1
                    cnum += 1
                    num += 1

    if cnum == 1 : #如果说cnum数为1，则刚好符合只有一个节点和节点1不同，其它节点都一样且不同的节点和节点1的值刚好相反
        pass
    else :
        print('the last row of table "pg_ddl_log_progress" got some worng, please check, failure !!! ')

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
    #checkAllSystemTable()
    #Checkpg_cluster_meta()
    #Check_pg_class()
    Check_pg_ddl_log_progress()
