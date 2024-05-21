import os
import subprocess
from base.other import info
import threading
import random
from base.other import connect
from base.other import write_log

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
        txt = 'insert into %s(txt) values(%s)' % (table_name, val)
        conn1.ddl_sql(txt)
    conn1.close()

def timer(func):
    pass

