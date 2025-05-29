import multiprocessing
import os

import pandas
from res import connection, read_conf
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
            print('id=%s type=%s' % (res, data_type))
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


def change_parquet_type(parquet_type, source_type):
    res = ''
    parquet_type = str(parquet_type)
    # 这个就是不用去改变的一些类型，
    source_typelist = ['boolean', 'date']
    # parquet和postgres类型是一一对应的，
    parquet_typelist = ['int8', 'int16', 'int32', 'int64', 'object', 'varchar', 'datetime64[ns]']
    postgre_typelist = ['boolean', 'smallint', 'int', 'bigint', 'varchar(100)', 'varchar(100)', 'time']
    num = 0
    if source_type in source_typelist:
        res = source_type
    else:
        for i in parquet_typelist:
            if parquet_type in i:
                res = postgre_typelist[num]
            num += 1
    return res


def create_table(parquet=0):
    # 创建表失败了就直接退出了，没有什么try不try的
    conf = read_conf.conf_info()
    node_info_list = connection.meta().all_comps()
    id_column_type = conf['id_column_type']
    # 根据配置文件中的这个列数据类型生成对应的创建表sql, 如
    # table_column_type = bigint, bigserial, boolean, text, time, date
    # create_sql: create table if not exists test1(id bigserial primary key, c2 bigint, c3 bigserial, c4 boolean, c5 text, c6 time, c7 date);
    #  bigint, bit, boolean, bytea
    #  character, character varying, cidr, date, double precision, inet, integer, macaddr, macaddr8, money, numeric, real
    #  smallint, text, timestamp without time zone, timestamp with time zone, time without time zone, time with time zone
    if parquet == 0:
        database = conf['res_database']
        table_name = conf['res_table_name']
        node_info_list = node_info_list[0]
    else:
        database = conf['dst_database']
        table_name = conf['dst_table_name']
        node_info_list = node_info_list[1]
    table_path = conf['parquet_table_path']
    data_type_list = conf['table_column_type'].split(',')
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


def create_parquet_table():
    node_info_list = connection.meta().all_comps()
    conf = read_conf.conf_info()
    comp_node = node_info_list[-1]
    # id列的数据类型
    id_column_type = conf['id_column_type']
    # 其它列的数据类型
    data_type_list = conf['table_column_type'].split(',')
    num = 0
    for i in range(len(data_type_list)):
        data_type_list[i] = data_type_list[i].replace(' ', '', 1)
        num += 1
    cluster_id = connection.meta().all_cluster_id()[-1][0]
    shard_id = connection.meta().shard_id(cluster_id=cluster_id)
    table_name = conf['dst_table_name']
    table_path = os.path.abspath(conf['parquet_table_path'])
    parquet_data = pandas.read_parquet(table_path)
    parquet_dtypes = parquet_data.dtypes
    print(parquet_dtypes)
    # parquet里面的cloumn数据类型
    parquet_type = parquet_dtypes.values
    # parquet里面的column名
    paruqet_column_name = parquet_dtypes.keys()
    drop_sql = 'drop table if exists %s;' % table_name
    sql = 'create table if not exists %s(' % table_name
    # index 就是parquet列名列表的index， data_index 就是源表的列名列表的index
    index = 0
    data_index = 0
    # 遍历parquet数据类型里面元素
    for tmp_type in parquet_type:
        # 当parquet的列名为id的时候其源表的这个列的类型就是id列数据类型
        if paruqet_column_name[index] == 'id':
            source_type = id_column_type
            # 因为源表id列不在那源表数据类型列表里面，所以这里在遇到id列的时候dataindex要
            data_index -= 1
        else:
            # if 'id' == paruqet_column_name[0]:
            #     source_type = data_type_list[index + 1]
            # else:
            source_type = data_type_list[data_index]
        pg_type = change_parquet_type(tmp_type, source_type)
        if index == 0:
            sql += '%s %s' % (paruqet_column_name[index], pg_type)
        else:
            sql += ', %s %s' % (paruqet_column_name[index], pg_type)
        index += 1
        data_index += 1
    sql += ") with (engine=parquet, table_path='%s/test.parquet', shard=%s);" % (table_path, shard_id)
    pg_conn = connection.pgsql(node_info_list=comp_node, db='postgres')
    print(drop_sql)
    pg_conn.sql(drop_sql)
    print('运行的计算节点：%s, sql:%s' % (str(comp_node), sql))
    pg_conn.sql(sql)
    pg_conn.close()


def load_worker():
    conf = read_conf.conf_info()
    pg_node_info = connection.meta().all_comps()
    process_num = conf['processes']
    database = conf['res_database']
    table_name = conf['res_table_name']
    table_size = int(conf['data_size'])
    # 装源表里面非自增列的列表
    column_name_list = []
    # 源表非自增列里面一些用得上的列信息
    column_info_list = []
    # 装源表的列信息
    table_column_info_list = get_column_info(node_info=pg_node_info[0], db=database, table=table_name)
    print(table_column_info_list)
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
