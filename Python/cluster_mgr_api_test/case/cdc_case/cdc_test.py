from base.api.cdc_api import *
from base.api.post import *
from case.general_test import *
from case.cdc_case import shell_comm


class Rcr2Cdc:
    def __init__(self):
        self.cdc_conf = getconf.get_conf_info().cdc_info()
        self.cluster_conf = getconf.get_conf_info().cluster_mgr()

    def same_meta_prepare_action(self, case_name):
        # 建立一个同元数据集群下的rcr及cdc准备工作
        for i in range(2):
            show_topic("创建一个集群", 2)
            res = cluster_setting(0).create_cluster(shard=1, nodes=2, comps=1)
            if res == 0:
                return [case_name, res]
        show_topic("创建rcr连接", 2)
        res = cluster_setting(0).create_rcr_with_thelatest_clusters()
        if res == 0:
            return [case_name, res]
        # 停此所有cdc组件
        shell_comm.CdcOpt().action('stop')
        # 清理所有cdc组件的数据目录
        shell_comm.CdcOpt().clean_data()
        # 启动所有cdc组件
        shell_comm.CdcOpt().action('start')

    def mariadb_test(self):
        # 要自己先搭建好上下游mariadb然后把对应信息写到配置文件里面
        case_name = "mariadb_test"
        self.same_meta_prepare_action(case_name)
        show_topic("当前测试用例为： [%s]" % case_name)
        conf = self.cdc_conf
        mariadb_host, mariadb_port, mariadb_user, mariadb_passwd = conf['mariadb_host_1'], conf['mariadb_port_1'], conf['mariadb_user_1'], conf['mariadb_password_1']
        first_load = 'python3 ./case/cdc_case/util/mariadb_load.py --type mysql --host %s --port %s --user %s --pwd %s' \
                     ' --dbname %s --threads 1 --table_size 10000 --tbname test1 --create_table y' % (
                     mariadb_host, mariadb_port, mariadb_user, mariadb_passwd, 'test')
        show_topic('灌数据到主mariadb节点上', 2)
        print(shell_comm.run_shell(first_load))
