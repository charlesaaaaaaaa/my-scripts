from configparser import ConfigParser

class readcnf():
    def __init__(self):
        pass

    def get_instance(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        cnf = dict(conf.items('instance'))
        return cnf