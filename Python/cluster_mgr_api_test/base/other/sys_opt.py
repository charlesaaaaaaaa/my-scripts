import os
import subprocess
from base.other import info,getconf
import threading
import random
from base.other import connect
from base.other import write_log


def run_set_variables():
    write_log.w2File().print_log('开始设置超时参数')
    variables_path = getconf.get_conf_info().cluster_mgr()['config_variables_path']
    start_script = "cd %s; python3 config_variables.py" % variables_path
    subprocess.run(start_script, shell=True)


def set_server_nodes_timeout(timeout_time=7200):
    server_node_dict = info.node_info().show_all_running_computer()
    var_list1 = ["mysql_write_timeout", "mysql_read_timeout"]
    var_list2 = ["statement_timeout", "lock_timeout", "log_min_duration_statement"]
    timeout_time_ms = timeout_time * 1000
    try:
        for server in server_node_dict:
            pg = connect.Pg(server[0], server[1], server[2], server[3], 'postgres')
            for var1 in var_list1:
                sql = 'alter system set %s = %s;' % (var1, timeout_time)
                pg.ddl_sql(sql)
            for var2 in var_list2:
                sql = 'alter system set %s = %s;' % (var2, timeout_time_ms)
                pg.ddl_sql(sql)
            pg.close()
    except Exception as err:
        print(err)
        return 0
    return 1


def set_storage_nodes_timeout(timeout_time=7200):
    timeout_time *= 1000
    storage_node_info = info.node_info().show_all_running_storage()
    var_list = ["lock_wait_timeout", "net_read_timeout", "net_write_timeout", "fullsync_timeout", "innodb_lock_wait_timeout"]
    try:
        for storage in storage_node_info:
            my = connect.My(storage[0], storage[1], storage[2], storage[3], 'mysql')
            for var in var_list:
                sql = 'set persist %s = %s' % (var, timeout_time)
                my.ddl_sql(sql)
            my.close()
    except Exception as err:
        print(err)
        return 0
    return 1

def set_timeout(timeout=7200):
    show_topic("设置超时变量", 2)
    res = set_server_nodes_timeout(timeout_time=timeout)
    t_res = 0
    if res == 0:
        t_res += 1
    res = set_storage_nodes_timeout(timeout_time=timeout)
    if res == 0:
        t_res += 1
    if t_res != 0:
        return 0
    return 1

