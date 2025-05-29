import random

from res import connection, other
import os


class TestCase:
    def __init__(self):
        self.meta = connection.meta()
        comps_info_list = self.meta.all_comps()
        self.comp_info = comps_info_list[0]

    def create_table(self):
        res = 1
        comp_info = self.comp_info
        create_sqlfile = os.path.abspath('./case/sql/transfer_create.sql')
        sql_shell = 'psql postgres://%s:%s@%s:%s/postgres -f %s' % (comp_info[2], comp_info[3], comp_info[0], str(comp_info[1]), create_sqlfile)
        res = other.run_shell(sql_shell)
        if 'error' in res or 'ERROR' in res:
            res = 0
        return res

    def trigger_test(self):
        res = 1
        comp_info = self.comp_info
        case = '触发器'
        create_sqlfile = os.path.abspath('./case/sql/transfer_trigger.sql')
        sql_shell = 'psql postgres://%s:%s@%s:%s/postgres -f %s' % (comp_info[2], comp_info[3], comp_info[0], str(comp_info[1]), create_sqlfile)
        result = other.run_shell(sql_shell)
        for i in result:
            if 'error' in result or 'ERROR' in result:
                print(result)
                res = 0
        sql = "insert into test_user(name, password, status, update_times) value('test2', 'test2', 'using', 0);"
        select_sql = 'select u_amount from amount where u_id = 2;'
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        pg_conn.sql(sql, commit=0)
        result = int(pg_conn.sql_with_res(select_sql, commit=0)[0][0])
        print(result == 100000)
        if result != 100000:
            res = 0
        pg_conn.close(commit=1)
        return [case, res]

    def function_test(self):
        res = 1
        comp_info = self.comp_info
        case = '函数使用'
        create_sqlfile = os.path.abspath('./case/sql/transfer_function.sql')
        sql_shell = 'psql postgres://%s:%s@%s:%s/postgres -f %s' % (comp_info[2], comp_info[3], comp_info[0], str(comp_info[1]), create_sqlfile)
        result = other.run_shell(sql_shell)
        if 'error' in result or 'ERROR' in result:
            print(result)
            res = 0
        print('使用对应函数创建到100个用户')
        id = 3
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        for i in range(id, 101):
            sql = "select change_user_status(%s, 'using')" % i
            pg_conn.sql(sql, commit=0)
        pg_conn.close(commit=1)
        return [case, res]

    def stored_procedure(self):
        res = 1
        comp_info = self.comp_info
        case = '存储过程'
        create_sqlfile = os.path.abspath('./case/sql/transfer_stored_procedure.sql')
        sql_shell = 'psql postgres://%s:%s@%s:%s/postgres -f %s' % (comp_info[2], comp_info[3], comp_info[0], str(comp_info[1]), create_sqlfile)
        result = other.run_shell(sql_shell)
        if 'error' in result or 'ERROR' in result:
            print(result)
            res = 0
        print('执行20次转账的存储过程')
        # 创建一个1到100的列表
        number_list = []
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        for i in range(1, 101):
            number_list.append(i)
        for i in range(20):
            p1 = random.randint(2, 100)
            p2 = random.randint(2, 100)
            while p2 == p1:
                p2 = random.randint(1, 100)
            amount = random.randint(100, 10000)
            sql = 'CALL transfer_case(%d, %d, %d)' % (p1, amount, p2)
            pg_conn.sql(sql, commit=0)
        pg_conn.close(commit=1)
        return [case, res]

    def drop_all_func(self):
        # 删除掉所有的函数 触发器 存储过程
        res = 1
        comp_info = self.comp_info
        case = '删除函数/触发器/存储过程'
        print('开始 %s' % case)
        func_list = ['get_user_status', 'get_user_amount', 'change_user_status', 'add_amount']
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
        for func in func_list:
            sql = 'drop function if exists %s CASCADE;' % func
            print(sql)
            pg_conn.sql(sql, commit=0)
        sql = 'drop trigger if exists trigger_add_amount on test_user;'
        print(sql)
        pg_conn.sql(sql, commit=0)
        sql = 'drop PROCEDURE if exists transfer_case CASCADE;'
        print(sql)
        pg_conn.sql(sql, commit=0)
        return [case, res]