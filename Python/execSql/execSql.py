import yaml
import pymysql
import psycopg2
import argparse
from time import sleep

def ReadFile():
    openFile = open(files,encoding='utf-8')
    readFile = yaml.safe_load(openFile.read())
    mySqls = readFile["mySqls"]
    pgSqls = readFile["pgSqls"]
    comp = readFile["computing_nodes"]
    
    lens = len(list(comp)) 
    title = list(comp)
    
    global ports, ips, users, pwds
    ports, ips, users, pwds = [], [], [], []
    for i in range(0, lens):
        comps = dict(comp[title[i]])
        port = comps['port']
        ip = comps['ip']
        user = comps['user']
        pwd = comps['pwd']
        ports.append(port)
        ips.append(ip)
        users.append(user)
        pwds.append(pwd)

    for i in range(lens):
        print('\n||这个是第%s个计算节点信息：\n||   ip | port | user | pwd' % (str(i + 1)))
        print("|| " + ips[i] + " | " + str(ports[i]) + " | " + users[i] + " | " + pwds[i])

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = '这个脚本是用来给集群里所有的节点都单独指定sql的脚本')
    parser.add_argument('--config', default='config.yaml', help = 'the configure yaml file')
    parser.add_argument('--type', default='all', help = 'can be "comp"||"storage"||"all"')
    args = parser.parse_args()
    types = args.type
    files = args.config
    ReadFile()
