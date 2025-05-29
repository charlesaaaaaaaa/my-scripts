import multiprocessing
from res import connection, read
import random
import string
import datetime


def get_column_info(node_info, db='postgres', table='test1'):
    # 获取列信息
    # postgres=# select column_name, is_nullable, data_type, column_default, numeric_precision, numeric_scale from
    # information_schema.columns where table_name = 'test1';
    #  column_name | is_nullable |       data_type        |           column_default            | numeric_precision | numeric_scale
    # -------------+-------------+------------------------+-------------------------------------+-------------------+---------------
    #  id          | NO          | bigint                 | "nextval"('test1_id_seq'::regclass) |                64 |             0
    #  c2          | YES         | bigint                 |                                     |                64 |             0
    #  c3          | NO          | bigint                 | "nextval"('test1_c3_seq'::regclass) |                64 |             0
    #  c4          | YES         | boolean                |                                     |                   |
    #  c5          | YES         | text                   |                                     |                   |
    #  c6          | YES         | time without time zone |                                     |                   |
    #  c7          | YES         | date                   |                                     |                   |
    # (7 rows)
    sql = "select column_name, is_nullable, data_type, column_default, " \
          "numeric_precision, numeric_scale from information_schema.columns " \
          "where table_name = '%s' order by ordinal_position;" % table
    conn = connection.pgsql(node_info_list=node_info, db=db)
    res = conn.sql_with_res(sql)
    return res


def gen_type_data(data_type, id, numeric_precision=None, numeric_scale=None):
    """
    产生指定的数据类型的数据
    id 就是第几行的数据，根据id产生数据
    numeric_precision和numeric_scale
      如 numeric(10, 2) == datatype='numeric', numeric_precision=10, numeric_scale=2
    像一些只有总位数的就可以如： integer（32）== datatype='interger', numeric_precision=32
     bigint, boolean, bytea, character, character varying, date, double precision,
     integer, numeric, smallint, text, time without time zone
    """
    # 当numeric_percision和numeric_scale为空时
    if not numeric_precision and not numeric_scale:
        if 'int' in data_type or 'numeric' in data_type or 'double' in data_type:
            res = id
        elif data_type == 'boolean':
            res = random.choice(['TRUE', 'FALSE'])
        elif data_type == 'bytea':
            res = random.choices(['0', '1'], k=50)
            res = ''.join(res)
            res = "'%s'" % res
        elif data_type == 'text':
            res = random.choices(string.digits + string.ascii_letters, k=200)
            res = ''.join(res)
            res = "'%s'" % res
        elif 'char' in data_type:
            res = random.choices(string.digits + string.ascii_letters, k=10)
            res = ''.join(res)
            res = "'%s'" % res
        elif data_type == 'date':
            res = datetime.date.today()
            res = res + datetime.timedelta(days=id)
            res = "'%s'" % res
        elif data_type == 'time without time zone' or data_type == 'time with time zone':
            res1 = str(datetime.datetime.now())
            res = str(res1).split(' ')[1]
            res = "'%s'" % res
    # 当numeric_percision和numeric_scale不为空时
    else:
        if 'int' in data_type:
            res = random.randint(-2 ** (numeric_precision - 1), 2 ** (numeric_precision - 1) - 1)
            # print('random=%s type=%s' % (res, data_type))
        elif 'char' in data_type:
            res = random.choices(string.digits + string.ascii_letters, k=numeric_precision)
            res = ''.join(res)
            res = "'%s'" % res
        elif 'double precision' in data_type:
            res = round(random.uniform(-2 ** (numeric_precision - 1), 2 ** (numeric_precision - 1) - 1), 2)
        elif 'real' in data_type:
            res = round(random.uniform(-2 ** (numeric_precision - 1), 2 ** (numeric_precision - 1) - 1), 2)
        elif 'numeric' in data_type:
            res = round(random.uniform(-2 ** (numeric_precision - 1), 2 ** (numeric_precision - 1) - 1), numeric_scale)
    return res

class CreateTable:
    def __init__(self):
        self.conf = read.conf_info()
        self.id_column_type = self.conf['id_column_type']
        self.data_type_list = self.conf['table_column_type'].split(',')

    def create_partition_table(self, node_info, partition_table_num=2, table_name='test_pt', database='postgres'):
        # partition_table_num 子分区表数量，默认为2
        conf = self.conf
        id_column_type = self.id_column_type
        data_type_list = self.data_type_list

        pg_conn = connection.pgsql(node_info_list=node_info, db=database)
        drop_sql = 'drop table if exists %s;' % table_name
        create_sql = 'create table if not exists %s(id %s primary key' % (table_name, id_column_type)
        column_num = 1
        for i in data_type_list:
            column_num += 1
            column_name = 'c%s' % column_num
            tmp_sql = ', %s %s' % (column_name, i)
            create_sql += tmp_sql
        create_sql += ') partition by hash(id) partitions %s;' % partition_table_num
        print(drop_sql)
        pg_conn.sql(drop_sql)
        print('运行的计算节点：%s, sql:%s' % (str(node_info), create_sql))
        pg_conn.sql(create_sql)
        pg_conn.close()
        return 1


    def create_table(self, parquet=0, dst=0, db=0, table=0, node_info=0):
        # 创建表失败了就直接退出了，没有什么try不try的
        conf = self.conf
        id_column_type = self.id_column_type
        data_type_list = self.data_type_list
        node_info_list = connection.meta().all_comps()
        # 根据配置文件中的这个列数据类型生成对应的创建表sql, 如
        # table_column_type = bigint, bigserial, boolean, text, time, date
        # create_sql: create table if not exists test1(id bigserial primary key, c2 bigint, c3 bigserial, c4 boolean, c5 text, c6 time, c7 date);


        if dst == 1:
            database = conf['dst_database']
            # 当为目标时，计算节点为正在运行中的最后一个
            table_name = conf['dst_table_name']
            node_info_list = node_info_list[-1]
        elif dst == 0:
            database = conf['res_database']
            table_name = conf['res_table_name']
            # 当为目标时，计算节点为正在运行中的第一个
            node_info_list = node_info_list[0]
        if table != 0:
            table_name = table
        if db != 0:
            database = db
        if node_info != 0:
            node_info_list = node_info
        table_path = conf['parquet_table_path']
        for i in range(len(data_type_list)):
            if data_type_list[i][0] == ' ':
                data_type_list[i].replace(' ', '', 1)
        drop_sql = 'drop table if exists %s;' % table_name
        create_sql = 'create table if not exists %s(id %s' % (table_name, id_column_type)
        if parquet == 0:
            create_sql += ' primary key'
        row_num = 1
        for data_type in data_type_list:
            row_num += 1
            tmp = ', c%s %s' % (row_num, data_type)
            create_sql += tmp
        if parquet == 0:
            create_sql += ');'
        else:
            cluster_id = connection.meta().all_cluster_id()[-1][0]
            shard_id = connection.meta().shard_id(cluster_id=cluster_id)
            create_sql += ") with (engine=parquet, table_path='%s/test.parquet', shard=%s);" % (table_path, shard_id)
        pg_conn = connection.pgsql(node_info_list=node_info_list, db=database)
        print(drop_sql)
        pg_conn.sql(drop_sql)
        print('运行的计算节点：%s, sql:%s' % (str(node_info_list), create_sql))
        pg_conn.sql(create_sql)
        pg_conn.close()
        return 1


