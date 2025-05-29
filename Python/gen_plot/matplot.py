import matplotlib.pyplot as plt
import argparse
import os


def run():
    # 现在开始处理指定目录下所有的文件的数据，先获取指定目录下所有文件名
    filename_list = os.listdir(input_dir)
    data_dict = {}
    max_grep_list = []
    max_size = 0
    # 访问所有文件
    for file_name in filename_list:
        with open('%s/%s' % (input_dir, file_name), 'r') as f:
            data_list = f.readlines()
        # 传入了要grep的字符，则会进行处理
        if grep:
            old_max_size = len(max_grep_list)
            grep_list = []
            for i in data_list:
                # 只筛选存在该字符串的行
                if grep in i:
                    grep_list.append(i)
            if len(grep_list) > old_max_size:
                max_grep_list = grep_list.copy()
            # 再把这个行给到数据列表里面
            data_list = grep_list.copy()
        # 传入了指定awk的列，则会对数据进行处理
        if awk_line:
            for i in range(len(data_list)):
                # 使用split继续分割字符串并筛选出对应的列
                data_list[i] = int(float(data_list[i].split(' ')[awk_line - 1]))
        # 最后把处理好的数据列表以文件名为key值放到一个dict里面
        tmp_dict = {file_name: data_list}
        data_dict.update(tmp_dict)

    # 如果有传入预期的数据大小，则这里会对所有数据进行比对
    # 如果不一样则会报错并退出
    if expect_datasize:
        max_size = expect_datasize
        err_datasize_times = 0
        for data_name in data_dict:
            cur_data_size = len(data_dict[data_name])
            if cur_data_size != expect_datasize:
                print('文件[%s]与预期[%s]数据行数不符, 实际只[%s]行数据，'
                      '请检查是否文件有误或者传入错误参数' % (data_name, expect_datasize, cur_data_size))
                err_datasize_times += 1
        if err_datasize_times > 0:
            exit(1)
    else:
        # 这里没有指定预期数据长度时，会找到最大的的那个文件
        # 以他的文件数据长度为准填充其它文件的长度，不然这个plt会失败，因为长度不同
        data_size_list = []
        for data_name in data_dict:
            data_size_list.append(len(data_dict[data_name]))
        max_size = max(data_size_list)
        for data_name in data_dict:
            cur_size = len(data_dict[data_name])
            need_size = max_size - cur_size
            for i in range(need_size):
                data_dict[data_name].append(0)

    # x_label, 就是折线图里面最下面那一行的标志
    x_label_list = []
    if x_awk_line and max_grep_list:
        for i in range(len(max_grep_list)):
            x_label_list.append(max_grep_list[i].split(' ')[x_awk_line - 1])
    else:
        for i in range(1, max_size + 1):
            the_str = '%s' % i
            x_label_list.append(the_str)
    # 设置输出图形的宽和高，18:6，inch
    plt.figure(figsize=(15, 5))
    # 当只有一个数据的时候，可以不用图例，就是legend()方法
    for data_name in data_dict:
        plt.plot(x_label_list, data_dict[data_name], label=data_name)
    # 当有超过1个数据文件时，会开启图例
    if len(data_dict) > 1:
        plt.legend()
    # xticks就是设置x坐标标签的间隔步长的，interval_num通过x标签的长度来决定间隔步长，最多输出30个标签
    interval_num = int(len(x_label_list)/30)
    plt.xticks(x_label_list[::interval_num])
    # plt.bar(aspects, feelings, color=['gold', 'brown'])
    plt.title(p_title)
    plt.ylabel(p_ylabel)
    plt.xlabel(p_xlabel)
    # plt.get_current_fig_manager().set_window_title('My Plot')
    if not output:
        plt.savefig('./result/%s.png' % p_title, bbox_inches='tight', dpi=135)
    else:
        plt.savefig(output, bbox_inches='tight', dpi=135)
    # plt.show()


if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='展示折线统计图的小脚本')
    ps.add_argument('--grep', help='使用grep命令，如--grep "] thds:" == grep "] thds:"', default='] thds:')
    ps.add_argument('--awk_line', help='awk第几列数据', default=9, type=int)
    ps.add_argument('--x_awk_line', type=int, default=2,
                    help='这个是x轴的标签数据，用文件里面的指定列展示，不指定就是从1到最大数据量展示')
    ps.add_argument('--input_dir', help='放原始数据文件的目录', default='./result')
    ps.add_argument('--expect_datasize', type=int,
                    help='预期中数据文件应该存在多少行数据, 超过或者少于该数会报错，不指定则不会有该检测步骤')
    ps.add_argument('--title', help='折线统计图的标题', default='test')
    ps.add_argument('--ylabel', help='折线统计图的y轴标签名', default='Q P S')
    ps.add_argument('--xlabel', help='折线统计图的s轴标签名', default='time')
    ps.add_argument('--output', help='把图片输出到什么路径下, 默认为`input_dir`/`title`.png')
    args = ps.parse_args()
    grep = args.grep
    awk_line = args.awk_line
    x_awk_line = args.x_awk_line
    input_dir = args.input_dir
    p_title = args.title
    p_ylabel = args.ylabel
    p_xlabel = args.xlabel
    expect_datasize = args.expect_datasize
    output = args.output
    run()
