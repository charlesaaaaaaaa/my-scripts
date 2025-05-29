import random
from res import connection, read_conf
from case import load_data

class Select:
    def __init__(self):
        self.conf = read_conf.conf_info()
        max_id_sql = 'select max(id) from %s' % self.conf['dst_table_name']
        self.pg_node_info = connection.meta().all_comps()
        pgconn = connection.pgsql(node_info_list=self.pg_node_info[-1], db=self.conf['dst_database'])
        self.max_id = pgconn.sql_with_res(max_id_sql)[0][0]
        self.column_info_list = load_data.get_column_info(node_info=self.pg_node_info[-1], db=self.conf['dst_database'], table=self.conf['dst_table_name'])
        # 这里是获取所有列名
        column_name_list, int_name_list = [], []
        for i in self.column_info_list:
            column_name_list.append(i[0])
            if 'int' in i[2] or 'double' in i[2] or 'real' in i[2]:
                int_name_list.append(i[0])
        self.column_name_list = column_name_list
        self.int_name_list = int_name_list


    def use_function(self, column_info_list):
        func_list = ['max', 'min', 'sum', 'avg', 'distinct']
        # # print(len(column_info_list), column_info_list)
        # if len(column_info_list) == 1:
        #     rand_k = 1
        # else:
        #     rand_k = random.randint(1, len(column_info_list))
        # 这里随机选择列名列表里3个及以下的列
        column_list = column_info_list
        tmp_func_list, tmp_column_list = [], []
        res = ''
        #for i in column_list:
        # 随机选择不重复的方法
        rand_func = random.choice(func_list)
        while rand_func in tmp_func_list:
            rand_func = random.choice(func_list)
        tmp_func_list.append(rand_func)
        tmp_res = '%s(%s)' % (rand_func, column_list)
        if not res:
            res = tmp_res
        else:
            res += ', %s' % tmp_res
        del func_list[-1]
        # # 检查是否有未被加上方法的列，有的话这里再加上去，不过是不带方法的
        # if len(column_info_list) != len(column_list):
        #     for i in column_info_list:
        #         if i not in column_list:
        #             res += ', %s' % i
        return res

    def where_case(self, func_opt):
        # 目前where主要是id列，其它的列不好指定
        max_id = self.max_id
        rand_num = random.randint(0, 4)
        while func_opt == 1 and rand_num == 2:
            rand_num = random.randint(0, 4)
        sql = ' where id'
        # 大于和小于的sql后面要加上limit，limit 50个以内结果。
        if rand_num == 0:
            # 当为大于时，最少要确保有5个结果被选中
            rand_id = random.randint(1, max_id - 5)
            sql += ' > %s' % rand_id
        elif rand_num == 1:
            # 当为小于时，最少要确保有5个结果被选中
            rand_id = random.randint(5, max_id)
            sql += ' < %s' % rand_id
        elif rand_num == 2:
            rand_id = random.randint(1, max_id)
            sql += ' = %s' % rand_id
        else:
            # 这里因为不等于的话会选择除指定id之外的所有值，故加个between避免这种情况
            rand_id = random.randint(50, max_id - 50)
            start_id = random.randint(rand_id - 50, rand_id)
            end_id = random.randint(rand_id, rand_id + 50)
            if rand_num == 3:
                sql += ' != %s' % rand_id
            sql += ' between %s and %s' % (start_id, end_id)
        return sql

    def order_by(self, column_name):
        order_list = [' asc', ' desc', ' ']
        order_opt = random.choice(order_list)
        res = ' order by %s%s' % (column_name, order_opt)
        return res

    def group_by(self, column_name):
        res = ' group by %s' % column_name
        return res

    def gen_select(self):
        conf = self.conf
        sql = ''
        max_id = self.max_id
        res_tb, dst_tb = conf['res_table_name'], conf['dst_table_name']
        column_name_list = self.column_name_list
        int_name_list = self.int_name_list
        if len(column_name_list) <= 3:
            column_num = 2
        else:
            column_num = random.randint(1, 3)
        select_column = random.choices(column_name_list, k=column_num)
        select_int_column = random.choices(int_name_list)[0]
        rand_func = random.randint(0, 2)
        rand_group = 0
        sql1, sql2 = '', ''
        # 当用随机使用的函数次数为0及1-3次的情况
        # print('  rand_func: %s' % rand_func)
        if rand_func == 0:
            # 为0的时候就是不调用方法, 这个时候又有两种情况
            # 一个是直接select *， 另一个是select 多个表名
            tmp_rand = random.randint(0, 1)
            if tmp_rand != 0:
                sql1 += 'select * from %s' % res_tb
                sql2 += 'select * from %s' % dst_tb
            else:
                rand_column_str = ', '.join(select_column)
                sql1 += 'select %s from %s' % (rand_column_str, res_tb)
                sql2 += 'select %s from %s' % (rand_column_str, dst_tb)
        else:
            # 当不为的时候，就直接调用那个use_function来生成列
            # 这个会再一次选择用哪几个列来加上pg的
            tmp_sql = self.use_function(select_int_column)
            sql1 += 'select %s from %s' % (tmp_sql, res_tb)
            sql2 += 'select %s from %s' % (tmp_sql, dst_tb)
        # where的情况
        rand_where = random.randint(0, 1)
        where_equal = ''
        if rand_where == 1:
            where_sql = self.where_case(func_opt=rand_func)
            sql += where_sql
            if '=' in sql:
                where_equal = 1
        # 当不只选择一行时，再继续 order by和group by的情况
        if not where_equal:
            rand_order = random.randint(0, 1)
            rand_group = random.randint(0, 3)
            if rand_group == 1:
                # 当group by时，sql要重新生成，前面生成的用不了了
                func_list = ['max', 'min', 'sum', 'avg']
                tmp_rand_func = random.choice(func_list)
                # rand_int_column = random.choice(select_int_column)
                rand_int_column = select_int_column
                rand_column = random.choice(select_column)
                res_sql = 'select %s, %s(%s) from %s group by %s' % (rand_column, tmp_rand_func, rand_int_column, res_tb, rand_column)
                dst_sql = 'select %s, %s(%s) from %s group by %s' % (rand_column, tmp_rand_func, rand_int_column, dst_tb, rand_column)
                if rand_order == 0:
                    res_sql += ';'
                    dst_sql += ';'
            if rand_order == 1:
                if rand_func == 0:
                    if rand_group != 1:
                        rand_column = random.choice(select_column)
                        sql += self.order_by(rand_column)
                    else:
                        sql = self.order_by(rand_column)
                        res_sql += sql + ';'
                        dst_sql += sql + ';'
        sql += ';'
        # 除了group by之外的sql要进行拼接
        if rand_group != 1:
            res_sql = sql1 + sql
            dst_sql = sql2 + sql
        return res_sql, dst_sql

    def compare(self):
        # 调用上面的gen_select生产的sql去源及parquet表里面跑
        conf = self.conf
        node_info = self.pg_node_info
        select_times = int(conf['select_times'])
        print('开始随机抽查[%s]次select语句' % select_times)
        res_db, dst_db = conf['res_database'], conf['dst_database']
        res_node, dst_node = node_info[0], node_info[-1]
        fail_times = 0
        for i in range(1, select_times + 1):
            res_sql, dst_sql = self.gen_select()

            res_pg_conn = connection.pgsql(node_info_list=res_node, db=res_db)
            dst_pg_conn = connection.pgsql(node_info_list=dst_node, db=dst_db)
            res_res, dst_res = 0, 0
            print('第[%s]次检查：res_sql: %s | dst_sql: %s' % (i, res_sql, dst_sql))
            try:
                dst_res = dst_pg_conn.sql_with_res(sql=dst_sql)
            except Exception as err:
                print('dst err: %s' % err)
            finally:
                dst_pg_conn.close()
            try:
                res_res = res_pg_conn.sql_with_res(sql=res_sql)
            except Exception as err:
                print('res err: %s' % err)
            finally:
                res_pg_conn.close()
            if dst_res == res_res:
                print(' 结果一致')
            else:
                fail_times += 1
                print(' 结果不一致')
        if fail_times == 0:
            print('本次检查成功')
            res = 1
        else:
            print('本次检查失败')
            res = 0
        return res

    def compare_table(self):
        conf = self.conf
        node_info = self.pg_node_info
        # select_times = int(conf['select_times'])
        # print('开始随机抽查[%s]次select语句' % select_times)
        res_db, dst_db = conf['res_database'], conf['dst_database']
        res_tb, dst_tb = conf['res_table_name'], conf['dst_table_name']
        res_node, dst_node = node_info[0], node_info[-1]
        res_pg_conn = connection.pgsql(node_info_list=res_node, db=res_db)
        dst_pg_conn = connection.pgsql(node_info_list=dst_node, db=dst_db)
        res_sql = 'select * from %s;' % res_tb
        dst_sql = 'select * from %s;' % dst_tb
        print(res_sql)
        res_res = res_pg_conn.sql_with_res(res_sql)
        print(dst_sql)
        dst_res = dst_pg_conn.sql_with_res(dst_sql)
        res_pg_conn.close()
        dst_pg_conn.close()
        if res_res == dst_res:
            print('源表与目标表数据相同')
            res = 1
        else:
            print('!源表与目标表数据不相同!')
            res = 1
        return res
