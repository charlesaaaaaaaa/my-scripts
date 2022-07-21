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
            print(stmt)
            os.makedirs('%s/%s' % (dir1, dir2))

    for cp in comp:
        stmt = 'cp *sh ./%s' % (cp)
        run(stmt)
        print(stmt)

    tis = '\n====================\n'
    #the first test
    for loadworkers in loadworker:
        for thd in threads:
            num = 0
            print('%s this is %s:%s %s' % (tis, loadworkers, thd, tis))
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
                times = 1
                while os.path.isfile('./pid.log'):
                    if times < 50 :
                        print('%s:%s still running, plz wait %ss ...' % (hosts, port[num], times))
                        sleep(1)
                        run(stmt)
                        times = times + 1
                    elif times == 50:
                        stmt = "ps -ef | grep sysbench | grep %s | grep %s | awk '{print $2}' | xargs kill -9" % (hosts, port[num])
                        print('running more than 50s, now kill sysbench process\n' + stmt)
                        run(stmt)
                        break
                num = num + 1


            sleep(relaxTime)

            stmt = 'rm -rf checktmp'
            run(stmt)
            sleep(1)
            
def checkRerun():
    
    stmt1 = 'rm -rf tmpcheck.txt\n ========================\n'
    for dirs in comp:
        stmt = 'cd %s && /bin/bash ./result.sh %s %s && /bin/bash ./check.sh %s %s && ls' % (dirs, sthd, slwk, sthd, slwk)
        print(stmt)
        subprocess.run(stmt, shell = True)

    for i in threads:
        if not os.path.exists('%scheck.yaml' % (i)):
            stmt = "rm -rf %scheck.yaml" % (i)
            print(stmt)
        else:
            with open('%scheck.yaml' % (i),"r",encoding="utf-8") as f:
                check = yaml.load(f, Loader=yaml.FullLoader)
            num = 0
            host, ports = [], []
            for item in check.items():
                sums = 0
                for ip in comp:
                    comps = comp[ip]
                    hosts = comps['host']
                    port = comps['port']
                    user = comps['user']
                    pwd = comps['pwd']
                    dbname = comps['dbname']
                    host.append(hosts)
                    ports.append(port)
                    loadworker = str(item[0])
                    thd  = str(item[1])
                    print('rerun %s:%s' % (loadworker, thd))
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
                stmt = '/bin/bash pid.sh %s %s' % (hosts, ports[num])
                print(stmt)
                run(stmt)
                times = 1
                while os.path.isfile('./pid.log'):
                    if times < 50 :
                        print('%s:%s still running, plz wait %ss ...' % (hosts, ports[num], times))
                        sleep(1)
                        run(stmt)
                        times = times + 1
                    elif times == 50:
                        stmt = "ps -ef | grep sysbench | grep %s | grep %s | awk '{print $2}' | xargs kill -9" % (hosts, ports[num])
                        print('running more than 50s, now kill sysbench process\n' + stmt)
                        run(stmt)
                        break
                num = num + 1

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

def prepare():
    if Prepare == 'y':
        host, pwd, port, dbname, user = [], [], [], [], []
        #sysbench oltp_point_select --tables= --table-size= --db-driver= --pgsql-host=$1 --pgsql-port= --pgsql-user= --pgsql-password= --pgsql-db= prepare
        for ip in comp:
            comps = comp[ip]
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

        stmt = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=%s --pgsql-host=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s prepare > prepare.log' % (table, tableSize, driver, host[0], port[0], user[0], pwd[0], dbname[0])
        print("======== now preparing sysbench data")
        print(stmt)
        run(stmt)
        stmt = '/bin/bash pid.sh %s %s' % (host[0], port[0])
        print(stmt)
        run(stmt)
        times = 1
        while os.path.isfile('./pid.log'):
            if times < 1500 :
                print('%s:%s still running, plz wait %ss ...' % (host[0], port[0], times))
                sleep(1)
                run(stmt)
                times = times + 1
            elif times == 1500:
                stmt = "ps -ef | grep sysbench | grep %s | grep %s | awk '{print $2}' | xargs kill -9" % (host[0], port[0])
                print('running more than 50s, now kill sysbench process\n' + stmt)
                run(stmt)
                break
        print('本次prepare时间为: %s s' % (times))

        stmt = 'sysbench oltp_delete --tables=%s --table-size=%s --db-driver=%s --pgsql-host=%s --pgsql-port=%s --pgsql-user=%s --pgsql-db=%s --pgsql-password=%s cleanup' % (table, tableSize, driver, host[0], port[0], user[0], dbname[0], pwd[0])
        print('======== 这个是你的sysbench clenaup命令, 本次不运行该条命令。')
        print(stmt)

    elif Prepare == 'n':
        print("skip prepare sysbench data")

if __name__ == '__main__':
    parse = argparse.ArgumentParser(description = 'a')
    parse.add_argument("--config", default = 'config.yaml', help = 'configuartion file')
    parse.add_argument("--prepare", default = 'n', help = '准备sysbench数据，有“n”和“y”，默认为“n”不准备sysbench数据')
    args = parse.parse_args()
    Prepare = args.prepare
    config = args.config

    readFile()
    prepare()
    runTest()
    for i in range(10):
        checkRerun()
    date()