def setting_variable(node_type, variable_name, value):
    # 用来设置变量的
    # node_type = ['computer']|['storage']
    # variable_name = 变量名
    # value = 变量值
    variable_list, nodes = [], []
    first_row = ''

    def print_log(txt):
        write_log.w2File().tolog(txt)
        print(txt)

    def get_res(node_info):
        # 获取变量结果
        res = ''
        if node_type == 'storage':
            connmy = connect.My(node_info[0], int(node_info[1]), node_info[2], node_info[3], 'mysql')
            sql = "show variables like '%s'" % variable_name
            res = connmy.sql_with_result(sql)[0]
        elif node_type == 'computer':
            connpg = connect.Pg(node_info[0], int(node_info[1]), node_info[2], node_info[3], 'postgres')
            sql = "show %s" % variable_name
            res = connpg.sql_with_result(sql)[0]
        return res

    def set_sql(node_info):
        # 设置变量值
        if node_type == 'storage':
            conn = connect.My(node_info[0], int(node_info[1]), node_info[2], node_info[3], 'mysql')
            if str(value).isdigit():
                sql = "SET PERSIST %s = %s" % (variable_name, value)
            else:
                sql = "SET PERSIST %s = '%s'" % (variable_name, value)
            conn.ddl_sql(sql)
            conn.close()
        elif node_type == 'computer':
            conn = connect.Pg(node_info[0], int(node_info[1]), node_info[2], node_info[3], 'postgres')
            if str(value).isdigit():
                sql = "ALTER SYSTEM SET %s = %s" % (variable_name, value)
            else:
                sql = "ALTER SYSTEM SET %s = '%s'" % (variable_name, value)
            print(sql)
            conn.ddl_sql(sql)
            conn.close()

    if node_type == "computer":
        nodes = info.node_info().show_all_running_computer()
        first_row = '| 计算节点 |'
    elif node_type == "storage":
        nodes = info.node_info().show_all_running_storage()
        first_row = '| 存储节点 |'

    len_v = len(variable_name)
    if len_v <= 8:
        size = (8 - len_v)
        if size % 2 == 0:
            left_size = int(size / 2)
            right_size = left_size
        else:
            left_size = int(size / 2)
            right_size = left_size + 1
        if node_type == "computer":
            first_row = '| 计算节点 |'
        elif node_type == "storage":
            first_row = '| 存储节点 |'
        second_row = '| %s%s%s |' % (' ' * left_size, variable_name, ' ' * right_size)
    else:
        size = (len_v - 8)
        if size % 2 == 0:
            left_size = int(size / 2)
            right_size = left_size
        else:
            left_size = int(size / 2)
            right_size = left_size + 1
        second_row = '| %s |' % variable_name
        if node_type == 'computer':
            first_row = '|  %s计算节点%s  |' % (' ' * left_size, ' ' * right_size)
        elif node_type == "storage":
            first_row = '| %s存储节点%s |' % (' ' * left_size, ' ' * right_size)

    for node in nodes:
        set_sql(node_info=node)
        if node_type == 'computer':
            tres = get_res(node_info=node)[0]
        elif node_type == 'storage':
            tres = get_res(node_info=node)[1]
        variable_list.append(tres)
        len_host = len(node[0])
        len_port = len(str(node[1]))
        len_res = len(tres)
        len_node = len_port + len_host + 1
        if len_node >= len_res:
            n_size = len_node - len_res
            first_row += ' %s:%s |' % (node[0], node[1])
            second_row += ' %s%s |' % (tres, ' ' * n_size)
        else:
            n_size = len_res - len_node
            first_row += ' %s:%s%s |' % (node[0], node[1], ' ' * n_size)
            second_row += ' %s |' % tres

    total_len = len(first_row)
    print_log('=' * total_len)
    print_log(first_row)
    print_log(second_row)
    print_log('=' * total_len)
    return setting_variable(node_type, variable_name, value)


def create_insert_table(pg_connect_info, db, table_name):
    create_sql = 'create table if not exists %s(id serial, b text);' % table_name
    drop_sql = 'drop table if exists %s' % table_name
    conn1 = connect.Pg(pg_connect_info[0], pg_connect_info[1], pg_connect_info[2], pg_connect_info[3], db)
    conn1.ddl_sql(drop_sql)
    conn1.ddl_sql(create_sql)
    random_times = random.randint(5, 25)
    for i in range(random_times):
        val = '{}_{}_{}'.format(db, table_name, i + 1)
        txt = "insert into %s(b) values('%s');" % (table_name, val)
        conn1.ddl_sql(txt)
    conn1.close()


def timer(func):
    pass


def show_topic(txt, level=1):
    write_log.w2File().tolog(txt)
    len_txt = len(str(txt).encode('GB2312'))
    if level == 1:
        split_str = '#'
    elif level == 2:
        split_str = '='
    elif level == 3:
        split_str = '-'
    len_split = len_txt + 4
    txt1 = split_str * len_split
    if level != 1:
        split_str = '|'
    txt2 = '%s %s %s' % (split_str, txt, split_str)
    txt = "%s\n%s\n%s" % (txt1, txt2, txt1)
    if level == 1:
        txt = '\n' + txt
    print(txt)


def pg_show_table(signal_server_list, table_name, schema='public', database='postgres'):
    sql = """select column_name, data_type, is_nullable, column_default from information_schema.columns where table_name
     = '%s' and table_schema = '%s';""" % (table_name, schema)
    server = signal_server_list
    pg = connect.Pg(host=server[0], port=server[1], user=server[2], pwd=server[3], db=database)
    try:
        res = pg.sql_with_result(sql)
        print('| column_name | data_type | is_nullable | column_default |')
        for i in res:
            i = str(i).replace('(', '| ').replace(')', ' |').replace(',', ' |')
            print(i)
    except Exception as err:
        print(err)
        return 0
    return res
