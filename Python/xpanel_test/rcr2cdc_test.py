import argparse
import bin.load.mongo
import bin.load.es
from bin.other_opt import *
from xpanel_case.alarm_server import *
from xpanel_case.rcr2cdc import multi_source


def get_db_tb_name(db, engine='InnoDB', partition=0):
    db_tb = {
        "mysql": ['public', 'test1'],
        "mariadb": ['public', 'test1'],
        "tdengine": ["device_shenzhen", "meter_tj"],
        "mongodb": ['testdb', 'testtb'],
        "es": ['test_index', 'test_index']
        # 源为es时kl同步表要求库名和表名是一样的，es这边我用的test_index为索引名，所以这里是test_index.test_index
    }
    db_name, tb = db_tb[db][0], db_tb[db][1]
    if db != 'tdengine':
        if engine == 'InnoDB':
            engine = 'innodb'
        tb += '_%s' % engine
        if db == 'es':
            db_name += '_%s' % engine
        if db != 'tdengine':
            if partition == 1:
                tb += '_partition'
                if db == 'es':
                    db_name += '_partition'
    return db_name, tb

@timer
def rcr_cdc(db, engine='InnoDB', partition=0, times=1):
    # partition=1时，会先创建一个单表的双活，然后再创建一个分区瑶双活
    # times=1时，会在添加第三方元数据和添加cdc节点之前删除掉可能存在的条目
    # ## 默认是1，这个机制只有在同时跑多个第三方双活时用得上
    # 先把所有的元数据节点信息放到一个配置文件里面去
    init_config()
    loading().load_and_change_pwd()
    try:
        print('\n=================\n开始测试多源 -- %s\n=================\n' % db)
        # 每个第三方源的双活同步表的库表名都不一样，要指定
        db_name, tb = get_db_tb_name(db=db, engine=engine, partition=partition)
        # db_tb = {
        #     "mysql": ['public', 'test1'],
        #     "mariadb": ['public', 'test1'],
        #     "tdengine": ["device_shenzhen", "meter_tj"],
        #     "mongodb": ['testdb', 'testtb'],
        #     "es": ['test_index', 'test_index']
        #     # 源为es时kl同步表要求库名和表名是一样的，es这边我用的test_index为索引名，所以这里是test_index.test_index
        # }
        # db_name, tb = db_tb[db][0], db_tb[db][1]
        # if partition == 1 and db != 'tdengine':
        #     tb += '_partition'
        #     if db == 'es':
        #         db += '_partition'
        # 创建同步表，prepare方法就是如果rcr要创建同步表的就会在这个方法里面创建好
        if db != "mysql" or db != "mariadb":
            res = multi_source.TestCase().prepare(thirdparty_db=db, table_engine=engine, partition=partition, tb_name=tb, db_name=db_name)
            assert res != 0
            # 创建状态表，和klustron的同级数据库下创建，这样就不用在api里面指定状态表位置了
            multi_source.TestCase().create_status_table(db=db_name)
            # sleep(50)

        # 准备表数据
        if db == 'mysql' or db == 'mariadb':
            res = multi_source.TestCase().gen_data(thirdparty_db=db)
            assert res != 0
        elif db == 'mongodb':
            # mongo的这个load方法包含有创建库表的操作
            # 因为mongo如果在指定db时如果db不存在就会创建对应的db，故这个方法不用创建db，直接创建集合就行
            res = bin.load.mongo.LoadMg().multi_load(thread=10, each_thread_size=10000, tb=tb)
            assert res != 0
        elif db == "es":
            # es没有库的概念，只有一个和表概念差不多的index索引
            # 指定process则以多进程的方式灌数据，反之以多线程方式
            # 指定threads也是多线程方式，但同时指定则以多进程的方式灌
            # 先去备es上创建一样的index
            bin.load.es.LoadEs().delete_create_index(host_num=1, index_name=tb)
            # 进程数10个，每个各灌1000000，为什么是thread_size, 因为我懒得改参数名了
            bin.load.es.LoadEs().mutil_load(drop=1, each_thread_size=10000, threads=10, index_name=tb)

        # 添加元数据节点
        res = multi_source.TestCase().add_metadata_node(thirdparty_db=db, index=tb, delete=times)
        assert res != 0

        # 创建rcr服务
        no_rcr_list = ['mongodb', 'es']
        if db not in no_rcr_list:
            res = multi_source.TestCase().create_rcr(thirdparty_db=db)
            assert res != 0

        # 添加 cdc 服务
        if times == 1:
            res = multi_source.TestCase().create_cdc_server(thirdparty_db=db, delete=times)
            assert res != 0
        time.sleep(120)

        # 创建主备cdc任务，klustron为source就是上游时，代表cdc是备的
        if db != 'mongodb':
            res = multi_source.TestCase().create_cdc_task(thirdparty_db=db, table=tb, schema=db_name)
            assert res != 0
            res = multi_source.TestCase().create_cdc_task(thirdparty_db=db, klustron_mode='source', sync_level='table', schema=db_name, table=tb)
            assert res != 0
        else:
            # mongodb如果在没有开启mvcc且引擎为rocksdb的情况下，这部分要先创建klu->mongo再创建mongo->klu
            res = multi_source.TestCase().create_cdc_task(thirdparty_db=db, klustron_mode='source', sync_level='table', schema=db_name, table=tb)
            assert res != 0
            res = multi_source.TestCase().create_cdc_task(thirdparty_db=db, table=tb, schema=db_name)
            assert res != 0
    except Exception as err:
        print(err)
        res = [db, 0]
    return res


