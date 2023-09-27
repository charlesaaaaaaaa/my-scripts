import multiprocessing
import threading
from threading import Thread
from base.command import *
import subprocess
from time import sleep
from base.getconf import readcnf


def show():
    conf = readcnf().get_instance()
    host = conf['host'].replace(' ', '').split(',')
    user = conf['user']
    interval = int(conf['interval'])

    def show_process(ip):
        com = comm(ip, user)
        command = 'mkdir -p result/%s' % (ip)
        subprocess.run(command, shell=True)
        for i in 'cpu', 'net', 'mem', 'disk':
            command = 'touch result/%s/%s' % (ip, i)
            subprocess.run(command, shell=True)
        def show_cpu():
            while True:
                subprocess.run(com.cpu(), shell=True)
                sleep(interval)
        def show_mem():
            while True:
                subprocess.run(com.mem(), shell=True)
                sleep(interval)
        def show_net():
            while True:
                subprocess.run(com.net(), shell=True)
                sleep(interval)
        def show_disk():
            while True:
                subprocess.run(com.disk(), shell=True)
                sleep(interval)
        collect_cpu = threading.Thread(target=show_cpu)
        collect_mem = threading.Thread(target=show_mem)
        collect_net = threading.Thread(target=show_net)
        collect_disk = threading.Thread(target=show_disk)
        collect_cpu.start()
        collect_mem.start()
        collect_net.start()
        collect_disk.start()
        collect_disk.join()
        collect_net.join()
        collect_mem.join()
        collect_cpu.join()

    l = []
    rm_c = 'rm -rf ./result/*'
    subprocess.run(rm_c, shell=True)
    for ip in host:
        p = multiprocessing.Process(target=show_process, args=(ip,))
        l.append(p)
        p.start()
    for li in l:
        li.join()

if __name__ == '__main__':
    show()