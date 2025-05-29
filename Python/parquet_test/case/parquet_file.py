import os
import time
from res import other, connection, read_conf


def create_andscp_parquet_file(storage_type='local', interrupt=0):
    # 生成parquet导出软件的命令并执行
    # 生成的文件会移动到./tmp/test.parquet
    # 然后把生成的文件通过ssh分发到所有的server里面去
    conf = read_conf.conf_info()
    versions = connection.meta().kunlun_version()
    meta_dbs = connection.meta().all_meta_format()
    cluster_id = connection.meta().all_cluster_id()[0][0]
    database = conf['res_database']
    table = conf['res_table_name']
    db_tables = database + '_\\$\\$_public.' + table
    tmp_abspath = os.path.abspath('./tmp')
    cdc_home = './tmp/kunlun-cdc-%s/bin' % versions
    cdc_abspath = os.path.abspath(cdc_home)
    shell_parquet = "cd %s; ./dump_table_parquet --meta_dbs %s --meta_user pgx --meta_passwd pgx_pwd --cluster_id %s --db_tables %s " \
                    "--storage_type %s; mv `ls | grep '\.parquet'` test.parquet" % (cdc_abspath, meta_dbs, cluster_id, db_tables, storage_type)
    if interrupt == 0:
        other.run_shell(shell_parquet)
    else:
        # 这里是把parquet放到后台跑，方便后面kill他
        shell_parquet_back = shell_parquet + ' &'
        # 可以用killall，但我不喜欢用
        shell_kill_parquet = "ps -ef | grep dump_table_parquet | awk '{print $2}' | xargs kill -9"
        try:
            other.run_shell(shell_parquet_back)
            print('等待1s后kill掉parquet导出进程')
            time.sleep(1)
            other.run_shell(shell_kill_parquet)
        except Exception as err:
            print(err)
        print('休息5s后开始重新发起parquet数据导出')
        time.sleep(5)
        other.run_shell(shell_parquet)
    shell_mv_parquet = 'rm -rf %s/test.parquet; mv %s/test.parquet %s' % (tmp_abspath, cdc_abspath, tmp_abspath)
    other.run_shell(shell_mv_parquet)
    # 这里开始分发parquet到其它机器
    parquet_obspath = os.path.abspath('./tmp/test.parquet')
    table_path = conf['parquet_table_path']
    other.mv2all_server(abspath=table_path, file=parquet_obspath)



