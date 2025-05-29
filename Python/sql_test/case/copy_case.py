import random
from case import load_data
from res import connection, read, other
import os


class Copy:
    def __init__(self):
        # 灌数据总是灌到运行中的第一个计算节点
        self.tmp_abspath = os.path.abspath('./tmp')
        self.conf = read.conf_info()
        columns_len = len(self.conf['table_column_type'].replace(' ', '').split(','))
        self.rand_column = 'c%s' % str(random.randint(1, columns_len) + 1)
        self.pg_node_info = connection.meta().all_comps()

    def diff_table(self, where_id=0, specify_columns=0):
        res = 1
        conf = self.conf
        pg_node_info = self.pg_node_info
        sql = 'select * from '
        if specify_columns != 0:
            sc = str(specify_columns).replace(')', '').replace('(', '')
            sql = 'select %s from ' % sc
        master_node, target_node = pg_node_info[0], pg_node_info[-1]
        master_tb, target_tb = conf['res_table_name'] , conf['dst_table_name']
        master_db, target_db = conf['res_database'], conf['dst_database']
        master_sql = sql + master_tb
        target_sql = sql + target_tb
        if where_id != 0:
            where_sql = ' %s' % where_id
            master_sql += where_sql
            target_sql += where_sql
        master_sql += ';'
        target_sql += ';'
        print('开始验证：master = %s -- target = %s' % (master_sql, target_sql))
        try:
            master_conn = connection.pgsql(node_info_list=master_node, db=master_db)
            master_res = master_conn.sql_with_res(master_sql)
            target_conn = connection.pgsql(node_info_list=target_node, db=target_db)
            target_res = target_conn.sql_with_res(target_sql)
            master_conn.close()
            target_conn.close()
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            if master_res == target_res:
                res = 1
            else:
                res = 0
        if res == 1:
            print('验证成功，源表与目标表数据一致\n')
        elif res == 0:
            print('验证失败，源表与目标表数据不一致\n')
        return res

    def run_case(self, opt='to', header=0, delimiter=',', encoding=0, quote=0, force_quote=0, where_id=0, specify_columns=0):
        # opt = [to]|[from], copy to, copy from
        res = 1
        conf = self.conf
        # 这里case就是后面汇总结果的输出
        case = ""
        file_name = conf['res_table_name']
        # 除id列之外的列的总数
        total_column_count = len(str(conf['table_column_type']).replace(' ','').split(','))
        # 开始判断并给出各个条件下对应的sql输出
        try:
            if opt == 'to':
                # 当为copy to的时候会先在源表里面创建表及灌数据，多进程个数及数据量等在配置文件里面改
                load_data.CreateTable().create_table(dst=0)
                load_data.load_worker()
                db, tb = conf['res_database'], conf['res_table_name']
                case += '|| %-4s ' % 'to'
            elif opt == 'from':
                # 当为copy from时只会在目标表里面创建表而已，并不会灌数据
                load_data.CreateTable().create_table(dst=1)
                db, tb = conf['dst_database'], conf['dst_table_name']
                case += '|| %-4s ' % 'from'
            # 这里delimiter是必须项，所以就没有去判断他存在不存在
            # 开始判断是否存在导入特定列的情况
            # if specify_columns == 1 and opt == 'from' and header == 1:
            if specify_columns != 0 and header == 1:
                rand_column = specify_columns
                sql = "\\copy %s %s %s '%s/%s.csv' with delimiter '%s' csv " % (tb, rand_column, opt, self.tmp_abspath, file_name, delimiter)
            else:
                sql = "\\copy %s %s '%s/%s.csv' with delimiter '%s' csv " % (tb, opt, self.tmp_abspath, file_name, delimiter)
                rand_column = 'NULL'
            case += '|| %-24s || %-9s ' % (rand_column, delimiter)
            # 后面的header/encoding/quote/force_quote/where都是非必须项
            # 故当为0时不会对其进行对应的操作
            if header == 1:
                sql += 'header '
                case += '|| %-6s ' % 'YES'
            else:
                case += '|| %-6s ' % 'NULL'
            if encoding != 0:
                sql += "encoding '%s' " % encoding
                case += '|| %-8s ' % encoding
            else:
                case += '|| %-8s ' % 'NULL'
            if quote != 0:
                sql += "quote '%s' " % quote
                case += "|| %-5s " % quote
            else:
                case += "|| %-5s " % 'NULL'
            if force_quote != 0 and opt == 'to':
                # force_quote只有在copy from时才能用
                rand_column = self.rand_column
                # 当指定列条件存在时，则在指定的几个列里面选择一个列来操作，不然会报错的
                if specify_columns != 0 and header == 1:
                    columns_list = str(specify_columns).replace('(','').replace(')', '').split(', ')
                    rand_column = random.choice(columns_list)
                sql += "force quote %s" % rand_column
                case += "|| %-11s " % rand_column
            else:
                case += "|| %-11s " % 'NULL'
            str_num = len(self.conf['data_size']) * 2 + 9
            if where_id != 0 and opt == 'from':
                # where条件只有在copy from时才可以使用
                opt_list = ['>', '<', '=', 'between']
                rand_opt = random.choice(opt_list)
                if rand_opt == '>' or '<':
                    # 当为大于或者小于时，要确认这个导出的数据量起码有50个, 从配置文件里面的data_size来确认其id值
                    rand_id = random.randint(50, int(self.conf['data_size']) - 50)
                    where_sql = ' where id %s %s' % (rand_opt, rand_id)
                elif rand_opt == '=':
                    # 从1到配置文件里面的数据量中随机选择一个id值
                    rand_id = random.randint(1, int(self.conf['data_size']))
                    where_sql = ' where id %s %s' % (rand_opt, rand_id)
                else:
                    # between 会选择两个id值，也是最少也要选择50行数据
                    start_id = random.randint(1, int(self.conf['data_size']) - 50)
                    end_id = random.randint(start_id, int(self.conf['data_size']))
                    where_sql = ' where id %s %s and %s' %(rand_opt, start_id, end_id)
                sql += where_sql
                case += f"|| %-{str_num}s ||" % where_sql
            else:
                where_sql = 0
                case += f"|| %-{str_num}s ||" % 'NULL'
            sql += ';'
            # 这里就直接用psql shell， psycopg2有自己的copy方法，所以直接copy语句会失败
            if opt == 'to':
                node = self.pg_node_info[0]
                comm = 'psql postgres://%s:%s@%s:%s/%s -c "%s"' % (node[3], node[2], node[0], node[1], db, sql)
            else:
                node = self.pg_node_info[-1]
                comm = 'psql postgres://%s:%s@%s:%s/%s -c "%s"' % (node[3], node[2], node[0], node[1], db, sql)
            res_str = other.run_shell(comm)
            for i in res_str:
                if 'ERROR' in i or 'error' in i:
                    res = 0
            if res == 1 and opt == 'from':
                # 只有前面都成功了这里都会开始验证，不然没意义
                res = self.diff_table(where_id=where_sql, specify_columns=specify_columns)
                if res == 1:
                    case += '  SUCC  ||'
                elif res == 0:
                    case += ' !FAIL! ||'
            else:
                # copy to 不用验证，因为还没有导入到目标表无法比较
                case += ' 未验证 ||'
        except Exception as err:
            print('测试失败，ERROR: %s' % err)
            res = 0
        return [case, res]
