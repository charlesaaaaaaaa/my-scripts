from res.cluster_info import getStorage
from res.connection import *
from res.getconf import *
from res.system_opt import *
import threading
from time import sleep

class configure_storage():
    def __init__(self):
        self.Infos = getStorage().Infos()
        self.Paths = getStorage().Paths()
        self.variables = readcnf().storage_settings()

    def change_variables(self):
        Infos = self.Infos
        variables = self.variables

        print('\n## setting storage node ...')
        for host in Infos:
            for infos in Infos[host]:
                print('setting storage %s: %s' % (infos[0], infos[1]))
                conn = connMy(infos[0], infos[1], infos[2], infos[3], 'mysql')
                for key in variables:
                    sql = 'SET PERSIST %s = %s' % (key, variables[key])
                    conn.myNotReturn(sql)

    def show_variables_old(self):
        Infos = self.Infos
        variables = self.variables

        print('\n|--------|\n|storage |\n|--------|')
        max_len = 15
        for key in variables:
            if len(key) > max_len:
                max_len = len(key)
        second_title_name = 'variable_name'
        second_title_name += ' ' * (max_len - len(second_title_name))
        second_title = '| %s |' % second_title_name
        times = 0
        for host in Infos:
            for infos in Infos[host]:
                times += 1
                ip_port = '%s:%s' % (infos[0], infos[1])
                second_title += ' %-20s |' % ip_port
        lines = '-' * (max_len + (23 * times) + 4)
        print(lines)
        print(second_title)
        print(lines)
        for key in variables:
            storage_var = key + ' ' * (max_len - len(key))
            stor_log = '| %s |' % storage_var
            for host in Infos:
                for infos in Infos[host]:
                    conn = connMy(infos[0], infos[1], infos[2], infos[3], 'mysql')
                    sql = 'show variables like "%s"' % key
                    res = conn.myReturn(sql)[0][1]
                    stor_log += ' %-20s |' % res
            print(stor_log)

    def show_variables(self):
        Infos = self.Infos
        variables = self.variables
        res_dict = {}
        host_len_dict = {}
        max_variable_len = 12 + 8

        print('\n|--------|\n|storage |\n|--------|\n')
        for key in variables:
            if len(key) > max_variable_len:
                max_variable_len = len(key)
        for host in Infos:
            port_dict = {}
            for infos in Infos[host]:
                port = str(infos[1])
                port_list = []
                conn = connMy(infos[0], infos[1], infos[2], infos[3], 'mysql')
                for key in variables:
                    sql = 'show variables like "%s"' % key
                    try:
                        res = conn.myReturn(sql)[0][1]
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
            #print(port_len_dict)
            for port in port_len_dict:
                total_port_len += port_len_dict[port]
            total_port_len += (port_count - 1) * 3
            if total_port_len >= host_len:
                host_len = total_port_len
            host_len_dict.update({host: [host_len, port_len_dict]})
        #print(host_len_dict)
        first_title_name= '| variable_name \\'
        first_title = first_title_name + (' ' * (max_variable_len - len(first_title_name) - 2)) + 'host |'
        secone_tital = '|' + ' ' * (max_variable_len - 1 - 12) + '\\' + ' ' * (max_variable_len - 9 - 12) + 'port |'
        #secone_tital = first_title_name + (' ' * (max_variable_len - len(first_title_name) - 2)) + 'port |'
        line = 0
        def empty_str(num):
            str = ' ' * num
            return str
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
        #print(res_dict)
        num = 0
        for key in variables:
            row_title = key + ' ' * (max_variable_len - len(key))
            reslog = '| %s |' % row_title
            for host in res_dict:
                for port in res_dict[host]:
                    #print(res_dict[host][num])
                    value = res_dict[host][port][num] + ' ' * (host_len_dict[host][1][port] - len(res_dict[host][port][num]))
                    reslog += ' %s |' % value
            num += 1
            print(reslog)
        print(lines('-', line))

    def write_config_file(self):
        Path = self.Paths
        variables = self.variables

        print("\n## write storage config file ...")
        for host in Path:
            OF = getFile(host)
            for info in Path[host]:
                print("### %s: %s" % (host, info[1]))
                for key in variables:
                    OF.replaceTxtRow(info[1], key, variables[key])

    def restart(self):
        print('\n## restart stoarge node ...')
        Path = self.Paths

        def thread_worker(host, info1, info2):
            restart_component(host).restart_db(info1, info2)

        l = []
        for host in Path:
            for info in Path[host]:
                #restart_component(host).restart_db(info[0], info[2])
                p = threading.Thread(target=thread_worker, args=[host, info[0], info[2]])
                l.append(p)
                p.start()
        for i in l:
            i.join()
        print('## sleep 30s')
        sleep(30)
