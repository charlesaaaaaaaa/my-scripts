import random
from bin import other_opt
from xpanel_case import cluster_manage, load
import time


global succ_dict, fail_dict
succ_dict = {'metadata': [], 'cluster_mgr': [], 'xpanel': []}
fail_dict = {'metadata': [], 'cluster_mgr': [], 'xpanel': []}


def gen_res_list(case_list, consfailover_type):
    global succ_dict, fail_dict
    case_name = case_list[0]
    res = case_list[1]
    if res == 1:
        succ_dict[consfailover_type].append(case_name)
    else:
        fail_dict[consfailover_type].append(case_name)


def run_test():
    # 先把所有的元数据节点信息放到一个配置文件里面去
    other_opt.init_config()
    load.loading().load_and_change_pwd()
    # load.loading().load_and_change_pwd()
    for consfail_num in range(1, 4):
        # 这里1到3是为了传参给对应的case的
        # 当为1时会kill 元数据主， 当为2时会kill cluster_mgr 主
        # 当为3时会重启xpanel
        if consfail_num == 1:
            consfailover = 'metadata'
        elif consfail_num == 2:
            consfailover = 'cluster_mgr'
        elif consfail_num == 3:
            consfailover = 'xpanel'
        print("\n================|================\n现在在测试 "
              "[%s] 异常情况\n================|================" % consfailover)
        # 下面这一段是用来检查后面show_result函数是否能正常输出结果的
        # tmp_case_list = ['创建集群', '删除集群', '增加shard', '删除shard', '增加计算节点', '删除计算节点', '增加存储节点', '删除存储节点']
        # for i in tmp_case_list:
        #     rand_res = random.randint(0, 5)
        #     if rand_res == 0:
        #         tmp_res = 0
        #     else:
        #         tmp_res = 1
        #     tmp_res_list = [i, tmp_res]
        #     gen_res_list(tmp_res_list, consfailover)
        gen_res_list(cluster_manage.cluster_list().add_new_cluster(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().add_storage(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().add_comp(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().add_shard(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().del_shard(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().del_comp(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().del_replica(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().rebuild_node(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().manual_swich_master(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().unswitch_setting(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().delete_all_cluster(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().add_new_cluster(consfailover=consfail_num, install_proxysql=1), consfailover)
        gen_res_list(cluster_manage.cluster_list().manual_backup(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().manual_restron(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().logic_backup(consfailover=consfail_num), consfailover)
        gen_res_list(cluster_manage.cluster_list().logic_restore(consfailover=consfail_num), consfailover)
        # gen_res_list(cluster_list().config_variables())
        # gen_res_list(cluster_list().monitor())
        # gen_res_list(cluster_list().tmp())
        # gen_res_list(alarm_test().start_alarm())


def show_result():
    global succ_dict, fail_dict
    case_list = []
    title = '|| %-20s || kill_metadata || kill_cluster_mgr || restart_xpanel ||' % 'case'
    print('_' * len(title))
    print(title)
    print('-' * len(title))
    # 把所有的case名收集起来到一个列表里面去
    for case_name in succ_dict['metadata']:
        case_list.append(case_name)
    for case_name in fail_dict['metadata']:
        case_list.append(case_name)
    for case in case_list:
        # cur_case = '|| %-15s ' % case
        cases = len(str(case).encode('GB2312'))
        left_len = 20 - cases
        cur_case = "|| %s%s " % (case, ' ' * left_len)

        # 查看结果的
        def show_case_result(case, consfailover):
            if case in succ_dict[consfailover]:
                res = 'SUCC'
            elif case in fail_dict[consfailover]:
                res = '!FAIL!'
            return res
        # metadata
        cur_case += '|| %-13s ' % show_case_result(case, 'metadata')
        # cluster_mgr
        cur_case += '|| %-16s ' % show_case_result(case, 'cluster_mgr')
        # xoanel
        cur_case += '|| %-15s' % show_case_result(case, 'xpanel')
        cur_case += '||'
        print(cur_case)
    print('-' * len(title))


if __name__ == '__main__':
    run_test()
    show_result()
    succ_num = len(succ_dict['metadata']) + len(succ_dict['cluster_mgr']) + len(succ_dict['xpanel'])
    fail_num = len(fail_dict['metadata']) + len(fail_dict['cluster_mgr']) + len(fail_dict['xpanel'])
    total_cases = succ_num + fail_num
    print('======== result ========')
    print('当前总共 【%s】 项测例' % total_cases)
    print('    成功 【%s】 项测例' % succ_num)
    print('    失败 【%s】 项测例' % fail_num)
    print('======== result ========')
