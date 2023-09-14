import time

from res.getconf import *
from res.command import *
import multiprocessing
import subprocess
from time import sleep
import os

class action():
    def __init__(self):
        self.necInfo = readcnf().get_necessary_info()
        self.dbInfo = readcnf().getDbInfo()

    def prepare(self):
        command = sysbench_command().preapre()
        command += ' > prepare.log 2>&1'
        print(command)
        subprocess.run(command, shell=True)

    def cleanup(self):
        command = sysbench_command().cleanup()
        print(command)
        subprocess.run(command, shell=True)

    def run(self):
        command = sysbench_command()
        sleepTime = self.necInfo['sleeptime']
        cases = self.necInfo['case'].replace(' ', '').split(',')
        threads = self.necInfo['threads'].replace(' ', '').split(',')
        host = self.dbInfo['host'].replace(' ', '').split(',')
        port = self.dbInfo['port'].replace(' ', '').split(',')

        def run_process(position, lock):
            lock.acquire()
            position += 1
            try:
                os.makedirs('./pro%s' % position)
            except:
                pass
            for case in cases:
                try:
                    os.makedirs('./pro%s/%s' % (position, case))
                except:
                    pass
                for thread in threads:
                    run_c = command.run(case, thread, position - 1)
                    print('正在对节点%s进行 %s - %s 线程并发测试' % (position, case, thread))
                    run_c += ' > pro%s/%s/%s 2>&1' % (position, case, thread)
                    print(run_c)
                    subprocess.run(run_c, shell=True)
                    sleep(int(sleepTime))

        l = []
        files = ''
        if len(host) != len(port):
            raise '配置文件中 host 与 port 数量不一致'
        else:
            for i in range(len(host)):
                file = './pro%s' % (i + 1)
                files += file + ' '
        subprocess.run('rm -rf %s' % files, shell=True)
        for position in range(len(host)):
            lock = multiprocessing.Lock()
            p = multiprocessing.Process(target=run_process, args=(position, lock,))
            l.append(p)
            p.start()
            if position == len(host) - 1:
                p.join()
        now = time.localtime()
        tar_time = '%s%s%s_%s%s%s' % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
        tar_c = 'tar -zcf %s.tgz %s' % (tar_time, files)
        subprocess.run(tar_c, shell=True)
