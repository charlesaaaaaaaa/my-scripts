from time import sleep
import time
from configparser import ConfigParser
import subprocess
from bin import connection
import os


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


class OtherConf:
    def __init__(self, conf_path):
        conf = ConfigParser()
        conf.read(conf_path, encoding='utf8')
        self.conf = conf
        self.conf_path = conf_path

    def read(self, key_name):
        conf = self.conf
        info = dict(conf.items(key_name))
        return info

    def write(self, sec_level_dict):
        # sec_level_dict, 就是要给一个二级的dict，第一级是配置文件里面的节(section), 第二级是一个列表，列表里面要有第二级的dict
        # 如 {'meta_info': [{'host': '192.168.0.129, 192.168.0.129, 192.168.0.129'}, {'port': '59301, 59304, 59307'},
        # {'user': 'pgx, pgx, pgx'}, {'pass': 'pgx_pwd, pgx_pwd, pgx_pwd'}]}
        conf = self.conf
        for section in sec_level_dict:
            if section not in conf:
                # 这里是添加一个不存在的节，就是配置文件里面的中括号[section]
                conf.add_section(section)
            for key in sec_level_dict[section]:
                # 这里是一级字典的值了，正常来说应该是个列表
                    # 这里就是列表里面的各个二级字典了
                    # 这里就是在这个节点里面添加key和value
                conf[section][key] = sec_level_dict[section][key]

        with open(self.conf_path, 'w') as f:
            conf.write(f)
        f.close()


class getconf():
    def __init__(self):
        conf = ConfigParser()
        conf.read('./conf/config.conf', encoding='utf8')
        self.conf = conf

    def getXpanelInfo(self):
        conf = self.conf
        xpanelInfo = dict(conf.items('xpanel_info'))
        return xpanelInfo


def init_config():
    # 测试开始前要做的动作，把所有需要的配置信息配置到一个临时文件里面
    master_dict = {}
    file_path = './conf/init.conf'
    conf = getconf().getXpanelInfo()
    meta_host, meta_port = conf['meta_host'], conf['meta_port']
    try:
        os.remove(file_path)
    except:
        pass
    # 所有元数据节点信息
    host, port, user_name, password = '', '', '', ''
    # 开始处理这个元数据节点信息
    all_meta_info_sql = 'select hostaddr, port, user_name, passwd from meta_db_nodes;'
    meta_conn = connection.My(host=meta_host, port=int(meta_port), user='pgx', password='pgx_pwd', db='kunlun_metadata_db')
    all_meta_info = meta_conn.sql_with_res(all_meta_info_sql)
    for info in all_meta_info:
        if host:
            host += ', %s' % info[0]
            port += ', %s' % str(info[1])
            user_name += ', %s' % info[2]
            password += ', %s' % info[3]
        else:
            host = info[0]
            port = str(info[1])
            user_name = info[2]
            password = info[3]
    # 新建一个元数据信息的字典
    meta_info = {'meta_info': {'host': host, 'port': port, 'user': user_name, 'pass': password}}
    # 把元数据节点信息添加到这个字典里面
    master_dict.update(meta_info)
    OtherConf(file_path).write(sec_level_dict=master_dict)


class getElements:
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

    def multi_tenan(self):
        conf = self.get('multi-tenancy')
        return conf

    def rcr_server(self):
        conf = self.get('rcr_server')
        return conf

    def metadata_nodelist(self):
        conf = self.get('meatadata_node_list')
        return conf

    def cdc_server(self):
        conf = self.get('cdc_server')
        return conf

def run_shell(command):
    print(command)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    res = output.communicate()
    for i in res:
        print(i)
    return res