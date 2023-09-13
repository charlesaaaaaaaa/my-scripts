from configparser import ConfigParser

class readcnf():
    def __init__(self):
        pass

    def getKunlunInfo(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('kunlun'))
        return cnf

    def getTestInfo(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('test'))
        return cnf
#readConf().kunlun()