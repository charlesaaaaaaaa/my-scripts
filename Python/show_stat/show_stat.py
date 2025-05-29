import argparse
import threading
import multiprocessing
import time
import pymysql
import subprocess


def get_meta(sql):
    # 连接到指定的meta节点并返回其sql结果
    host = meta.split(':')[0]
    port = int(meta.split(':')[1])
    conn = pymysql.connect(host=host, port=port, user='pgx', password='pgx_pwd', database='kunlun_metadata_db')
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return res


def run_shell(command):
    # 跑一些shell并返回打印输出
    # print(command)
    output = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')
    res = output.communicate()
    return res


def write_file(file_path, txt):
    # 写东西到指定文件里面
    with open(file_path, mode='a', encoding='utf-8') as f:
        f.write(txt)
    f.close()


def get_node_info():
    # 获取元数据下所有节点信息，返回一个字典
    cluster_mgr_sql = "select hostaddr, port from cluster_mgr_nodes where member_state = 'source';"
    meta_node_sql = 'select hostaddr, port from meta_db_nodes;'
    shard_node_sql = "select hostaddr, port from shard_nodes where status = 'active';"
    comp_node_sql = "select hostaddr, port from comp_nodes where status = 'active';"
    cluster_info = get_meta(sql=cluster_mgr_sql)
    meta_node_info = get_meta(sql=meta_node_sql)
    shard_node_info = get_meta(sql=shard_node_sql)
    comp_node_info = get_meta(sql=comp_node_sql)
    machine_list = []
    res_dict = {'cluster_mgr': cluster_info, 'metadata': meta_node_info, 'shard_node': shard_node_info, 'comp_node': comp_node_info}
    # 遍历这个字典
    for compont in res_dict:
        for node in res_dict[compont]:
            # 找到ip值，如果已经存在就不写入machine_list里面，反之则写入
            if node[0] not in machine_list:
                machine_list.append(node[0])
    res_dict['machine_info'] = machine_list
    return res_dict


def get_pid(host, port, pid_type='comp_node'):
    # 获取对应节点的pid
    if pid_type == 'comp_node':
        comm = "ssh kunlun@%s \"ps -ef | grep %s | grep -v grep | grep bin/postgres | awk '{print \\$2}'\"" % (host, port)
    elif pid_type == 'shard_node' or pid_type == 'metadata':
        comm = "ssh kunlun@%s \"ps -ef | grep %s | grep 'pid-file' | grep -v grep | awk '{print \\$2}'\"" % (host, port)
    elif pid_type == 'cluster_mgr':
        comm = "ssh kunlun@%s \"sudo lsof -i:%s | grep cluster_m | awk '{print \\$2}' | tail -1\"" % (host, port)
    res = run_shell(command=comm)
    pid = str(res[0]).replace('\n', '')
    return pid


