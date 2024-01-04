from configparser import ConfigParser

class get_variables():
    def __init__(self):
        tmp_path = './tmp.conf'
        configps = ConfigParser()
        configps.read(tmp_path, encoding='utf-8')
        self.conf = dict(configps.items('variables'))

    def dbtype(self):
        conf = self.conf
        res = conf['dbtype']
        return res

    def config(self):
        conf = self.conf
        res = conf['config']
        return res

    def sqlfile(self):
        conf = self.conf
        res = conf['sqlfile']
        return res

def getconf(types):
    configps = ConfigParser()
    dbtype = get_variables().dbtype()
    config = get_variables().config()
    configps.read(config, encoding='utf-8')
    conf = {}
    if types == 0:
        if dbtype == 'mysql':
            conf = dict(configps.items(dbtype))
        if dbtype == 'pgsql':
            conf = dict(configps.items(dbtype))
    elif types == 1:
        conf = dict(configps.items('klustron'))
    return conf