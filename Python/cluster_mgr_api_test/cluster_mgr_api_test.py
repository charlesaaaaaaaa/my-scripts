from case import ticket_1930

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
    case_res(ticket_1930.test_case())

if __name__ == "__main__":
    test()
    print('======== 结果 ========')
    print('当前共测试 %s 项case：' % (len(succ_list) + len(fail_list)))
    print('成功项：%s' % succ_list)
    print('失败项：%s' % fail_list)
    print('======== 结果 ========')
    if fail_list:
        print('！！！ 测试失败  ！！！')
        exit(1)
