from time import sleep
import time
from configparser import ConfigParser

def timer(func):
    def wapper(*args, **kwargs):
        startTime = time.time()
        res = func(*args, **kwargs)
        endTime = time.time()
        spendTime = endTime - startTime
        sleep(5)
        print('本次 %s 测试使用了 %s 秒' % (func.__name__, spendTime))
        return res
    return wapper

class getconf():
    def __init__(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        self.conf = conf

    def getXpanelInfo(self):
        conf = self.conf
        xpanelInfo = dict(conf.items('xpanel_info'))
        return xpanelInfo

class getElements():
    def __init__(self):
        conf = ConfigParser()
        conf.read('./conf/elements.conf', encoding='utf8')
        self.conf = conf

    def get(self, name):
        conf = self.conf
        res = dict(conf.items(name))
        return res

    def cluster_manage(self):
        conf = self.get('cluster_manage')
        return conf

    def alarm(self):
        conf = self.get('alarm_server_manage')
        return conf

    def loadInterface(self):
        conf = self.get('load_interface')
        return conf

    def system_manage(self):
        conf = self.get('system_manage')
        return conf