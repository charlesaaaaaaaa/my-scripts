import configparser

def conf_info():
    cnf = configparser.ConfigParser()
    cnf.read('./conf/parquet.conf', encoding='utf-8')
    cnf_info = dict(cnf.items('cluster_info'))
    return cnf_info
