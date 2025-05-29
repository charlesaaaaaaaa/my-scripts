import threading

from res.cluster_info import getServer
from res.connection import *
from res.getconf import *
from time import sleep
from res.system_opt import *

class configure_server():
    def __init__(self):
        self.Infos = getServer().Infos()
        self.Path = getServer().Paths()
        self.variables = readcnf().server_settings()

    def show_variables_old(self):
        Infos = self.Infos
        variables = self.variables

        print('\n|--------|\n| server |\n|--------|')
        variable_len = 15
        for key in variables:
            if len(key) > variable_len:
                variable_len = len(key)
        first_title_name = 'variable_name'
        first_title_name += ' ' * (variable_len-len(first_title_name))
        first_title = "| %s |" % first_title_name
        times = 0
        for host in Infos:
            port_len = 0
            for infos in Infos[host]:
                port_len += 1
                times += 1
                ip_port = '%s:%s' % (infos[0], infos[1])
                first_title += ' %-20s |' % ip_port

        lines = '-' * (variable_len + (23 * times) + 4)
        print(lines)
        print(first_title)
        print(lines)
        for key in variables:
            key_name = key
            key_name += ' ' * (variable_len - len(key_name))
            reslog = '| %s |' % key_name
            sql = "show %s" % key
            for host in Infos:
                for infos in Infos[host]:
                    conn = connPg()
                    res = conn.pgReturn_other(infos[0], infos[1], infos[2], infos[3], sql)[0][0]
                    reslog += ' %-20s |' % res
            print(reslog)

    def show_variables(self):
        Infos = self.Infos
        variables = self.variables
        res_dict = {}
        host_len_dict = {}
        max_variable_len = 12 + 8

        print('\n|--------|\n| server |\n|--------|\n')
        for key in variables:
            if len(key) > max_variable_len:
                max_variable_len = len(key)
        for host in Infos:
            port_dict = {}
            for infos in Infos[host]:
                port = str(infos[1])
                port_list = []
                conn = connPg()
                for key in variables:
                    sql = 'show "%s"' % key
                    try:
                        res = conn.pgReturn_other(infos[0], infos[1], infos[2], infos[3], sql)[0][0]
                    except:
                        res = 'noRes'
                    port_list.append(res)
                port_dict.update({port: port_list})
            res_dict.update({host: port_dict})
        for host in res_dict:
            host_len = 12
            port_count = len(res_dict[host])
            port_len_dict = {}
            for port in res_dict[host]:
                tmp_port_len = 5
                for variable in res_dict[host][port]:
                    if len(variable) > tmp_port_len:
                        tmplen = len(variable)
                        tmp_port_len = tmplen
                if port_count == 1:
                    if tmp_port_len < len(host):
                        tmp_port_len = len(host)
                port_len = {port: tmp_port_len}
                port_len_dict.update(port_len)
            total_port_len = 0
            # print(port_len_dict)
            for port in port_len_dict:
                total_port_len += port_len_dict[port]
            total_port_len += (port_count - 1) * 3
            if total_port_len >= host_len:
                host_len = total_port_len
            host_len_dict.update({host: [host_len, port_len_dict]})
        # print(host_len_dict)
        first_title_name= '| variable_name \\'
        first_title = first_title_name + (' ' * (max_variable_len - len(first_title_name) - 2)) + 'host |'
        if max_variable_len <= 20:
            secone_tital = '|' + ' ' * 16 + '\port |'
        else:
            secone_tital = '|' + ' ' * (17) + '\\' + ' ' * (max_variable_len - 17 - 4) + 'port |'
        line = 0
        def empty_str(num):
            strs = ' ' * num
            return strs
        for host in host_len_dict:
            empty_str_num = host_len_dict[host][0] - len(host)
            left_empty_str_num = int(empty_str_num / 2)
            left_empty_str = empty_str(left_empty_str_num)
            right_empty_str = empty_str(empty_str_num - left_empty_str_num)
            host_column = left_empty_str + host + right_empty_str
            line += host_len_dict[host][0]
            first_title += ' %s |' % host_column
            for port in host_len_dict[host][1]:
                port_column = port + ' ' * (host_len_dict[host][1][port] - len(port))
                secone_tital += ' %s |' % port_column
        def lines(str, linenum):
            line = '|' + '%s' % str * (linenum + max_variable_len + (len(host_len_dict) * 3) + 2) + '|'
            return line
        print(lines('-', line))
        print(first_title)
        print(lines('-', line))
        print(secone_tital)
        print(lines('=', line))
        # print(res_dict)
        num = 0
        for key in variables:
            row_title = key + ' ' * (max_variable_len - len(key))
            reslog = '| %s |' % row_title
            for host in res_dict:
                for port in res_dict[host]:
                    # print(res_dict[host][num])
                    value = res_dict[host][port][num] + ' ' * (
                                host_len_dict[host][1][port] - len(res_dict[host][port][num]))
                    reslog += ' %s |' % value
            num += 1
            print(reslog)
        print(lines('-', line))

    def write_config_file(self):
        Path = self.Path
        variables = self.variables

        print('\n## setting server node ...')

        def set_signal_server(host, num):
            OF = getFile(host)
            for info in Path[host]:
                print('### thread_%s: setting server %s:%s' % (num, host, info[1]))
                for key in variables:
                    OF.replaceTxtRow(info[1], key, variables[key])

        th_list, num = [], 0
        # 这里开始多线程修改pg配置文件
        for host in Path:
            th = threading.Thread(target=set_signal_server, args=(host, num, ))
            th_list.append(th)
            th.start()
            num += 1
        for th in th_list:
            th.join()

        # for host in Path:
        #     OF = getFile(host)
        #     for info in Path[host]:
        #         print('### setting server %s:%s' % (host, info[1]))
        #         for key in variables:
        #             OF.replaceTxtRow(info[1], key, variables[key])

    def restart(self):
        Path = self.Path
        print('\n## restart server node ...')

        def thread_worker(host, basedir, port, datadir):
            datadir = str(datadir).replace('/postgresql.conf', '')
            restart_component(host).restart_pg(basedir, port, datadir)

        l = []
        for host in Path:
            for info in Path[host]:
                #print(info)
                p = threading.Thread(target=thread_worker, args=[host, info[0], info[2], info[1]])
                l.append(p)
                p.start()
        for i in l:
            i.join()

        print('sleep 30s ...\n')
        sleep(30)
