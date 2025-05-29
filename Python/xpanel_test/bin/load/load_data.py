import multiprocessing
from bin import connection
from bin.other_opt import getconf as read
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


def create_table(db='postgres', table='test1', node_info=0):
    # 创建表失败了就直接退出了，没有什么try不try的
    conf = read().getXpanelInfo()
    node_info_list = connection.meta().all_comps()
    id_column_type = conf['id_column_type']
    # 根据配置文件中的这个列数据类型生成对应的创建表sql, 如
    # table_column_type = bigint, bigserial, boolean, text, time, date
    # create_sql: create table if not exists test1(id bigserial primary key, c2 bigint, c3 bigserial, c4 boolean, c5 text, c6 time, c7 date);

    table_name = table
    database = db
    node_info_list = node_info
    data_type_list = conf['table_column_type'].split(',')
    for i in range(len(data_type_list)):
        if data_type_list[i][0] == ' ':
            data_type_list[i].replace(' ', '', 1)
    drop_sql = 'drop table if exists %s;' % table_name
    create_sql = 'create table if not exists %s(id %s' % (table_name, id_column_type)
    row_num = 1
    for data_type in data_type_list:
        row_num += 1
        tmp = ', c%s %s' % (row_num, data_type)
        create_sql += tmp
    create_sql += ');'
    pg_conn = connection.pgsql(node_info_list=node_info_list, db=database)
    print(drop_sql)
    pg_conn.sql(drop_sql)
    print('运行的计算节点：%s, sql:%s' % (str(node_info_list), create_sql))
    pg_conn.sql(create_sql)
    pg_conn.close()
    return 1


def load_worker(node_info, db='postgres', table='test1', tb_size=0):
    conf = read().getXpanelInfo()
    pg_node_info = node_info
    process_num = conf['processes']
    database = db
    table_name = table
    table_size = int(conf['data_size'])
    if tb_size != 0:
        table_size = int(tb_size)
    # 装源表里面非自增列的列表
    column_name_list = []
    # 源表非自增列里面一些用得上的列信息
    column_info_list = []
    # 装源表的列信息
    print('对计算节点 %s db = %s  table = %s 灌 [%s] 行数据' % (pg_node_info, database, table_name, table_size))
    table_column_info_list = get_column_info(node_info=pg_node_info, db=database, table=table_name)
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
        pg_conn = connection.pgsql(node_info_list=pg_node_info, db=database)
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


def diff_tabls(source_node_info, target_node_info, source_db='postgres', source_table='test1', target_db='postgres', target_table='test1'):
    print('开始对比表是否相同')
    pg_source_conn = connection.pgsql(node_info_list=source_node_info, db=source_db)
    pg_target_conn = connection.pgsql(node_info_list=target_node_info, db=target_db)
    source_sql = 'select * from %s' % source_table
    target_sql = 'select * from %s' % target_table
    source_res = pg_source_conn.sql_with_res(source_sql)
    target_res = pg_target_conn.sql_with_res(target_sql)
    if source_res == target_res:
        res = 1
        print('相同，对比成功')
    else:
        res = 0
        print('不同，对比失败')
    return res
