import random
import time
from case import pg_dump_restore, consfail_sql, transfer_case, other_function
import argparse


global succ_list, fail_list
succ_list, fail_list = [], []

def gen_res_dict(case_list, column_name):
    case_name = case_list[0]
    case_res = case_list[1]
    if case_res == 1:
        succ_list.append([column_name, case_name])
    elif case_res == 0:
        fail_list.append([column_name, case_name])
    time.sleep(3)

def gen_res_list(case_list):
    case_name = case_list[0]
    case_res = case_list[1]
    if case_res == 1:
        succ_list.append(case_name)
    else:
        fail_list.append(case_name)
    time.sleep(3)

def test_pg_dump_restore():
    action = ['db', 'table', 'only_data', 'only_create_table', 'multi_table']
    pg_dump_restore.TestPgDumpRestore().download_server()
    for act in action:
        # 下面三行是检查展示结果函数是否正常的，不重要
        """
        for column in 'pg_dump', 'psql_restore', 'pg_restore':
            tmp_res = random.randint(0, 1)
            gen_res_dict([act, tmp_res], column_name=column)
        """
        case = pg_dump_restore.TestPgDumpRestore()
        # 这里是导出常规sql文件，就是用psql导入的测试
        gen_res_dict(case.dump_case(dump_type=act), column_name='pg_dump')
        gen_res_dict(case.psql_case(psql_type=act), column_name='psql_restore')
        # 这里是归档的测试，就是用pg_restore导入的测试
        gen_res_dict(case.dump_case(dump_type=act, fc=1), column_name='pg_dump_Fc')
        gen_res_dict(case.restore_case(restore_type=act), column_name='pg_restore')


def consfail_case():
    case = consfail_sql.TestCase()
    gen_res_list(case.deal_lock())
    gen_res_list(case.isolation_test())

def function_case():
    # case = transfer_case.TestCase()
    # case.drop_all_func()
    # case.create_table()
    # gen_res_list(case.trigger_test())
    # gen_res_list(case.function_test())
    # gen_res_list(case.stored_procedure())
    # gen_res_list(case.drop_all_func())
    case = other_function.TestCase()
    # gen_res_list(case.cursor_case())
    # gen_res_list(case.view_case())
    # gen_res_list(case.repeatable_read())
    gen_res_list(case.tablegroup())

def show_result_list():
    succ_times = len(succ_list)
    fail_times = len(fail_list)
    total_times = succ_times + fail_times
    print('%s %s %s' % ('=' * 10, '结果', '=' * 10))
    print('本次总共 [%s] 条用例, 其中成功 [%s] 条， 失败 [%s] 条' % (total_times, succ_times, fail_times))
    print('成功项为: %s' % succ_list)
    print('失败项为: %s' % fail_list)
    print('%s %s %s' % ('=' * 10, '结果', '=' * 10))

def show_result_table(case):
    if case == 'pg_dump_restore':
        columns = ['pg_dump', 'psql_restore', 'pg_dump_Fc', 'pg_restore']
        case_list = ['db', 'table', 'only_data', 'only_create_table', 'multi_table']
    # 这里先把表格列名打出来
    title = '|| %-20s ||' % 'case_name'
    for column in columns:
        len_col = len(column)
        if len_col <= 6:
            len_col = 6
        title += f" %-{len_col}s ||" % column
    title_len = len(title)
    print('_' * title_len)
    print(title)
    print('-' * title_len)
    # 开始展示case结果
    for case in case_list:
        case_row = '|| %-20s ||' % case
        # 先把每个列的结果分别放到临时的表里面
        tmp_succ_list, tmp_fail_list = [], []
        for succ in succ_list:
            if case in succ:
                tmp_succ_list.append(succ[0])
        for fail in fail_list:
            if case in fail:
                tmp_fail_list.append(fail[0])
        # 根据上面的临时表生成最终展示的行
        for column in columns:
            len_col = len(column)
            if len_col <= 6:
                len_col = 6
            if column in tmp_succ_list:
                case_row += f' %-{len_col}s ||' % ' succ'
            elif column in tmp_fail_list:
                case_row += f' %-{len_col}s ||' % '!fail!'
            else:
                case_row += f' %-{len_col}s ||' % " None"
        print(case_row)
    print('-' * title_len)
    succ_times = len(succ_list)
    fail_times = len(fail_list)
    total_times = succ_times + fail_times
    print("======== 结果 ========")
    print("本次总共 [%s] 项测试" % total_times)
    print("    成功 [%s] 项" % succ_times)
    print("    失败 [%s] 项" % fail_times)
    print("======== 结果 ========")

def run(case):
    if case == 'pg_dump_restore':
        test_pg_dump_restore()
    elif case == 'consfail_test':
        consfail_case()
    elif case == 'function_case':
        function_case()

    if case == 'pg_dump_restore':
        show_result_table(case)
    else:
        show_result_list()

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='sql test')
    ps.add_argument('--case', help='[pg_dump_restore]|[consfail_test]|[function_case]')
    args = ps.parse_args()
    case = args.case
    run(case)