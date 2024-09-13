import subprocess
from base.other.getconf import *
from case.general_test import *


def run_shell(comm):
    print(comm)
    p = subprocess.Popen(comm, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    res = p.stdout.read().decode("utf-8").replace('\n', ' ').split(' ')
    return res


def split_conf(conf_str):
    res = str(conf_str).replace(' ', '').split(',')
    return res


class CdcOpt:
    def __init__(self):
        self.conf = get_conf_info().cdc_info()

    def action(self, act='start'):
        # act = stop | start
        conf = self.conf

        def run_act(cdc_host_list, cdc_user_list, cdc_home_list):
            show_topic('开始[%s]cdc' % act, 2)
            for i in range(len(cdc_host_list)):
                cdc_bin = "%s/bin" % cdc_home_list[i]
                act_comm = "ssh %s@%s 'cd %s; bash ./%s_kunlun_cdc.sh'" % (cdc_user_list[i], cdc_host_list[i], cdc_bin, act)
                print(act_comm)
                res = run_shell(act_comm)
                print(res)

        cdc_host, cdc_port = split_conf(conf['cdc_host_1']), split_conf(conf['cdc_port_1'])
        cdc_user, cdc_home = split_conf(conf['cdc_user_1']), split_conf(conf['cdc_home_1'])
        run_act(cdc_host_list=cdc_host, cdc_user_list=cdc_user, cdc_home_list=cdc_home)
        if conf['cdc_host_2']:
            cdc_host, cdc_port = split_conf(conf['cdc_host_2']), split_conf(conf['cdc_port_2'])
            cdc_user, cdc_home = split_conf(conf['cdc_user_2']), split_conf(conf['cdc_home_2'])
            run_act(cdc_host_list=cdc_host, cdc_user_list=cdc_user, cdc_home_list=cdc_home)

    def clean_data(self):
        conf = self.conf

        def run_act(cdc_host_list, cdc_home_list, cdc_user_list):
            show_topic('开始清除cdc数据目录', 2)
            for i in range(len(cdc_host_list)):
                cdc_data = "%s/data" % cdc_home_list[i]
                clean_comm = "ssh %s@%s 'cd %s; rm -rf *'" % (cdc_user_list[i], cdc_host_list[i], cdc_data)
                print(clean_comm)
                res = run_shell(clean_comm)
                print(res)

        cdc_host, cdc_port = split_conf(conf['cdc_host_1']), split_conf(conf['cdc_port_1'])
        cdc_user, cdc_home = split_conf(conf['cdc_user_1']), split_conf(conf['cdc_home_1'])
        run_act(cdc_host_list=cdc_host, cdc_user_list=cdc_user, cdc_home_list=cdc_home)
        if conf['cdc_host_2']:
            cdc_host, cdc_port = split_conf(conf['cdc_host_2']), split_conf(conf['cdc_port_2'])
            cdc_user, cdc_home = split_conf(conf['cdc_user_2']), split_conf(conf['cdc_home_2'])
            run_act(cdc_host_list=cdc_host, cdc_user_list=cdc_user, cdc_home_list=cdc_home)


class MariadbOpt:
    def __init__(self):
        self.conf = get_conf_info().cdc_info()

    def start(self):
        conf = self.conf

        def run_act(mariadb_home_list, mariadb_host_list, mariadb_sys_user_list, mariadb_data_list, defaults_file_list):
            show_topic('开始[start]mariadb', 2)
            for i in range(len(mariadb_host_list)):
                cat_comm = "ssh %s@%s 'cd %s; /bin/sh ./bin/mysqld_safe --defaults-file=%s --datadir=%s --user=%s'" % \
                           (mariadb_sys_user_list[i], mariadb_host_list[i], mariadb_home_list[i], defaults_file_list,
                            mariadb_data_list[i], mariadb_sys_user_list[i])
                print(cat_comm)
                res = run_shell(cat_comm)
                print(res)

        mariadb_home, mariadb_host, mariadb_user = split_conf(conf['mariadb_home_1']), split_conf(
            conf['mariadb_host_1']), split_conf(conf['mariadb_sys_user_1'])
        mariadb_data, mariadb_de_file = split_conf(conf['mariadb_data_1']), split_conf(conf['mariadb_defaults_file_1'])
        run_act(mariadb_home, mariadb_host, mariadb_user, mariadb_data, mariadb_de_file)
        if conf['mariadb_host_2']:
            mariadb_home, mariadb_host, mariadb_user = split_conf(conf['mariadb_home_2']), split_conf(
                conf['mariadb_host_2']), split_conf(conf['mariadb_sys_user_2'])
            mariadb_data, mariadb_de_file = split_conf(conf['mariadb_data_2']), split_conf(
                conf['mariadb_defaults_file_2'])
            run_act(mariadb_home, mariadb_host, mariadb_user, mariadb_data, mariadb_de_file)
