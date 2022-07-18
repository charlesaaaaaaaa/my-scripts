import yaml
import datetime
from time import sleep
import argparse
import subprocess
import random
import os
import json

def run(stmt):
    subprocess.Popen(stmt, stdout=subprocess.PIPE, shell = True)

def readFile():
    global config, runtime, table, tableSize, driver, sthd, slwk
    global loadworker, reportInterval, relaxTime, threads, files, comp
    f = open(config)
    files = yaml.safe_load(f.read())
    
    runtime = dict(files)['runtime']
    table = dict(files)['table']
    tableSize = dict(files)['tableSize']
    driver = dict(files)['driver']
    reportInterval = dict(files)['reportInterval']
    relaxTime = dict(files)['relaxTime']
    threads = dict(files)['threads']
    comp = dict(files)['config']
    loadworker = dict(files)['loadworker']
    
    sthd = str(threads)
    sthd = sthd.replace('[','"')
    sthd = sthd.replace(',','')
    sthd = sthd.replace(']','"')

    slwk = str(loadworker)
    slwk = slwk.replace('[','"')
    slwk = slwk.replace(']','"')
    slwk = slwk.replace("'","")
    slwk = slwk.replace(",","")
    
    print('-------- testing threads = ' + sthd)
    print('-------- testing loadworker = ' + slwk)

def runTest():
    a = 0
    global comps
    host, pwd, port, dbname, user = [], [], [], [], []
    for i in comp:
        print(i)
        print(comp)
        comps = comp[i]
        hosts = comps['host']
        pwds = comps['pwd']
        ports = comps['port']
        dbnames = comps['dbname']
        users = comps['user']
        host.append(hosts)
        pwd.append(pwds)
        port.append(ports)
        dbname.append(dbnames)
        user.append(users)
    
    for dir1 in comp:
        stmt = "rm -rf %s" % (dir1)
        print(stmt)
        run(stmt)
        sleep(1)
        for dir2 in loadworker:
            stmt = "mkdir -p %s/%s " % (dir1, dir2)
            #run(stmt)
            print(stmt)
            os.makedirs('%s/%s' % (dir1, dir2))

    for cp in comp:
        stmt = 'cp *sh ./%s' % (cp)
        run(stmt)
        print(stmt)

    tis = '\n====================\n'
    #the first test
    for loadworkers in loadworker:
        print('%s this is %s %s' % (tis, loadworkers, tis))
        for thd in threads:
            num = 0
            print('%s this is %s %s' % (tis, thd, tis))
            for i in comp:
                #这个是首次跑时的sysbench数据
                stmt = "sysbench oltp_%s --tables=%d --table-size=%d --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%d --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%d --time=%s --rand-type=uniform run > ./%s/%s/%d_%s 2>&1 & \n" % (loadworkers, table, tableSize, driver, host[num], reportInterval, port[num], user[num], pwd[num], dbname[num], thd, runtime, i, loadworkers, thd, loadworkers)
                print(stmt)
                run(stmt)
                num = num + 1

            sleep(runtime)
            
            num = 0
            stmt = 'rm -rf checktmp && touch checktmp'
            print(stmt)
            run(stmt)
            sleep(1)
            
            for hosts in host:
                stmt = '/bin/bash pid.sh %s %s' % (hosts, port[num])
                print(stmt)
                run(stmt)
                num = num + 1
                while os.path.isfile('./pid.log'):
                    print('%s:%s still runing, plz wait...' % (hosts, port[num]))
                    sleep(1)
                    run(stmt)
            sleep(relaxTime)

            stmt = 'rm -rf checktmp'
            run(stmt)
            sleep(1)
            
def checkRerun():
    
    stmt1 = 'rm -rf tmpcheck.txt\n ========================\n'
    for dirs in comp:
        #stmt = 'cd %s && /bin/bash ./result.sh %s %s' % (dirs, sthd, slwk)
        stmt = 'cd %s && /bin/bash ./result.sh %s %s && /bin/bash ./check.sh %s %s && ls' % (dirs, sthd, slwk, sthd, slwk)
        print(stmt)
        subprocess.run(stmt, shell = True)

#    stmt = 'cat tmpcheck.yaml | sort | uniq >> tmpcheck.yaml && rm tmpcheck.yaml'
#    print(stmt)
#    run(stmt)

    for i in threads:
        if not os.path.getsize('%scheck.yaml' % (i)):
            stmt = "rm -rf %scheck.yaml" % (i)
            print(stmt)
            #run(stmt)
        else:
            with open('%scheck.yaml' % (i),"r",encoding="utf-8") as f:
            #check = yaml.safe_load(ch.read())
                check = yaml.load(f, Loader=yaml.FullLoader)
            #print(type(check))
            num = 0
            #for a in check:
             #   print(a,type(a))
                #print(type(a))
                #dic = yaml.load(a,Loader=yaml.FullLoader) #把str转换成dict
                #print(type(dic))
               # sleep(1)
            for item in check.items():
                #host = comps['host']
                sums = 0
                for ip in comp:
                    comps = comp[ip]
                    hosts = comps['host']
                    port = comps['port']
                    user = comps['user']
                    pwd = comps['pwd']
                    dbname = comps['dbname']
                    loadworker = str(item[0])
                    thd  = str(item[1])
                   # print(type(loadworker), type(thd))
                #这个是在检查发现有不成功重新跑的sysbench，会所有节点同时重跑失败的测试
                    stmt = "sysbench oltp_%s --tables=%s --table-size=%s --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%s --time=%s --rand-type=uniform run > ./%s/%s/%s_%s 2>&1 & \n" % (loadworker, table, tableSize, driver, hosts, reportInterval, str(port), user, pwd, dbname, thd, runtime, ip, loadworker, thd, loadworker)
                    print(stmt)
                    run(stmt)
                    sums = sums + 1
            
            sleep(runtime)

            num = 0
            stmt = 'rm -rf checktmp && touch checktmp'
            print(stmt)
            run(stmt)
            sleep(1)
            
            for hosts in host:
                stmt = '/bin/bash pid.sh %s %s' % (hosts, port[num])
                print(stmt)
                run(stmt)
                num = num + 1
                while os.path.isfile('./pid.log'):
                    print('%s:%s still runing, plz wait...' % (hosts, port[num]))
                    sleep(1)
                    run(stmt)
            sleep(relaxTime)

            stmt = 'rm -rf checktmp'
            run(stmt)
            sleep(1)

            
            num = num + 1
    stmt = 'rm -rf *check.ymal'
    print(stmt)
    run(stmt)

def date():
    global dirName
    compName = []
    for i in comp:
        compName.append(i)
    compName = str(compName)
    compName = compName.replace("'","")
    compName = compName.replace(",","")
    compName = compName.replace("[","")
    compName = compName.replace("]","")
    dirName=datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    stmt = 'tar -zcf %s.tgz %s' % (dirName, compName)
    run(stmt)

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description = 'a')
    parse.add_argument("--config", default = 'config.yaml')
    args = parse.parse_args()
    config = args.config

    readFile()
    runTest()
    #for i in range(10):
    #    checkRerun()
    date()
