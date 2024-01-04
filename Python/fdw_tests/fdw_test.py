import argparse, os
from configparser import ConfigParser
from base.test import *

def write_conf(config, sqlfile, dbtype):
    try:
        os.remove(tmpfile)
    except:
        pass
    name_list = ['config', 'sqlfile', 'dbtype']
    value_list = [config, sqlfile, dbtype]
    print(name_list, value_list)
    with open(tmpfile, 'a') as f:
        num = 0
        f.write('[variables]\n')
        for value in value_list:
            key = name_list[num]
            content = '%s = %s\n' % (key, value)
            f.write(content)
            num += 1

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='fdw test')
    ps.add_argument("--config", default='./conf/config.conf', type=str)
    ps.add_argument("--sqlfile", type=str, default='./dml.sql')
    ps.add_argument("--dbtype", type=str, default='mysql', help='[mysql]|[pgsql]|[oracle]')
    tmpfile = './tmp.conf'
    args = ps.parse_args()
    config = args.config
    sqlfile = args.sqlfile
    dbtype = args.dbtype
    write_conf(config, sqlfile, dbtype)
    print(args)
    test()
    os.remove(tmpfile)