from configparser import ConfigParser

class readcnf():
    def __init__(self):
        pass

    def getDbInfo(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('database_info'))
        return cnf

    def get_necessary_info(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('necessary_info'))
        return cnf

    def get_other_info(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('other_info'))
        return cnf
#readConf().kunlun()