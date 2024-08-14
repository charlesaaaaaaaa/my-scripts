from case.ticket_case import ticket_1930
from case.daily_test import smoke_test, caict_test
import argparse

global succ_list, fail_list
succ_list, fail_list = [], []


def case_res(res_list):
    global succ_list, fail_list
    case_name = res_list[0]
    case_result = res_list[1]
    if case_result == 1:
        succ_list.append(case_name)
    elif case_result == 0:
        fail_list.append(case_name)


def ticket_test():
    case_res(ticket_1930.test_case())


def daily_test():
    test_suite = smoke_test.TestCase(2)
    case_res(test_suite.install_cluster())
    case_res(test_suite.add_comps())
    case_res(test_suite.add_shards())
    case_res(test_suite.add_nodes())
    case_res(test_suite.rebuild_nodes())
    case_res(test_suite.del_comps())
    case_res(test_suite.del_nodes())
    case_res(test_suite.del_shard())
    case_res(test_suite.del_cluster())
    case_res(test_suite.cluster_backup_restore())
    case_res(test_suite.cluster_table_repartition())
    case_res(test_suite.expand_cluster())
    case_res(test_suite.centos_logicalbackup_restore())
    case_res(test_suite.mirror_tables())
    case_res(test_suite.rcr_smoke())
    case_res(test_suite.expand_tg())
    case_res(test_suite.install_rbrcluster_degrade())


def caict():
    test = caict_test.CaictCase(2)
    case_res(test.check_metadata_117())
    case_res(test.wr_split_118())
    case_res(test.cluster_data_backup_312())
    case_res(test.cluster_data_restore_313())
    case_res(test.resource_split_314())
    case_res(test.balanced_distribution_hash_502())
    case_res(test.online_expand_503())


if __name__ == "__main__":
    ps = argparse.ArgumentParser(description='cluster_mgr test script')
    ps.add_argument("--test-case", help="test suite, [daily_test]|[ticket_test]", default="daily_test")
    args = ps.parse_args()
    test_case = args.test_case
    if test_case == "daily_test":
        daily_test()
    elif test_case == "caict":
        caict()
    elif test_case == "ticket_test":
        ticket_test()
    print('======== 结果 ========')
    print('当前共测试 %s 项case：' % (len(succ_list) + len(fail_list)))
    print('成功项：%s' % succ_list)
    print('失败项：%s' % fail_list)
    print('======== 结果 ========')
    if fail_list:
        print('！！！ 测试失败  ！！！')
        exit(1)