class ShowStat:
    def __init__(self):
        self.node_info = get_node_info()

    def show_machine_cpu(self, host):
        # 主要是获取iowait[5] 和 idle[-1]两个值， 其它的不管
        # 返回一个列表
        comm = 'ssh kunlun@%s "mpstat | tail -1"' % host
        res = run_shell(command=comm)
        # print(res)
        split_list = list(filter(None, res[0].split()))
        new_string = ' '.join(split_list)
        res = new_string.split(' ')
        # print(res)
        res_list = [res[5], res[-1]]
        return res_list

    def show_machine_mem(self, host):
        # 主要看mem-total, mem-used, swap-total, swap-used
        res_list = []
        comm = 'ssh kunlun@%s "free -h | tail -2"' % host
        res_tuple = str(run_shell(command=comm)).split('\\n')
        res_list = []
        for i in range(2):
            split_list = list(filter(None, res_tuple[i].split()))
            res_list.append(split_list[1])
            res_list.append(split_list[2])
        return res_list

    def show_machine_disk(self, host, device):
        # iostat -d -p nvme0n1 | grep -w nvme0n1
        # 主要是看tps[1] kB_read/s[2] kB_wrtn/s[3]
        # 返回一个字典，key为盘符名
        res_dict = {}
        device_list = str(device).split(',')
        for dev in device_list:
            comm = 'ssh kunlun@%s "iostat -hd -p %s 1 2 | grep -w %s | tail -1"' % (host, dev, dev)
            res = run_shell(command=comm)
            split_list = list(filter(None, res[0].split()))
            new_string = ' '.join(split_list)
            res = new_string.split(' ')
            res_dict[dev] = [res[0], res[1], res[2]]
        return res_dict


    def show_node_cpu_mem(self, host, pid):
        # 获取节点的占用的cpu和mem
        # 主要是获取%CPU[2] 和%MEM[3]
        comm = 'ssh kunlun@%s "ps -u -p %s | tail -1"' % (host, pid)
        res = run_shell(command=comm)
        split_list = list(filter(None, res[0].split()))
        new_string = ' '.join(split_list)
        res = new_string.split(' ')
        res_list = [res[2], res[3]]
        return res_list

    def show_node_disk(self, host, pid):
        # 主要是获取kB_rd/s[3]   kB_wr/s[4]
        # comm = 'ssh kunlun@%s "pidstat -Hhd --dec=0 -p %s 1 1 | tail -1"' % (host, pid)
        comm = 'ssh kunlun@%s "pidstat -Hhd --Human -p %s 1 1 | tail -1"' % (host, pid)
        res = run_shell(command=comm)
        split_list = list(filter(None, res[0].split()))
        new_string = ' '.join(split_list)
        res = new_string.split(' ')
        res_list = [res[3], res[4]]
        return res_list

    def start(self):
        def show_node_pid(node_list, pid_type):
            # print(node_list, pid_type)
            node_pid_list = []
            for node in node_list:
                cur_pid = get_pid(host=node[0], port=node[1], pid_type=pid_type)
                node_pid_list.append(cur_pid)
            return node_pid_list

        def write_title(node_list, file, data_num, second_title_list, exists_port=1, f_column_title_list=None):
            # data_num就是每个节点获得的资源个数
            # 先在文件里面写入标题
            # 这里13是后面write_node_info里面一个数据占11个固定字符加' |'两个字符
            # -2是因为这里的开头'|'和最后的' |'共3个字符，但write_node_info时又在最前面加了个'|'所以再+1故-2

            # title_len = 13 * data_num - 2
            title_len = -2
            for i in second_title_list:
                title_len += i[1] + 3
            second_title = delimiter * 2
            first_title = delimiter * 2
            # 分割线
            def split_line(line_len, delim_str):
                the_line = '%s' % (delim_str * line_len)
                the_line += '\n'
                return the_line

            if f_column_title_list:
                for i in f_column_title_list:
                    if i == 'time':
                        first_title += ' %8s %s' % ('-', delimiter)
                        second_title += ' %8s %s' % (i, delimiter)
                    else:
                        first_title += ' %11s %s' % ('-', delimiter)
                        second_title += ' %11s %s' % (i, delimiter)
                first_title += delimiter
                second_title += delimiter

            # 处理二级标题
            for i in range(len(node_list)):
                for sec_title_name in second_title_list:
                    tmp = f" %{sec_title_name[1]}s %s" % (sec_title_name[0], delimiter)
                    second_title += tmp
                second_title += delimiter
            second_title += '\n'
            # 处理1级标题
            for i in node_list:
                if exists_port == 1:
                    host_port = '%s:%s' % (i[0], i[1])
                else:
                    host_port = i
                # 先获取一级标题内容长度
                len_host_port = len(host_port)
                # 再获取标题两边留白的长度
                signal_size_len = int((title_len - len_host_port) / 2)
                left_len = (title_len - len_host_port) % 2
                # 再根据各种长度组合成对应的一级标题
                title = '%s%s%s %s' % (' ' * signal_size_len, host_port, ' ' * (signal_size_len + left_len), delimiter * 2)
                first_title += title
            len_first_title = len(first_title)
            first_title += '\n'
            # 分别把1级标题和2级标题写到文件里面去
            write_file(file_path=file, txt=split_line(len_first_title, delim_str='='))
            write_file(file_path=file, txt=first_title)
            write_file(file_path=file, txt=split_line(len_first_title, delim_str='='))
            write_file(file_path=file, txt=second_title)
            write_file(file_path=file, txt=split_line(len_first_title, delim_str='-'))

        def write_node_info(node_list, file, pid_list, second_title_list):
            # 写一次占用情况
            node_dict = {}

            # 单个线程做的事
            def signal_thread(host, port, pid):
                key = '%s:%s' % (host, port)
                value = list(self.show_node_cpu_mem(host, pid))
                disk = list(self.show_node_disk(host, pid))
                value.extend(disk)
                node_dict[key] = value

            pid_index = 0
            tl = []
            for node in node_list:
                t = threading.Thread(target=signal_thread, args=(node[0], node[1], pid_list[pid_index]))
                tl.append(t)
                t.start()
                pid_index += 1
            for i in tl:
                i.join()
            data_row = delimiter * 2
            data_row += ' %8s %s' % (time.strftime('%H:%M:%S'), delimiter * 2)
            for node in node_list:
                key = '%s:%s' % (node[0], node[1])
                tmp_list = node_dict[key]
                column_index = 0
                for value in tmp_list:
                    tmp = f" %{second_title_list[column_index][1]}s %s" % (value, delimiter)
                    data_row += tmp
                    column_index += 1
                data_row += delimiter
            data_row += '\n'
            # 写到文件里面去
            write_file(file, txt=data_row)

        def comp_node_info():
            comps = self.node_info['comp_node']
            file_path = '%s/server_node.log' % output_dir
            # 这里就是展示所有的计算节点的mem cpu disk信息

            # 写标题
            # sec_title_list = ['time', '%cpu', '%mem', 'kB_rd/s', 'kB_wr/s']
            sec_title_list = [['%cpu', 6], ['%mem', 6], ['kB_rd/s', 8], ['kB_wr/s', 8]]
            write_title(comps, file_path, 5, second_title_list=sec_title_list, f_column_title_list=['time'])
            the_times = 0
            pid_list = show_node_pid(comps, 'comp_node')
            while True:
                the_times += 1
                start_time = time.time()
                write_node_info(node_list=comps, file=file_path, pid_list=pid_list, second_title_list=sec_title_list)
                if the_times == 50:
                    the_times = 0
                    pid_list = show_node_pid(comps, 'comp_node')
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def stor_node_info():
            stors = self.node_info['shard_node']
            file_path = '%s/storage_node.log' % output_dir

            # 写标题
            sec_title_list = [['%cpu', 6], ['%mem', 6], ['kB_rd/s', 8], ['kB_wr/s', 8]]
            write_title(stors, file_path, 5, second_title_list=sec_title_list, f_column_title_list=['time'])
            the_times = 0
            pid_list = show_node_pid(stors, 'shard_node')
            while True:
                the_times += 1
                start_time = time.time()
                write_node_info(node_list=stors, file=file_path, pid_list=pid_list, second_title_list=sec_title_list)
                if the_times == 50:
                    the_times = 0
                    pid_list = show_node_pid(stors, 'shard_node')
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def cluster_node_info():
            clusters = self.node_info['cluster_mgr']
            file_path = '%s/cluster_mgr.log' % output_dir

            # 写标题
            sec_title_list = [['%cpu', 6], ['%mem', 6], ['kB_rd/s', 8], ['kB_wr/s', 8]]
            write_title(clusters, file_path, 5, second_title_list=sec_title_list, f_column_title_list=['time'])
            the_times = 0
            pid_list = show_node_pid(clusters, 'cluster_mgr')
            while True:
                the_times += 1
                start_time = time.time()
                write_node_info(node_list=clusters, file=file_path, pid_list=pid_list, second_title_list=sec_title_list)
                if the_times == 50:
                    the_times = 0
                    pid_list = show_node_pid(clusters, 'cluster_mgr')
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def meta_node_info():
            metas = self.node_info['metadata']
            file_path = '%s/metadata.log' % output_dir

            # 写标题
            sec_title_list = [['%cpu', 6], ['%mem', 6], ['kB_rd/s', 8], ['kB_wr/s', 8]]
            write_title(metas, file_path, 5, second_title_list=sec_title_list, f_column_title_list=['time'])
            the_times = 0
            pid_list = show_node_pid(metas, 'metadata')
            # print(pid_list)
            while True:
                start_time = time.time()
                the_times += 1
                write_node_info(node_list=metas, file=file_path, pid_list=pid_list, second_title_list=sec_title_list)
                if the_times == 50:
                    the_times = 0
                    pid_list = show_node_pid(metas, 'metadata')
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def machine_cpu_info():
            machine_list = self.node_info['machine_info']
            file_path = '%s/cpu.log' % output_dir
            # 写标题
            sec_title_list = [['%iowait', 7], ['%idle', 6]]
            write_title(machine_list, file_path, 3, exists_port=0, second_title_list=sec_title_list, f_column_title_list=['time'])
            cpu_dict = {}

            # 单次线程要做的事
            def signal_thread(host):
                res = self.show_machine_cpu(host)
                cpu_dict[host] = res
            while True:
                cpu_dict = {}
                tl = []
                start_time = time.time()
                for machine in machine_list:
                    t = threading.Thread(target=signal_thread, args=(machine,))
                    tl.append(t)
                    t.start()
                for i in tl:
                    i.join()
                data_row = delimiter * 2
                data_row += ' %8s %s' % (time.strftime('%H:%M:%S'), delimiter * 2)
                for machine in machine_list:
                    column_index = 0
                    for cpu_info in cpu_dict[machine]:
                        data_row += f" %{sec_title_list[column_index][1]}s %s" % (cpu_info, delimiter)
                        column_index += 1
                    data_row += '|'
                data_row += '\n'
                write_file(file_path=file_path, txt=data_row)
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def machine_mem_info():
            machine_list = self.node_info['machine_info']
            file_path = '%s/mem.log' % output_dir
            # 写标题
            sec_title_list = [['mem-to', 6], ['mem-us', 6], ['swa-to', 6], ['swa-us', 6]]
            write_title(machine_list, file_path, 5, exists_port=0, second_title_list=sec_title_list, f_column_title_list=['time'])
            mem_dict = {}

            # 单次线程要做的事
            def signal_thread(host):
                res = self.show_machine_mem(host)
                mem_dict[host] = res

            while True:
                mem_dict = {}
                tl = []
                start_time = time.time()
                for machine in machine_list:
                    t = threading.Thread(target=signal_thread, args=(machine,))
                    tl.append(t)
                    t.start()
                for i in tl:
                    i.join()
                data_row = delimiter * 2
                data_row += ' %8s %s' % (time.strftime('%H:%M:%S'), delimiter * 2)
                for machine in machine_list:
                    column_index = 0
                    for cpu_info in mem_dict[machine]:
                        data_row += f" %{sec_title_list[column_index][1]}s %s" % (cpu_info, delimiter)
                        column_index += 1
                    data_row += delimiter
                data_row += '\n'
                write_file(file_path=file_path, txt=data_row)
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        def machine_disk_info():
            machine_list = self.node_info['machine_info']
            file_path = '%s/disk.log' % output_dir
            # 写标题
            title_len = len(disk_device.split(',')) * 4
            sec_title_list = [['tps', 8], ['read/s', 8], ['wrtn/s', 8]]
            # sec_title_list = ['time', 'tps', 'read/s', 'wrtn/s']
            write_title(machine_list, file_path, 4, exists_port=0, second_title_list=sec_title_list, f_column_title_list=['time', 'device_name'])
            disk_dict = {}

            # 单次线程要做的事
            def signal_thread(host):
                res = self.show_machine_disk(host, disk_device)
                # print(res)
                for dev_name in res:
                    if dev_name not in disk_dict:
                        disk_dict[dev_name] = {host: res[dev_name]}
                    else:
                        disk_dict[dev_name].update({host: res[dev_name]})
                # disk_dict[host] = res

            while True:
                disk_dict = {}
                tl = []
                start_time = time.time()
                for machine in machine_list:
                    t = threading.Thread(target=signal_thread, args=(machine,))
                    tl.append(t)
                    t.start()
                for i in tl:
                    i.join()
                # print(disk_dict)
                for devive_name in disk_dict:
                    data_row = '%s %8s | %11s %s' % (delimiter * 2, time.strftime('%H:%M:%S'), devive_name, delimiter * 2)
                    for host in disk_dict[devive_name]:
                        column_index = 0
                        for disk_info in disk_dict[devive_name][host]:
                            data_row += f" %{sec_title_list[column_index][1]}s %s" % (disk_info, delimiter)
                            column_index += 1
                        data_row += delimiter
                    data_row += '\n'
                    write_file(file_path=file_path, txt=data_row)
                end_time = time.time()
                spend_time = end_time - start_time
                sleep_time = interval - spend_time
                time.sleep(sleep_time)

        # 开启多进程
        pl = []
        p = multiprocessing.Process(target=comp_node_info)
        pl.append(p)
        p = multiprocessing.Process(target=stor_node_info)
        pl.append(p)
        p = multiprocessing.Process(target=meta_node_info)
        pl.append(p)
        p = multiprocessing.Process(target=cluster_node_info)
        pl.append(p)
        p = multiprocessing.Process(target=machine_cpu_info)
        pl.append(p)
        p = multiprocessing.Process(target=machine_mem_info)
        pl.append(p)
        p = multiprocessing.Process(target=machine_disk_info)
        pl.append(p)
        for p in pl:
            p.start()
        # 限制运行时间
        if run_time <= 0:
            for p in pl:
                p.join()
        else:
            time.sleep(run_time)
        for p in pl:
            p.terminate()


if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='收集通过从指定的meta节点下在运行的所有节点机器信息并获取对应的资源占用情况\n过程中产生的cpu.log disk.log mem.log是集群所在的机器的总资源占用情况\n另外四个log文件是集群组件进程的资源占用情况')
    ps.add_argument('--meta', help='meta节点信息，如192.168.0.1:3306', type=str)
    ps.add_argument('--output', type=str, default='./show_stat', help='输出结果的目录, 默认./show_stat')
    ps.add_argument('--interval', type=int, default=10, help='每次检查间隔的时间, 默认10s')
    ps.add_argument('--delimiter', type=str, default='|', help='每个值之前的分割符， 默认"|"')
    ps.add_argument('--disk_device', type=str, help='硬盘盘符，超过1个盘符时用逗号隔开, 默认"nvme0n1,nvme1n1"', default='nvme0n1,nvme1n1')
    ps.add_argument('--runtime', type=int, help='该脚本的运行时间，以秒记，默认为0则不限制', default=0)
    args = ps.parse_args()
    meta = args.meta
    output_dir = args.output
    interval = args.interval
    delimiter = args.delimiter
    disk_device = args.disk_device
    run_time = args.runtime
    ShowStat().start()

