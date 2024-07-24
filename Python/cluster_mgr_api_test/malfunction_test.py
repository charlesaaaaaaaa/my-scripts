from case.malfunction.malfunction_create_cluster import *
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

def test(weekday):
    file_name = './log/malfunction.log'
    the_line = '\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-'
    txt = '|                     case name                      | 前期 | api  | 计算节点 | 备注 |'
    w2File().toOther(file_name=file_name, txt=txt)
    test_case = case_test()
    if weekday == 6:
        print(the_line)
        test_case.case1_malfunction(file_name)
        print(the_line)
        test_case.case2_malfunction(file_name)
        print(the_line)
        test_case.case3_malfunction(file_name)
        print(the_line)
        test_case.case4_malfunction(file_name)
        print(the_line)
        test_case.case5_malfunction(file_name)
        print(the_line)
        test_case.case6_malfunction(file_name)
        print(the_line)
        test_case.case7_malfunction(file_name)
        print(the_line)
        test_case.case8_malfunction(file_name)
        print(the_line)
        test_case.case9_malfunction(file_name)
        print(the_line)
        test_case.case10_malfunction(file_name)
        print(the_line)
        test_case.case11_malfunction(file_name)
    elif weekday == 7:
        print(the_line)
        test_case.case12_malfunction(file_name)
        print(the_line)
        test_case.case13_malfunction(file_name)
        print(the_line)
        test_case.case14_malfunction(file_name)
        print(the_line)
        test_case.case15_malfunction(file_name)
        print(the_line)
        test_case.case16_malfunction(file_name)
        print(the_line)
        test_case.case17_malfunction(file_name)
        print(the_line)
        test_case.case18_malfunction(file_name)
        print(the_line)
        test_case.case19_malfunction(file_name)
        print(the_line)
        test_case.case20_malfunction(file_name)
        print(the_line)
        test_case.case21_malfunction(file_name)
        print(the_line)
        test_case.case22_malfunction(file_name)

if __name__ == "__main__":
    ps = argparse.ArgumentParser(description='故障测试，周六日运行')
    ps.add_argument('--weekday', help='[6]|[7],6=周六，7=周日')
    args = ps.parse_args()
    weekday = args.weekday
    test(weekday)
