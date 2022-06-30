import yaml
from time import sleep
import argparse
import subprocess
import random
import os

def readFile():
    global config, runtime, table, tableSize, driver, sthd
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
    sthd = sthd.replace(']','"')

    slwk = str(loadworker)
    slwk = slwk.replace('[','"')
    slwk = slwk.replace(']','"')
    slwk = slwk.replace("'","")
    
    print('-------- testing threads = ' + sthd)
    print('-------- testing loadworker = ' + slwk)

def runTest():
    a = 0
    host, pwd, port, dbname, user = [], [], [], [], []
    for i in comp:
        print(i)
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
        for dir2 in loadworker:
            stmt = "mkdir `pwd`/%s/%s" % (dir1, dir2)
            print(stmt)

    for cp in comp:
        stmt = "cp *sh ./%s" % (cp)
        print(stmt)

    tis = '\n====================\n'
    #the first test
    for loadworkers in loadworker:
        print('%s this is %s %s' % (tis, loadworkers, tis))
        for thd in threads:
            num = 0
            print('%s this is %s %s' % (tis, thd, tis))
            for hosts in host:
                stmt = "sysbench oltp_%s --tables=%d --table-size=%d --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%d --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%d --time=%s --rand-type=uniform run > ./%s/%s/%d_%s 2>&1 & \n" % (loadworkers, table, tableSize, driver, hosts, reportInterval, port[num], user[num], pwd[num], dbname[num], thd, runtime, i, loadworkers, thd, loadworkers)
                print(stmt)
                num = num + 1

            #sleep(runtime)
            
            num = 0
            stmt = 'rm -rf checktmp && touch checktmp'
            print(stmt)
            for hosts in host:
                stmt = 'bash ./pid.sh %s %s' % (hosts, port[num])
                print(stmt)
            
            print('sleep 10')
            
            while not os.path.getsize('./pid.log'):
                os.remove('./pid.log')
                break
            else:
                print('%s:%s is got some worng, please wait 10s……' % (loadworkers, thd))
                sleep(10)
                stmt = 'ps -ef | grep sysbench | xargs kill -9'
                print(stmt)
                os.remove('./pid.log')

def checkRerun():
    
    stmt1 = 'rm -rf tmpcheck.txt\n ========================\n'
    for dirs in comp:
        stmt = 'cd `pwd`/%s && /bin/bash ./result.sh && /bin/bash ./check.sh %s ' % (sthd)
        print(stmt)

    stmt = 'cat tmpcheck.yaml | sort | uniq >> tmpcheck.yaml && rm tmpcheck1.yaml'
    print(stmt)

    for i in threads:
        ch = open('%scheck.yaml' % (i))
        check = yaml.safe_load(ch.read())
        print(check)
        num = 0
        for a in check:
            sleep(1)
            for item in a.items():
                loadworker = item[0]
                thd  = item[1]
                stmt = "sysbench oltp_%s --tables=%d --table-size=%d --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%d --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%d --time=%s --rand-type=uniform run > ./%s/%s/%d_%s 2>&1 & \n" % (loadworkers, table, tableSize, driver, hosts, reportInterval, port[num], user[num], pwd[num], dbname[num], thd, runtime, i, loadworkers, thd, loadworkers)
                print(stmt)
            
            #sleep(runtime)

            stmt = 'bash pid.sh %s %s' % (hosts, loadworker)

            while not os.path.getsize('./pid.log'):
                os.remove('./pid.log')
                break
            else:
                print('%s:%s is got some worng, please wait 10s……' % (loadworkers, thd))
                sleep(10)
                stmt = 'bash pid.sh %s %s' % (hosts, loadworker)
                print(stmt)
                os.remove('./pid.log')

            
            num = num + 1

'''
    ch = open('tmpcheck.yaml')
    check = yaml.safe_load(ch.read())
    
    print(check)
    num = 0
    for a in check:
        print(a)
        sleep(1)
        for item in a.items():
            loadworker = item[0]
            thd  = item[1]
            stmt = "sysbench oltp_%s --tables=%d --table-size=%d --db-ps-mode=disable --db-driver=%s --pgsql-host=%s --report-interval=%d --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=%s --threads=%d --time=%s --rand-type=uniform run > ./%s/%s/%d_%s 2>&1 & \n" % (loadworkers, table, tableSize, driver, hosts, reportInterval, port[num], user[num], pwd[num], dbname[num], thd, runtime, i, loadworkers, thd, loadworkers)
            print(stmt)

        num = num + 1
'''


if __name__ == '__main__':
    parse = argparse.ArgumentParser(description = 'a')
    parse.add_argument("--config", default = 'config.yaml')
    args = parse.parse_args()
    config = args.config

    readFile()
    #runTest()
    #for i in range(10):
    #    checkRerun()
