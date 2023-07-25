# -*- coding:utf-8 -*-
from configparser import ConfigParser

class readcnf():
    def __init__(self):
        with open('./.location.txt', 'r') as f:
            dir_path = str(f.readlines(1)).replace('\\\\', '\\').split('=')[1].replace('\\n\']', '')
            f.close()
        self.location = dir_path

    def getConfigDbInfo(self):
        location = self.location
        cnf = ConfigParser()
        cnf.read(location, encoding='utf-8')
        clusterInfo = {}
        try:
            kl1 = dict(cnf.items('klustron'))
            signalInfo = {'klustron' : kl1}
            clusterInfo = dict(clusterInfo, **signalInfo)
        except:
            print('未找到klustron计算节点配置1')
            exit(1)
        try:
            my1 = dict(cnf.items('mysql'))
            signalInfo = {'mysql': my1}
            clusterInfo = dict(clusterInfo, **signalInfo)
        except:
            print('未找到mysql配置1')
            exit(1)
        return clusterInfo

    def getCdcInfo(self):
        location = self.location
        cnf = ConfigParser()
        cnf.read(location, encoding='utf-8')
        cdcInfo = dict(cnf.items('cdc'))
        return cdcInfo

    def getMysqlInfo(self):
        location = self.location
        cnf = ConfigParser()
        cnf.read(location, encoding='utf-8')
        mysqlInfo = dict(cnf.items('mysql'))
        return mysqlInfo

    def getKunlunInfo(self):
        location = self.location
        cnf = ConfigParser()
        cnf.read(location, encoding='utf-8')
        kunlunInfo = dict(cnf.items('klustron'))
        return kunlunInfo
