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
            run(stmt)
            #os.makedirs('%s/%s' % (dir1, dir2))

    for cp in comp:
        stmt = 'cp *sh ./%s' % (cp)
        run(stmt)
        print(stmt)

    tis = '\n====================\n'
    #the first test
    for loadworkers in loadworker:
        for thd in threads:
            num = 0
            print('%s this is %s:%s, wait %ss %s' % (tis, loadworkers, thd, runtime, tis))
            for i in comp:
                #这个是首次跑时的sysbench数据
                stmt = "date > ./%s/%s/%d_%s " % (i, loadworkers, thd, loadworkers)
                stmt = "sysbench oltp_%s --tables=%d --table-size=%d --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%d --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%d --time=%s --rand-type=uniform run >> ./%s/%s/%d_%s & \n" % (loadworkers, table, tableSize, driver, host[num], reportInterval, port[num], user[num], pwd[num], dbname[num], thd, runtime, i, loadworkers, thd, loadworkers)
                print(stmt)
                run(stmt)
                num = num + 1

            #sleep(runtime)
            
            snum = 0
            stmt = 'rm -rf checktmp && touch checktmp'
            print(stmt)
            run(stmt)
            sleep(1)
            
            #现在是到了指定的运行时间了，检查是否进程依旧存在
            times = 1
            overtime = runtime + 50
            for hosts in host:
                stmt = '/bin/bash pid.sh %s %s' % (hosts, port[snum])
                print(stmt)
                run(stmt)
                sleep(1)
                while os.path.isfile('./pid.log'):
                    if times <= runtime :
                        sleep(5)
                        times = times + 5
                        run(stmt)
                    if times < overtime and times >= runtime : 
                        print('%s:%s still running, plz wait %ss ...' % (hosts, port[snum], times))
                        sleep(1)
                        run(stmt)
                        times = times + 1
                        #当超时到了50s直接杀进程
                    elif times >= overtime :
                        stmt = "ps -ef | grep sysbench | grep %s | grep %s | awk '{print $2}' | xargs kill -9" % (hosts, port[snum])
                        print('running more than 50s, now kill sysbench process\n' + stmt)
                        run(stmt)
                        break
                snum = snum + 1
            if times < runtime:
                print('%s: %s use %ss, less than %s, failed' % (loadworkers, thd, times, runtime))
            elif times >= runtime: 
                print('%s: %s use %ss, more than %s, success' % (loadworkers, thd, times, runtime))
            stmt = "rm -rf pid.log && ps -ef | grep -w sysbench | awk '{print $2}' | xargs kill -9"
            print(stmt)
            run(stmt)

            sleep(relaxTime)
            stmt = 'rm -rf checktmp'
            run(stmt)
            sleep(1)
            
def checkRerun():
    
    stmt1 = 'rm -rf *check.yaml'
    print(stmt1)
    run(stmt1)

    for dirs in comp:
        stmt = 'cd %s && /bin/bash ./result.sh %s %s && /bin/bash ./check.sh %s %s && ls' % (dirs, sthd, slwk, sthd, slwk)
        print(stmt)
        subprocess.run(stmt, shell = True)
    #检查是否存在测试失败的项
    for i in threads:
        if not os.path.exists('%scheck.yaml' % (i)):
            stmt = "%scheck.yaml does not exists, skip!" % (i)
            print(stmt)
        else:
            stmt = "cp %scheck.yaml %scheck.yamlbak && cat %scheck.yamlbak | sort | uniq > %scheck.yaml && rm %scheck.yamlbak" % (i, i, i, i, i) 
            run(stmt)
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
                    stmt = "date > ./%s/%s/%s_%s && sysbench oltp_%s --tables=%s --table-size=%s --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%s --time=%s --rand-type=uniform run >> ./%s/%s/%s_%s 2>&1 & \n" % (ip, loadworker, thd, loadworker, loadworker, table, tableSize, driver, hosts, reportInterval, str(port), user, pwd, dbname, thd, runtime, ip, loadworker, thd, loadworker)
                    print(stmt)
                    run(stmt)
                    sums = sums + 1
            
            num = 0
            stmt = 'rm -rf checktmp && touch checktmp'
            print(stmt)
            run(stmt)
            sleep(1)
            # 测试结束检查是否依旧存在进程
            times = 1
            overtime = runtime + 50
            for hosts in host:
                stmt = '/bin/bash pid.sh %s %s' % (hosts, ports[num])
                print(stmt)
                run(stmt)
                sleep(1)
                while os.path.isfile('./pid.log'):
                    if times < runtime:
                        sleep(5)
                        run(stmt)
                        times = times + 5
                    if times < 50 :
                        print('%s:%s still running, plz wait %ss ...' % (hosts, ports[num], times))
                        sleep(1)
                        run(stmt)
                        times = times + 1
                        #进程超时50s直接杀掉对应进程
                    elif times >= 50:
                        stmt = "ps -ef | grep sysbench | grep %s | grep %s | awk '{print $2}' | xargs kill -9" % (hosts, ports[num])
                        print('running more than 50s, now kill sysbench process\n' + stmt)
                        run(stmt)
                        break
                num = num + 1
            if times < runtime:
                print('%s: %s use %ss, less than %s, fail' % (loadworkers, thd, times, runtime))
            elif times >= runtime:
                print('%s: %s use %ss, more than %s, success' % (loadworkers, thd, times, runtime))
            stmt = "rm -rf pid.log && ps -ef | grep -w sysbench | awk '{print $2}' | xargs kill -9"
            print(stmt)
            run(stmt)
            sleep(relaxTime)

            stmt = 'rm -rf checktmp'
            run(stmt)
            sleep(1)

            
            num = num + 1
    #stmt = 'rm -rf *check.yaml'
    #print(stmt)
    #run(stmt)

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
        #开始准备sysbench测试数据
        stmt = 'sysbench oltp_point_select --tables=%s --table-size=%s --db-driver=%s --pgsql-host=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s prepare > prepare.log' % (table, tableSize, driver, host[0], port[0], user[0], pwd[0], dbname[0])
        print("======== now preparing sysbench data")
        print(stmt)
        run(stmt)
        stmt = '/bin/bash pid.sh %s %s' % (host[0], port[0])
        print(stmt)
        run(stmt)
        times = 1
        #检查当前准备数据进程是否存在
        while os.path.isfile('./pid.log'):
            if times < 9000 :
                print('%s:%s still running, plz wait %ss ...' % (host[0], port[0], times))
                sleep(1)
                run(stmt)
                times = times + 1
                #当进程超过9000s直接杀进程
            elif times >= 9000:
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
