import subprocess
import os
import shutil
import wget
from res import connection, read_conf


def run_shell(command):
    print('\n%s' % command)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    res = output.communicate()
    return res


def wget_cdc():
    # 在当前页面下新建一个tmp目录用来下载cdc
    cdc_version = read_conf.conf_info()['cdc_version']
    cdc = 'kunlun-cdc-%s' % (cdc_version)
    target_dir = os.path.abspath('./tmp')
    shell_rm = 'rm -rf %s; rm -rf ./%s.tgz' % (target_dir, cdc)
    run_shell(shell_rm)
    print('mkdir %s' % target_dir)
    os.mkdir(target_dir)
    cdc_url = 'http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/%s.tgz' % cdc
    print('wget %s' % cdc_url)
    wget.download(url=cdc_url)
    shell_tar = 'tar -zxf ./%s.tgz' % cdc
    run_shell(shell_tar)
    shell_mv = 'mv ./%s %s' % (cdc, target_dir)
    run_shell(shell_mv)
    cdc_abspath = os.path.abspath('./tmp/%s' % cdc)
    return cdc_abspath


def mv2all_server(abspath, file):
    # 把file给到所有server的abspath上，要所有server上都存在abspath
    sys_user = read_conf.conf_info()['sys_user']
    server_host_tuple = connection.meta().all_server_host()
    for host in server_host_tuple:
        shell_scp = 'scp %s %s@%s:%s' % (file, sys_user, host[0], abspath)
        run_shell(shell_scp)
