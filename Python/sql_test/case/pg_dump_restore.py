import time

from res import other, connection, read
from case import load_data
import random
import wget
import os


class TestPgDumpRestore:
    def __init__(self):
        comp_info_list = connection.meta().all_comps()
        tmp_abspath = os.path.abspath('./tmp')
        # 正在运行的计算节点记录中第一个为导出的源节点
        self.source_node = comp_info_list[0]
        # 正在运行的计算节点记录中最后一个为导入的目标节点
        # 在只有一个节点的情况下，第一个和最后一个为同一个节点
        self.target_node = comp_info_list[-1]
        self.conf = read.conf_info()
        version = self.conf['version']
        self.pack_name = 'kunlun-server-%s' % version
        self.tables = ['test1', 'test2', 'test3']
        self.tb_size = ['1000', '5000', '10000']
        self.rand_tb = random.choice(self.tables)
        self.multi_tb = ' -t '.join(self.tables)
        self.dump_loc = '%s/dump.sql' % tmp_abspath

    def print_title(self, txt):
        print()
        title = txt
        title_len = len(title) + 5
        print('=' * title_len)
        print(title)
        print('=' * title_len)

    def download_server(self):
        pack_name = self.pack_name
        urls = 'http://zettatech.tpddns.cn:14000/dailybuilds/enterprise/%s.tgz' % pack_name
        shell_rm = 'rm -rf %s*; rm -rf ./tmp/%s' % (pack_name, pack_name)
        shell_tar = 'tar -zxf %s.tgz' % pack_name
        shell_mv = 'mv %s ./tmp/%s' % (pack_name, pack_name)
        other.run_shell(shell_rm)
        print('wget %s' % pack_name)
        wget.download(url=urls)
        other.run_shell(shell_tar)
        other.run_shell(shell_mv)

    def diff_source_target(self, type):
        res = 1
        print('开始检查源表与目标表一致性')
        source = self.source_node
        target = self.target_node
        source_conn = connection.pgsql(node_info_list=source, db='source')
        target_conn = connection.pgsql(node_info_list=target, db='target')
        diff_times = 0
        if type == 'db' or type == 'multi_table':
            for table in self.tables:
                sql = 'select * from %s' % table
                source_res = source_conn.sql_with_res(sql=sql)
                target_res = target_conn.sql_with_res(sql=sql)
                if target_res != source_res:
                    print('[%s]表不一致' % table)
                    diff_times += 1
        elif type == 'table' or type == 'only_data':
            table = self.rand_tb
            sql = 'select * from %s' % table
            source_res = source_conn.sql_with_res(sql=sql)
            target_res = target_conn.sql_with_res(sql=sql)
            if target_res != source_res:
                print('[%s]表不一致' % self.rand_tb)
                diff_times += 1
        elif type == 'only_create_table':
            source_res = load_data.get_column_info(node_info=source, db='source', table=self.rand_tb)
            target_res = load_data.get_column_info(node_info=target, db='target', table=self.rand_tb)
            if target_res != source_res:
                print('[%s]表不一致' % self.rand_tb)
                diff_times += 1
        if diff_times == 0:
            print('本次检查成功')
        else:
            print('本次检查失败')
            res = 0
        target_conn.close()
        source_conn.close()
        return res

    def drop_create_db(self):
        for node_info in self.source_node, self.target_node:
            if node_info == self.source_node:
                db = 'source'
            else:
                db = 'target'
            print('给节点 %s 创建数据库[%s]' % (node_info, db))
            pg_conn = connection.pgsql(node_info_list=node_info, db='postgres')
            pg_conn.sql('drop database if exists %s;' % db)
            pg_conn.sql('create database if not exists %s;' % db)
            pg_conn.close()

    def drop_target_table(self, tb='all'):
        tables = self.tables
        sql = 'drop table if exists % '
        pg_conn = connection.pgsql(node_info_list=self.target_node, db='postgres')
        if tb == 'all':
            for table in tables:
                pg_conn.sql('drop table if exists %s' % table)
        elif tb == 'signal':
            pg_conn.sql('drop table if exists %s' % self.rand_tb)
        pg_conn.close()

    def dump_case(self, dump_type='db', fc=0):
        res = 1
        txt = 'pg_dump导出 %s' % dump_type
        if fc == 1:
            txt += '并归档'
        self.print_title(txt)
        self.drop_create_db()
        pack_name = self.pack_name
        case = dump_type
        node = self.source_node
        tables = self.tables
        tb_size = self.tb_size
        # pg_dump做的，先创建表，再灌数据，最后dump
        # dump_type：导出的方式[db]|[table]|[only_data]|[only_create_table]|[multi_table]
        try:
            for num in range(len(tables)):
                print('开始创建表%s并灌%s行数据' % (tables[num], tb_size[num]))
                res = load_data.CreateTable().create_table(db='source', table=tables[num])
                if res == 0:
                    return [case, res]
                load_data.load_worker(db='source', table=tables[num], tb_size=tb_size[num])

            shell_dump = 'PGPASSWORD=%s ./tmp/%s/bin/pg_dump --host %s --port %s --username %s ' \
                         '--dbname source --no-shard-option ' % (node[3], pack_name, node[0], node[1], node[2])
            if dump_type == 'table':
                shell_dump += ' -t %s' % self.rand_tb
            elif dump_type == 'only_data':
                shell_dump += ' -t %s -a' % self.rand_tb
            elif dump_type == 'only_create_table':
                shell_dump += ' -t %s -s' % self.rand_tb
            elif dump_type == 'multi_table':
                shell_dump += ' -t %s' % self.multi_tb
            if fc == 1:
                shell_dump += ' -Fc'
            shell_dump +=  ' > %s' % self.dump_loc
            other.run_shell(shell_dump)
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def psql_case(self, psql_type='db'):
        res = 1
        txt = 'psql导入%s' % psql_type
        self.print_title(txt)
        case = psql_type
        target_node = self.target_node
        try:
            if psql_type == 'db' or psql_type == 'multi_table':
                self.drop_target_table(tb='all')
            elif psql_type == 'table' or psql_type == 'only_create_table':
                self.drop_target_table(tb='signal')
            elif psql_type == 'only_data':
                print(target_node)
                load_data.CreateTable().create_table(db='target', table=self.rand_tb, node_info=target_node)
            # psql_type：psql导入的方式[db]|[table]|[only_data]|[only_create_table]|[multi_table]
            case = '%s' % psql_type
            shell_psql = 'psql postgres://%s:%s@%s:%s/target -f %s' % (target_node[2], target_node[3], target_node[0], target_node[1], self.dump_loc)
            other.run_shell(shell_psql, no_echo=1)
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            res = self.diff_source_target(type=psql_type)
        return [case, res]

    def restore_case(self, restore_type='db'):
        res = 1
        txt = 'pg_retore导入%s' % restore_type
        self.print_title(txt)
        case = '%s' % restore_type
        node = self.target_node
        shell_restore = 'PGPASSWORD=%s ./tmp/%s/bin/pg_restore --host %s --port %s --username %s ' \
                        '--dbname target ' % (node[3], self.pack_name, node[0], node[1], node[2])
        try:
            if restore_type == 'only_data':
                # 当只导入数据的时候就提前创建个新表
                load_data.CreateTable().create_table(db='target', table=self.rand_tb, node_info=node)
            else:
                # 否则就用 -c 选项drop掉所有表
                for tb in self.tables:
                    load_data.CreateTable().create_table(db='target', table=tb, node_info=node)
                shell_restore += '-c '
            shell_restore += '-e %s' % self.dump_loc
            out = other.run_shell(shell_restore)
            for txt in out:
                if 'pg_restore' in txt:
                    res = 0
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            res = self.diff_source_target(type=restore_type)
        return [case, res]