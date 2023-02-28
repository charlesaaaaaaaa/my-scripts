# -*- coding: utf-8 -*-
import wget
import time
import subprocess
import selenium
import argparse

start_time = time.time()
def deploy_cluster():
    subprocess.run("rm -rf *gz* && rm -rf cloudnative", shell=True)
    start_cloud_time = time.time()
    print('start clone cloudnative ...')
    subprocess.run("git clone https://gitee.com/zettadb/cloudnative.git", shell=True)
    end_cloud_time = time.time()
    final_cloud_time = end_cloud_time - start_cloud_time 
    print('clone cloudnative: %.2f s' % (final_cloud_time))
    thirdPart_downList = ['hadoop-3.3.1.tar.gz', 'jdk-8u131-linux-x64.tar.gz', 'mysql-connector-python-2.1.3.tar.gz', 'prometheus.tgz', 'haproxy-2.5.0-bin.tar.gz', 'efk/filebeat-7.10.1-linux-x86_64.tar.gz']
    kunlun_downList = ['kunlun-cluster-manager-1.1.1.tgz', 'kunlun-node-manager-1.1.1.tgz', 'kunlun-server-1.1.1.tgz', 'kunlun-storage-1.1.1.tgz', 'kunlun-proxysql-1.1.1.tgz']
    print('download component ...')
    start_downl_time = time.time()
    for i in thirdPart_downList:
        Url = "http://zettatech.tpddns.cn:14000/thirdparty/%s" % (str(i))
        print("\ndownloading %s ..."% (i))
        wget.download(Url)
    for i in kunlun_downList:
        Url = "http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/%s" % (str(i))
        print("\ndownloading %s ..." % (i))
        wget.download(Url)
    end_downl_time = time.time()
    final_downl_time = end_downl_time - start_downl_time
    print('download component : %.2f s' % (final_downl_time))
    subprocess.run("mv *gz* cloudnative/cluster/clustermgr", shell=True)
    subprocess.run("cp %s cloudnative/cluster" % (Deploy), shell=True)
    start_deploy_time = time.time()
    print('start deploy KunlunBase ...')
    deploy_command = "cd cloudnative/cluster && python2 setup_cluster_manager.py --config %s --action install --defuser %s --product_version 1.1.1" % (Deploy, User)
    print(deploy_command)
    subprocess.run(deploy_command, shell=True)
    subprocess.run("cd cloudnative/cluster && bash -e clustermgr/install.sh", shell=True)
    end_deploy_time = time.time()
    final_deploy_time = end_deploy_time - start_deploy_time
    print('deploy KunlunBase : %.2f s' % (final_deploy_time))

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='deploy&install KunlunBase cluster')
    ps.add_argument("--depoly", default='deploy-config.json', type=str, help='KunlunBase deploy config file, default value = "deploy-config.json"')
    ps.add_argument("--user", default='kunlun', type=str, help='KunlunBase user')
    #ps.add_argument("--install", type=str, help='KunlunBase install config file')
    args = ps.parse_args()
    User = args.user
    Deploy = args.depoly
    #Install = args.install
    print(args)
    start_time = time.time()
    deploy_cluster()
    #subprocess.run('Xvfb -ac :7 -screen 0 1280x1024x8 -nolisten tcp & export DISPLAY=:7; python3 Xpanel_install_cluster.py', shell=True)
    end_time = time.time()
    spend_time = end_time - start_time
    print("本次安装部署花费了：%.2f 秒" % (spend_time))