def load_worker(db=0, table=0, tb_size=0, not_echo_err=1):
    conf = read.conf_info()
    pg_node_info = connection.meta().all_comps()
    process_num = conf['processes']
    database = conf['res_database']
    table_name = conf['res_table_name']
    table_size = int(conf['data_size'])
    if db != 0:
        database = db
    if table != 0:
        table_name = table
    if tb_size != 0:
        table_size = int(tb_size)
    # 装源表里面非自增列的列表
    column_name_list = []
    # 源表非自增列里面一些用得上的列信息
    column_info_list = []
    # 装源表的列信息
    print('对计算节点 %s db = %s  table = %s 灌 [%s] 行数据' % (pg_node_info[0], database, table_name, table_size))
    table_column_info_list = get_column_info(node_info=pg_node_info[0], db=database, table=table_name)
    for column_info in table_column_info_list:
        # 只处理非自增列, 然后把列名给到column_list变量方便后续多进程使用
        if not column_info[3] or 'nextval' not in column_info[3]:
            column_name_list.append(column_info[0])
    # 以column_info这个装非自增列名的列表为准，把用得上的列信息给到column_info_list
    for column_name in column_name_list:
        for i in table_column_info_list:
            if i[0] == column_name:
                # 0为列名column_name， 2为数据类型data_type
                # 4为类型的总位数numeric_precision， 5为类型的小数位数numeric_scale
                # 以这几个列的信息为准产生对应的数据
                tmp_list = [i[0], i[2], i[4], i[5]]
                column_info_list.append(tmp_list)
    column_name = ', '.join(column_name_list)
    insert_sql = 'insert into %s(%s) values ' % (table_name, column_name)

    # 创建一个共享列表，方便所有的子进程都能访问的列表
    # 主要是用来监控灌数据进度的
    # [[1, 101], [101, 201], [201, 301], [301, 401], [401, 501], [501, 601], ...]
    id_list = []
    for i in range(0, table_size, 100):
        start_num = i + 1
        end_num = i + 100 + 1
        tmp_list = [start_num, end_num]
        id_list.append(tmp_list)
    if id_list[-1][1] != table_size:
        id_list[-1][1] = table_size + 1
    share_list = multiprocessing.Manager().list()
    share_list.extend(id_list)

    # 每个worker进程要做的事
    def signal_worker(share_list, num):
        err_info = ''
        print('loadworker_%s loading ...' % num)
        # 创建一个源表的连接
        pg_conn = connection.pgsql(node_info_list=pg_node_info[0], db=database)
        # 生成 100行数据
        while share_list:
            sql = insert_sql
            tmp_str = ''
            # print('11111 %s' % tmp_str)
            # 获取共享列表的第1个元素，然后在共享列表里面删掉他
            # 如果此次insert数据失败则把这个元素重新加到共享列表里面去
            cur_id_list = share_list[0]
            del share_list[0]
            for i in range(cur_id_list[0], cur_id_list[1]):
                tmp_data = ''
                for column in column_info_list:
                    # 每个列生成一个数据，然后给到tmp_data
                    tmp = gen_type_data(data_type=column[1], id=i, numeric_precision=column[2], numeric_scale=column[3])
                    if tmp_data:
                        tmp_data += ', %s' % str(tmp)
                    else:
                        tmp_data += str(tmp)
                tmp_data = '(%s)' % tmp_data
                if tmp_str:
                    tmp_str += ', %s' % tmp_data
                else:
                    tmp_str += tmp_data
            # 数据和前面的insert部分拼接在起
            sql += tmp_str + ';'
            try:
                pg_conn.sql(sql)
            except Exception as err:
                if not_echo_err == 0:
                    print(str(err))
                share_list.append(cur_id_list)
        pg_conn.close()
        print('loadworker_%s done' % num)

    # 开启多进程
    pl = []
    num = 0
    for i in range(int(process_num)):
        p = multiprocessing.Process(target=signal_worker, args=(share_list, num))
        pl.append(p)
        p.start()
        num += 1
    for i in pl:
        i.join()
