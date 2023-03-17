# -*- coding: utf-8 -*-
import wget
import time
import subprocess
import selenium
import argparse

start_time = time.time()
def deploy_cluster():
    subprocess.run("rm -rf cloudnative", shell=True)
    start_cloud_time = time.time()
    print("git clone -b %s https://gitee.com/zettadb/cloudnative.git" % (Version))
    subprocess.run("git clone -b %s https://gitee.com/zettadb/cloudnative.git" % (Version), shell=True)
    end_cloud_time = time.time()
    final_cloud_time = end_cloud_time - start_cloud_time 
    print('clone cloudnative: %.2f s' % (final_cloud_time))
    thirdPart_downList = ['hadoop-3.3.1.tar.gz', 'jdk-8u131-linux-x64.tar.gz', 'mysql-connector-python-2.1.3.tar.gz', 'prometheus.tgz', 'haproxy-2.5.0-bin.tar.gz', 'efk/filebeat-7.10.1-linux-x86_64.tar.gz']
    kunlun_downList = ['kunlun-cluster-manager-%s.tgz' % (ProductVersion), 'kunlun-node-manager-%s.tgz' % (ProductVersion), 'kunlun-server-%s.tgz' % (ProductVersion), 'kunlun-storage-%s.tgz' % (ProductVersion), 'kunlun-proxysql-%s.tgz' % (ProductVersion)]
    print('download component ...')
    start_downl_time = time.time()
    for i in thirdPart_downList:
        Url = "%s/thirdparty/%s" % (Link, str(i))
        print("\ndownloading %s ..."% (i))
        wget.download(Url)
    for i in kunlun_downList:
        Url = "%s/dailybuilds/enterprise/%s" % (Link, str(i))
        print("\ndownloading %s ..." % (Url))
        wget.download(Url)
    end_downl_time = time.time()
    final_downl_time = end_downl_time - start_downl_time
    print('\ndownload component : %.2f s' % (final_downl_time))
    subprocess.run("mv *gz* cloudnative/cluster/clustermgr", shell=True)
    subprocess.run("cp %s cloudnative/cluster" % (Deploy), shell=True)
    start_deploy_time = time.time()
    print('start deploy KunlunBase ...')
    deploy_command = "cd cloudnative/cluster && python2 setup_cluster_manager.py --config %s --action install --defuser %s --product_version %s" % (Deploy, User, ProductVersion)
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
    ps.add_argument("--link", default='http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/', type=str, help='Kunlun-component download link')
    ps.add_argument("--version", default='1.1', type=str, help='cloudnative version')
    ps.add_argument("--product_version", default='1.1.2', type=str, help='KunlunBase version')
    args = ps.parse_args()
    Version = args.version
    ProductVersion = args.product_version
    User = args.user
    Deploy = args.depoly
    Link = args.link
    print(args)
    start_time = time.time()
    deploy_cluster()
    end_time = time.time()
    spend_time = end_time - start_time
    print("本次安装部署花费了：%.2f 秒" % (spend_time))