# 这里就是检查数据一致性的
def compare_data(db, comp_partition, comp_engine):
    db_name, tb = get_db_tb_name(db=db, engine=comp_engine, partition=comp_partition)
    print('\n开始检查[%s], %s.%s\n' % (db, db_name, tb))
    if db == 'mongodb':
        res = bin.load.mongo.LoadMg().compare_datasize(process=20, tb=tb, db=db_name)
    elif db == 'es':
        res = bin.load.es.LoadEs().compare_data(process=10, index_name=tb)
    return res


def get_res(db, engine, partition):
    # 根据[引擎]和[是否分区]各进行一次测试
    res_list = []
    db_list, engine_list, partition_list = [], [], []
    # 因为外部参数db里面要求多个db同时跑的情况下要用,分开
    # 所以这里就直接判断是否存在','，存在就同时跑多个双活流程
    if ',' in db:
        db_list = str(db).replace(', ', ',').split(',')
        engine_list = str(engine).replace(', ', ',').split(',')
        partition_list = str(partition).replace(', ', ',').split(',')

    if db_list:
        print('本轮双活测试将测试以下用例：')
        for i in range(len(db_list)):
            txt = '\t[%-10s]: 同步表为 [%-10s] 引擎' % (db_list[i], engine_list[i])
            if int(partition_list[i]) == 0:
                txt += ', 且同步表 [不分区]'
            elif int(partition_list[i]) == 1:
                txt += ', 且同步表 [分区]'
            print(txt)
        print('\n开始测试')
        for num in range(len(db_list)):
            times = num + 1
            res = rcr_cdc(db=db_list[num], engine=engine_list[num], partition=int(partition_list[num]), times=times)
            res_list.append(res)
    # 否则 就只跑单个双活的流程
    else:
        res = rcr_cdc(db=db, engine=engine, partition=int(partition))
        res_list.append(res)
    succ, fail = [], []
    print('res = %s' % res_list)
    for i in res_list:
        if i[1] == 1:
            succ.append(i[0])
        elif i[1] == 0:
            fail.append(i[0])

    # 没有失败的就开始检查数据一致性
    if not fail:
        compare_reslist = []
        if db_list:
            for i in range(len(db_list)):
                res = compare_data(db=db_list[i], comp_partition=partition_list[i], comp_engine=engine_list[i])
                compare_reslist.append(res)
        else:
            res = compare_data(db=db, comp_partition=partition, comp_engine=engine)
            compare_reslist.append(res)
        # 结果列表清空再重新统计一次
        succ, fail = [], []
        for i in compare_reslist:
            if i[1] == 1:
                succ.append(i[0])
            elif i[1] == 0:
                fail.append(i[0])
    result = {'succ': succ, 'fail': fail}
    return result


if __name__ == "__main__":
    init_config()
    ps = argparse.ArgumentParser()
    ps.add_argument('--db', help='[mysql]|[mariadb]|[tdengine]|[mongodb]|[es], 如果要同时跑多个，'
                                 '可以用半角逗号","分隔', default='es, mongodb')
    ps.add_argument('--engine', help='[InnoDB]|[rocksdb], db为多个时这个也要用'
                                     '半角逗号","分隔且一一对应上', default='InnoDB, rocksdb')
    ps.add_argument('--partition', help='1为要进行分区，0为不要进行分区，[0]|[1], db为多'
                                        '个时这个也要用半角逗号","分隔且一一对应上', default='1, 0')
    args = ps.parse_args()
    print(args)
    thirdparty_db = args.db
    engine = args.engine
    partition = args.partition
    res = get_res(db=thirdparty_db, engine=engine, partition=partition)
    totalLen = len(res['succ']) + len(res['fail'])
    print('\n======== 测试结果 ========')
    print('当前测试共 %s 项， 成功 %s 项， 失败 %s 项.' % (totalLen, len(res['succ']), len(res['fail'])))
    print('成功项：%s' % res['succ'])
    print('失败项：%s' % res['fail'])
    print('======== 测试结果 ========')
    if totalLen == len(res['succ']):
        exit(0)
    else:
        exit(1)
