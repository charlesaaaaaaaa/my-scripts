import argparse

def test():
    with open(expected, 'r', encoding='utf-8') as f:
        expected_content = f.readlines()
    with open(output, 'r', encoding='utf-8') as f:
        output_content = f.readlines()
    write_err = open('./err.diff', 'a', encoding='utf-8')
    select_query = ['select', 'SELECT']
    start_signal, stop_signal = 0, 0
    expected_list = []
    select_start = 0
    total_select_count = 0
    fail_select_count = 0
    f_name = '%s:' % str(output).split('/')[-1]
    file_name_times = 0
    global output_rownum
    output_rownum = 0
    def get_output_select(select_row, start_num):
        output_start_signal = 0
        output_list = []
        output_stop_signal = 0
        output_select_start = 0
        global output_rownum
        #for num in range(output_rownum, output_len):
        new_start_num = 0
        for output_row in output_content:
            new_start_num += 1
            if new_start_num < start_num:
                continue
            #print(output_stop_signal, output_start_signal, output_start_signal, output_row)
            if 'EXPLAIN' in output_row or 'explain' in output_row:
                output_stop_signal = 1
                continue
            if ';' in output_row and output_stop_signal == 1:
                output_stop_signal = 0
                continue
            # if '======' in output_row and output_select_start == 0:
            #     continue
            if 'SELECT' in output_row and output_stop_signal == 0 or 'select' in output_row and output_stop_signal == 0:
                output_start_signal = 1
                output_select_start = 1
                output_list.append('')
            if output_select_start == 1:
                output_list[0] += output_row
                #print(output_list)
                if ';' in output_row:
                    output_select_start = 0
                    if output_list[0] != select_row:
                        output_start_signal = 0
                        output_list = []
                continue
            #print('output: %s %s %s %s %s' % (output_start_signal, output_stop_signal, output_select_start, output_row, output_list))
            if '\n' == output_row:
                continue
            if output_start_signal == 1 and output_select_start == 0:
                output_list.append(output_row)
                if 'row)' in output_row or 'rows)' in output_row or 'ERROR' in output_row or '=======' in output_row:
                    output_list = list(filter(None, output_list))
                    num = 0
                    for i in output_list:
                        if '========' == i:
                            del output_list[num]
                        num += 1
                    #print(output_list, new_start_num)
                    return output_list, new_start_num

    def write_err_log(lists, type):
        write_err.write('\n%s:\n' % type)
        for i in lists:
            if i != lists[0]:
                write_err.write(i)
    start_num = 0
    for exp_row in expected_content:
        exp_sp = exp_row.split(' ')
        if 'EXPLAIN' in exp_row or 'explain' in exp_row:
            stop_signal = 1
            continue
        elif ';' in exp_row and stop_signal == 1:
            stop_signal = 0
            start_signal = 0
            continue
        #print(start_signal, stop_signal, exp_row)
        if exp_sp[0] in select_query:
            start_signal = 1
            expected_list.append('')
            select_start = 1
        if start_signal == 1 and stop_signal == 0:
            if select_start == 1:
                expected_list[0] += exp_row
                if ';' in exp_row:
                    select_start = 0
                continue
            expected_list.append(exp_row)
            if 'row)' in exp_row or 'rows)' in exp_row or 'ERROR' in exp_row:
                start_signal = 0
                expected_list = list(filter(None, expected_list))
                total_select_count += 1
                #print(expected_list[0])
                output_list, new_start_num = get_output_select(expected_list[0], start_num)
                start_num = new_start_num
                fail_signal = 0
                for num in range(len(expected_list)):
                    try:
                        exp_r = expected_list[num]
                        out_r = output_list[num]
                    except:
                        pass
                    if exp_r != out_r:
                        err_exp_r = ''
                        err_out_r = ''
                        for i in exp_r:
                            if ' ' != i:
                                err_exp_r += i
                        for i in out_r:
                            if ' ' != i:
                                err_out_r += i
                        if err_out_r != err_exp_r:
                            fail_signal = 1
                            #print('exp: %s' % err_exp_r)
                            #print('out: %s' % err_out_r)
                if fail_signal == 1:
                    fail_select_count += 1
                    #print('%s rows' % start_num)
                    #print(expected_list[0])
                    #print('exp: %s\n' % expected_list)
                    #print('out: %s\n========' % output_list)
                    if file_name_times == 0:
                        len_f_name = len(f_name)
                        write_err.write('=' * len_f_name + '|')
                        write_err.write('\n%s' % f_name + '|\n')
                        write_err.write('=' * len_f_name + '|' + '\n\n')
                        file_name_times = 1
                    select_len = len(expected_list[0])
                    write_err.write('v' * select_len + '\n')
                    write_err.write(expected_list[0])
                    write_err_log(expected_list, 'expected')
                    write_err_log(output_list, 'output')
                    write_err.write('^' * select_len + '\n\n')
                expected_list = []
                continue
    total_query = 'select query count: %s' % total_select_count
    fail_query = 'fail query count: %s' % fail_select_count
    print('=' * 25 + '|')
    print('%s' % f_name + ' ' * (25 - len(f_name)) + '|')
    print( total_query + ' ' * (25 - len(total_query)) + '|')
    print( fail_query + ' ' * (25 - len(fail_query)) + '|')
    print('=' * 25 + '|\n')

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='diff expected file and output file')
    ps.add_argument('--expected', default='dml.out', type=str, required=True, help='expected file')
    ps.add_argument('--output', default='k_dml.out', type=str, required=True, help='output file')
    args = ps.parse_args()
    expected = args.expected
    output = args.output
    test()
