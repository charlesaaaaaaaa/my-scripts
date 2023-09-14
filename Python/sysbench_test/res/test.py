from res.getconf import *
from res.command import *
import multiprocessing
import subprocess
from time import sleep

class action():
    def __init__(self):
        self.necInfo = readcnf().get_necessary_info()

    def prepare(self):
        command = sysbench_command().preapre()
        command += ' > prepare.log 2>&1'
        p = subprocess.Popen(command, shell=True)
        p.terminate()

    def cleanup(self):
        command = sysbench_command().cleanup()
        subprocess.run(command, shell=True)

    def run(self):
        command = sysbench_command()
        sleepTime = self.necInfo['sleeptime']
        cases = self.necInfo['case'].replace(' ', '').split(',')
        threads = self.necInfo['threads'].replace(' ', '').split(',')
        host = self.necInfo['host'].replace(' ', '').split(',')
        port = self.necInfo['port'].replace(' ', '').split(',')

        def run_process(position, lock):
            lock.acquire()
            for case in cases:
                for thread in threads:
                    run_c = command.run(case, thread, position)
                    print('正在对 %s:%s 进行 %s - %s 线程并发测试')
                    run_c += ' > pro%s/%s/%s 2>&1' % (position, case, thread)
                    p = subprocess.Popen(run_c, shell=True)
                    p.terminate()
                    sleep(sleepTime)

        l = []
        if len(host) != len(port):
            raise '配置文件中 host 与 port 数量不一致'
        for position in range(len(self.necInfo['host'])):
            lock = multiprocessing.Lock()
            p = multiprocessing.Process(target=run_process, args=(position, lock,))
            l.append(p)
            p.start()