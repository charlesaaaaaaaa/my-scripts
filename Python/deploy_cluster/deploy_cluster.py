import wget, subprocess
import argparse, os
import time, shutil

def timer(func):
    def wapper(*args, **kwargs):
        start_time = time.time()
        res = func(*args, **kwargs)
        endtime = time.time()
        spend_time = endtime - start_time
        print(f'{func.__name__} 运行时间: {spend_time}')
        return res
    return wapper

@timer
def download_components(website, version, debugs, extra_site):
    thirdPart_downList = ['hadoop-3.3.1.tar.gz', 'jdk-8u131-linux-x64.tar.gz', 'mysql-connector-python-2.1.3.tar.gz',
                          'prometheus.tgz', 'haproxy-2.5.0-bin.tar.gz', 'efk/filebeat-7.10.1-linux-x86_64.tar.gz']
    kunlun_downList = ['kunlun-cluster-manager','kunlun-node-manager', 'kunlun-server','kunlun-storage', 'kunlun-proxysql']
    print('downloading components ...')
    clustermgr = './cloudnative/cluster/clustermgr'
    Link = ''
    try:
        os.mkdir('./tmp_download')
    except:
        pass
    if website == 'internal':
        Link = 'http://192.168.0.104:14000/'
    elif website == "public":
        Link = 'http://zettatech.tpddns.cn/'
    elif website == "release":
        Link = "http://zettatech.tpddns.cn:14000/releases/"
    for i in thirdPart_downList:
        file = '%s' % i
        new_path = './tmp_download/' + i
        if i == 'efk/filebeat-7.10.1-linux-x86_64.tar.gz':
            file = './%s' % ('filebeat-7.10.1-linux-x86_64.tar.gz')
            new_path = './tmp_download/' + 'filebeat-7.10.1-linux-x86_64.tar.gz'
        if os.path.exists(file) or os.path.exists(new_path):
            print('%s exists, skip ...' % i)
            try:
                shutil.move(file, new_path)
            except:
                pass
            shutil.copy(new_path, clustermgr)
            continue
        Url = "%s/thirdparty/%s" % (Link, str(i))
        print("\ndownloading %s ..." % (i))
        wget.download(Url, new_path)
        shutil.copy(new_path, clustermgr)
    if website != "release":
        if debugs == 'debug':
            Link += 'dailybuilds_debug/enterprise/'
        elif debugs == 'release':
            Link += 'dailybuilds/enterprise/'
    if extra_site != '0':
        Link += '/%s' % extra_site
    for i in kunlun_downList:
        file = '%s-%s.tgz' % (i, version)
        new_path = './tmp_download/' + file
        if os.path.exists(file) or os.path.exists(new_path):
            print('%s exists, skip ...' % i)
            try:
                shutil.move(file, new_path)
            except:
                pass
            shutil.copy(new_path, clustermgr)
            continue
        url = '%s%s' % (Link, file)
        print('downloading %s' % url)
        wget.download(url, new_path)
        print()
        shutil.copy(new_path, clustermgr)
    subprocess.run('cp -rf ./tmp_download/* ./cloudnative/cluster/clustermgr', shell=True)

@timer
def clone_cloudtive(version):
    subprocess.run('rm -rf ./cloudnative', shell=True)
    com = "git clone -b %s https://gitee.com/zettadb/cloudnative.git" % version
    print(com)
    subprocess.run(com, shell=True)

def move_configure_and_depoly(config_file, version, user):
    com = 'cp ./%s ./cloudnative/cluster' % config_file
    print(com)
    subprocess.run(com, shell=True)
    com = "cd cloudnative/cluster && python2 setup_cluster_manager.py --config %s --action install --defuser %s " \
          "--product_version %s && bash -e clustermgr/install.sh" % (config_file, user, version)
    print(com)
    subprocess.run(com, shell=True)

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='deploy klustron')
    ps.add_argument("--config", default='deploy-config.json', type=str, help='KunlunBase deploy config file, default value = "deploy-config.json"')
    ps.add_argument("--user", default='kunlun', type=str, help='KunlunBase user')
    ps.add_argument("--cloudnative_version", default='main', type=str, help='cloudnative version')
    ps.add_argument("--product_version", default='1.3.1', type=str, help='KunlunBase version')
    ps.add_argument("--extra_site", type=str, default='0')
    ps.add_argument("--downloadsite", type=str, default='public', help='[internal]|[public]|[release]')
    ps.add_argument("--downloadtype", type=str, default='release', help='[release]|[debug]')
    args = ps.parse_args()
    config = args.config
    user = args.user
    cv = args.cloudnative_version
    pv = args.product_version
    esite = args.extra_site
    website = args.downloadsite
    down_type = args.downloadtype
    @timer
    def run():
        clone_cloudtive(cv)
        download_components(website, pv, down_type, esite)
        move_configure_and_depoly(config, pv, user)
    run()
