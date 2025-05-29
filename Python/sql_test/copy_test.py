from case import copy_case
from res import read, other
import time
import random


global res_list
res_list = []

def get_res(case_list):
    global res_list
    if not res_list:
        num = 1
    else:
        num = len(res_list) + 1
    tmp_res = "|| %-8s " % num
    tmp_res += case_list[0]
    if case_list[1] == 1:
        tmp_res += ' %-6s ||' % ' SUCC '
    else:
        tmp_res += ' %-6s ||' % '!FAIL!'
        print(tmp_res)
    res_list.append(tmp_res)

def test():
    num = 0
    copy = ['to', 'from']
    delimiter_list = [',', '-', '=', '|', '&']
    delimiter = []
    for i in range(2):
        tmp_delimiter = random.choice(delimiter_list)
        while tmp_delimiter in delimiter:
            tmp_delimiter = random.choice(delimiter_list)
        delimiter.append(tmp_delimiter)
    header = [1, 0]
    encoding_list = [0, 'utf-8', 'gb2312']
    quote_list = [',', '-', '=', '|', '&']
    # 删除掉和delimiter相同的元素
    # delimiter 和quote的符号在同一个copy语句里面不能相同
    quote = []
    for i in range(2):
        tmp_quote = random.choice(quote_list)
        while tmp_quote in quote or tmp_quote in delimiter:
            tmp_quote = random.choice(quote_list)
        quote.append(tmp_quote)
    where_id = [1, 0] # pg12后才支持，故跳过该测试
    force_quote = [0, 1]
    specify_columns = [1, 0]
    for de in delimiter:
        for hd in header:
            for en in encoding_list:
                # for wi in where_id:
                for sc in specify_columns:
                    for qt in quote:
                        if qt == de:
                            continue
                        for fq in force_quote:
                            case = copy_case.Copy()
                            # 这里如果存在指定列，则要导出和导入都要指定相同的列，否则会失败
                            # 所以在这个循环里面会重置一次指定的列，确保接下来的copy to 和copy from是指定相同的列
                            if sc == 1:
                                sc_value = other.rand_column_names()
                            else:
                                sc_value = 0
                            for cp in copy:
                                num += 1
                                print('第 [%s] 条用例：' % num)
                                try:
                                    get_res(case.run_case(opt=cp, header=hd, delimiter=de, encoding=en, quote=qt,
                                                          force_quote=fq,specify_columns=sc_value))
                                except:
                                    print('本用例失败')
                                time.sleep(3)


if __name__ == '__main__':
    str_num = len(read.conf_info()['data_size']) * 2 + 9
    res_title = f"|| case_num || copy ||     specify columns      || delimiter || header || encoding || quote || " \
                f"force quote || %-{str_num}s || verify || result ||" % 'where_id'
    test()
    title_len = len(res_title)
    print('_' * title_len)
    print(res_title)
    print('-' * title_len)
    succ_times = 0
    for i in res_list:
        res = str(i).split('||')[-2]
        if 'SUCC' in res:
            succ_times += 1
        print(i)
    print('-' * title_len)
    print('======== 测试结果 ========')
    print('当前共 [%s] 项测试' % len(res_list))
    print('成功   [%s] 项' % succ_times)
    print('失败   [%s] 项' % (len(res_list) - succ_times))
    print('======== 测试结果 ========')
    if succ_times != len(res_list):
        exit(1)
    else:
        exit(0)
