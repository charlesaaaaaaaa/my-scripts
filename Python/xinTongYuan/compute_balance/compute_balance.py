import argparse
from time import sleep
import psycopg2
import yaml
import _thread as thread
import subprocess

def subrun(cmd):
    p = subprocess.Popen(cmd, shell = True, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
    return(p.communicate()[0])

def tMem(times, intervel, threshold, longName):
    for i in range(times):
        res = subrun('bash mem.sh %s' % (longName))
        if int(res) >= threshold:
            print("warning: 当前所有服务器中内存最大读数与最小读数超过给定%s阈值: %s" % (threshold, int(res)))
        sleep(intervel)

def tCpu(times, intervel, threshold, longName):
    for i in range(times):
        res = subrun('bash cpu.sh %s' % (longName))
        if int(res) >= int(threshold):
            print("warning: 当前所有服务器中cpu空闲率最大读数与最小读数超过给定%s阈值: %s" % (threshold, int(res)))
        sleep(intervel)

def test():
    with open(config, mode = 'r', encoding = 'utf-8') as files:
        conf = yaml.safe_load(files)
    
    #这里是开启haproxy
    long_name = '%s:%s' % (conf['haproxy_host'], conf['haproxy_port'])
    for i in conf['instance']:
        if len(conf['instance'][i]) == 4:
            long_name = "%s %s:%s" % (long_name, conf['instance'][i]['host'], conf['instance'][i]['port'])
    print('=== 开启haproxy...')
    subprocess.run('bash installHaproxy.sh %s' % (long_name), shell = True)

    #启动sysbench
    num = 0
    for i in conf['instance']:
        if len(conf['instance'][i]) == 4:
            print(len(conf['instance'][i]))
            host = conf['instance'][i]['host']
            port = conf['instance'][i]['port']
            user = conf['instance'][i]['user']
            pwd  = conf['instance'][i]['pwd']
            break
    Time = conf['runtime']
    execClear = "sysbench oltp_point_select --tables=10 --table-size=525000 --db-driver=pgsql --pgsql-host=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=postgres --threads=10 clearup" % (conf['haproxy_host'], conf['haproxy_port'], user, pwd)
    execPrepare = "sysbench oltp_point_select --tables=10 --table-size=525000 --db-driver=pgsql --pgsql-host=%s --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=postgres --threads=10 prepare" % (conf['haproxy_host'], conf['haproxy_port'], user, pwd)
    try:
        subrun(execClear)
        sleep(5)
    except:
        print("skip clear")
    subprocess.run(execPrepare, shell = True)
    sleep(10)
    for i in conf['instance']:
        num = num + 1
    threads = num * 100
    execStart = "sysbench oltp_write_only --tables=10 --table-size=50000 --db-ps-mode=disable --db-driver=pgsql --pgsql-host=%s --report-interval=60 --pgsql-port=%s --pgsql-user=%s --pgsql-password=%s --pgsql-db=postgres --threads=%d --time=%s --rand-type=uniform run > sysbenchRun.log 2>&1 &" % (conf['haproxy_host'], conf['haproxy_port'], user, pwd, threads, Time)
    
def check():
    with open(config, mode = 'r', encoding = 'utf-8') as files:
        conf = yaml.safe_load(files)

    #开始检测机器状态是否超过给定的阈值
    Time=conf['runtime']
    interval=conf['interval']
    interval = conf['interval']
    threshold = conf['threshold']
    times = int(Time/interval)
    longName = conf['defuser']
    for i in conf['instance']:
        longName = "%s %s" % (longName, conf['instance'][i]['host'])
    t1 = thread.start_new_thread(tMem, (times, interval, threshold, longName,))
    t1 = thread.start_new_thread(tCpu, (times, interval, threshold, longName,))
    sleep(Time)

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='the compute balance test')
    ps.add_argument('--config', type=str, help='the config file of KunlunBase')
    args = ps.parse_args()
    print(args)
    config = args.config
    test()
    check()
