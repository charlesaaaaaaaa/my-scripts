from case.malfunction.malfunction_create_cluster import *

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

def test():
    file_name = './log/malfunction.log'
    test_case = case_test()
    # case 1
    test_case.case1_malfunction(file_name)
    # case 2
    test_case.case2_malfunction(file_name)
    # case 3
    test_case.case3_malfunction(file_name)
    # case 4
    test_case.case4_malfunction(file_name)
    # case 5
    test_case.case5_malfunction(file_name)
    # case 6
    test_case.case6_malfunction(file_name)
    # case 7
    test_case.case7_malfunction(file_name)
    # case 8
    test_case.case8_malfunction(file_name)
    # case 9
    test_case.case9_malfunction(file_name)
    # case 10
    test_case.case10_malfunction(file_name)
    # case 12
    test_case.case12_malfunction(file_name)
    # case 13
    test_case.case13_malfunction(file_name)
    # case 14
    test_case.case14_malfunction(file_name)
    # case 15
    test_case.case15_malfunction(file_name)
    # case 22
    test_case.case22_malfunction(file_name)

if __name__ == "__main__":
    test()
    # print('======== 结果 ========')
    # print('当前共测试 %s 项case：' % (len(succ_list) + len(fail_list)))
    # print('成功项：%s' % succ_list)
    # print('失败项：%s' % fail_list)
    # print('======== 结果 ========')
    # if fail_list:
    #     print('！！！ 测试失败  ！！！')
    #     exit(1)
