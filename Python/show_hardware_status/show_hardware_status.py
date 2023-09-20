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

    def signal_thread(ip):
        com = comm(ip, user)
        for i in 'cpu', 'mem', 'net', 'disk':
            mk_c = 'mkdir -p result/%s/; touch result/%s/%s' % (ip, i)
            subprocess.run(mk_c, shell=True)
        while True:
            subprocess.run(com.cpu(), shell=True)
            subprocess.run(com.mem(), shell=True)
            subprocess.run(com.net(), shell=True)
            subprocess.run(com.disk(), shell=True)
            sleep(interval)

    l = []
    rm_c = 'rm -rf ./result/*'
    subprocess.run(rm_c, shell=True)
    for ip in host:
        p = Thread(target=signal_thread, args=[ip])
        l.append(p)
        p.start()

if __name__ == '__main__':
    show()
