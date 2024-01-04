from base.get_conf import *
from base.db_opts import *
from base.conntion import *

def test():
    sqlfile = get_variables().sqlfile()
    dbtype = get_variables().dbtype()
    other_db_info = getconf(0)
    with open(sqlfile, 'r') as f:
        contant = f.readlines()
    db = 'postgres'
    for sql in contant:
        sqllist = sql.split(' ')
        if '\\c' in sqllist:
            new_db = list(sqllist[1])
            del new_db[-1]
            db = ''.join(new_db)
            conn = dbs(1, 'postgres')
            conn.autocomm()
            sqlc = 'create database if not exists %s' % db
            sqld = 'drop database if exists %s' % db
            conn.execsql(sqld)
            conn.execsql(sqlc)
            conn.close()
            break
    conn_klustron = dbs(2, db)
    klustron_create = dbs(2, db)
    tmpsql = ''
    cur_dbtype = 'none'
    server_dict = {}
    pg_function_switch = 0

    for sql in contant:
        # turning sql str type to list type
        sqlsp = sql.split(' ')
        if cur_dbtype == 'none':
            cur_dbtype = choice_db(sqlsp)
        end_symbol = list(sqlsp[-1])
        if 'CREATE' in sql and 'FUNCTION' in sql:
            pg_function_switch = 1
        elif 'language' in sql:
            pg_function_switch = 0
        if sqlsp[0] == '\\c':
            tmpsql = ''
            cur_dbtype = 'none'
            continue
        if cur_dbtype == 'skip':
            cur_dbtype = 'none'
            continue
        if ';' in end_symbol and pg_function_switch == 0:
            if cur_dbtype == 'klustron':
                tmpsql += sql
                if ':' in tmpsql:
                    # :MYSQL_USER_NAME, :MYSQL_PASS
                    if dbtype == 'mysql':
                        if ':MYSQL_HOST' in tmpsql:
                            tmpsql = tmpsql.replace(':MYSQL_HOST', " '%s'" % other_db_info['host'])
                        if ':MYSQL_PORT' in tmpsql:
                            tmpsql = tmpsql.replace(':MYSQL_PORT', " '%s'" % other_db_info['port'])
                        if ':MYSQL_USER_NAME' in tmpsql:
                            tmpsql = tmpsql.replace(':MYSQL_USER_NAME', " '%s'" % other_db_info['user'])
                        if ':MYSQL_PASS' in tmpsql:
                            tmpsql = tmpsql.replace(':MYSQL_PASS', " '%s'" % other_db_info['pass'])
                try:
                    res = conn_klustron.execsql(tmpsql)
                    for txt in res:
                        try:
                            txt = txt.decode(encoding='utf-8')
                            txt = txt.replace('\n', '')
                            print(txt)
                        except:
                            pass
                except Exception as err:
                    print('psycopg2 err: %s' % err)
            elif cur_dbtype == 'create':
                if 'OPTIONS' in sqlsp and 'SERVER' not in sqlsp:
                    sql = rewrite_option(sqlsp)
                tmpsql += str(sql)
                tmpsqlsp = tmpsql.split(' ')
                if 'SERVER' in tmpsqlsp and 'TABLE' not in tmpsqlsp:
                    server_name = tmpsql.split('SERVER')[1].split(' ')[1]
                if 'TABLE' in tmpsqlsp and 'FOREIGN' in tmpsqlsp:
                    if dbtype == 'mysql':
                        try:
                            dbname = tmpsql.split('dbname ')[1].split(',')[0].replace('\'', '')
                        except:
                            dbname = 'empty'
                        try:
                            src_table = tmpsql.split('table_name ')[1].split(')')[0].replace('\'', '')
                        except:
                            try:
                                src_table = tmpsql.split('TABLE_NAME ')[1].split(')')[0].replace('\'', '')
                            except:
                                print('script warning: this create statememt doesn\'t have table name!')
                        dst_table = tmpsql.split(' ')[3].split(' ')[0].split('(')[0].replace('\'', '')
                        tmpdict = {dbname: {dst_table: src_table}}
                        if dbname not in server_dict:
                            server_dict.update({dbname: {}})
                        server_dict[dbname][dst_table] = src_table
                klustron_create.execsql(tmpsql)
            else:
                tmpsql += sql
                if dbtype == 'mysql':
                    sqllist = srctb_sql(server_dict, tmpsql)
                    if sqllist == 'klustron':
                        dbs(2, db).execsql(tmpsql)
                    else:
                        sql = sqllist[1]
                        db = sqllist[0]
                        print('%s - dbname = %s; src_pgsql = %s' % (dbtype, db, tmpsql), end='')
                        dbs(0, db).execsql(sql)
                if dbtype == 'pgsql':
                    print('%s - dbname = %s; src_pgsql = %s' % (dbtype, db, tmpsql), end='')
                    dbs(0, db).execsql(sql)
            cur_dbtype = 'none'
            tmpsql = ''
            print('========')
        else:
            tmpsql += sql

