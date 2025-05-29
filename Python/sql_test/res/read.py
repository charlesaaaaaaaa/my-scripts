import configparser

def conf_info():
    cnf = configparser.ConfigParser()
    cnf.read('./conf/sql_test.conf', encoding='utf-8')
    cnf_info = dict(cnf.items('kunlun'))
    return cnf_info

def other_file(file_path):
    of = open(file=file_path, mode='r', encoding='utf-8')
    res = of.readlines()
    return res