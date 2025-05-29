from res import connection, other
from case import load_data


class TestCase:
    def __init__(self):
        self.meta = connection.meta()
        comps_info_list = self.meta.all_comps()
        self.comp_info = comps_info_list[0]

    def run_sql_list(self, sql_list):
        res = 1
        comp_info = self.comp_info
        try:
            pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres')
            for sql in sql_list:
                print(sql)
                if 'select' in sql and 'declare' not in sql and 'create' not in sql:
                    result = pg_conn.sql_with_res(sql, commit=0)
                    for i in result:
                        print(i)
                else:
                    pg_conn.sql(sql, commit=0)
            pg_conn.close()
        except Exception as err:
            print('ERROR: %s' % err)
            res = 0
        return res

    def cursor_case(self):
        res = 1
        case = '游标'
        sql_list = ["drop table if exists tab1 CASCADE;", "create table tab1(id int primary key,name varchar(23));",
                    "insert into tab1 values(1,'rose'),(2,'irving'),(3,'wade'),(6,'james'),(8,'bryant'),(10,'usakobe'),(11,'irving');",
                    "select * from tab1;", "begin;", "declare curs1 SCROLL cursor for select * from tab1;",
                    "fetch first from curs1;", "fetch next from curs1;", "fetch next from curs1;", "move last in curs1;", "fetch next from curs1;",
                    "close curs1;", "commit;"
                    ]
        res = self.run_sql_list(sql_list)
        return [case, res]

    def view_case(self):
        res = 1
        case = '物化视图'
        comp_info = self.comp_info
        pg_conn = connection.pgsql(node_info_list=comp_info, db='postgres', autocommit=1)
        sql_list_1 = ["drop table if exists t1 CASCADE;", "create table t1(id int primary key,name varchar(23));",
                    "insert into t1 values(1,'rose'),(0,'westbrook'),(2,'kyrie'),(3,'wade'),(6,'LBJ'),(8,'mamba'),(10,'uskobe'),(11,'irving');",
                    "create materialized view mv_t1 as select * from t1;"]
        res = self.run_sql_list(sql_list_1)
        result = load_data.get_column_info(node_info=comp_info, db='postgres', table='mv_t1')
        print('\d mv_t1')
        for i in result:
            print(i)
        sql_list_2 = ["insert into t1 values(20,'allen'),(21,'duncan'),(23,'james'),(24,'bryantkobe');",
                    "select * from t1;",
                    "select * from mv_t1;"]
        sql_list_3 = [
                    "refresh materialized view mv_t1;",
                    "select * from mv_t1;"
                    ]
        res = self.run_sql_list(sql_list_2)
        for sql in sql_list_3:
            print(sql)
            pg_conn.sql(sql, commit=1)
            pg_conn.close()
            # sql_shell = 'psql postgres://%s:%s@%s:%s/postgres -c "%s"' % (comp_info[2], comp_info[3], comp_info[0], str(comp_info[1]), sql)
            # result = other.run_shell(sql_shell)
            # for i in result:
            #     if 'ERROR' in i or 'error' in i:
            #         res = 0
        return [case, res]