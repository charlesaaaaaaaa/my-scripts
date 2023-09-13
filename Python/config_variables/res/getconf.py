from configparser import ConfigParser

class readcnf():
    def __init__(self):
        pass

    def getKunlunInfo(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('kunlun'))
        return cnf

    def server_settings(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('server_settings'))
        return cnf

    def storage_settings(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('storage_settings'))
        return cnf
#readConf().kunlun()