from configparser import ConfigParser

class get_conf_info():
    def __init__(self):
        self.cnf = ConfigParser()

    def cluster_mgr(self):
        # 这里就是获取配置文件里面cluster_mgr那部分的信息
        # 以字典的形式返回
        cnf = self.cnf
        cnf.read('./conf/config.conf', encoding='utf-8')
        cluster_mgr_info = dict(cnf.items('cluster_mgr'))
        return cluster_mgr_info

    def klustron_metadata(self):
        # 同上，不过是获取配置文件里面的klustron_metadata信息
        cnf = self.cnf
        cnf.read('./conf/config.conf', encoding='utf-8')
        klustron_metadata_info = dict(cnf.items('klustron_metadata'))
        return klustron_metadata_info
