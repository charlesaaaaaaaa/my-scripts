from base.get_conf import *
from base.get_func_range import *
from base.translate import *

def choice_db(sql_list):
    dbtype = get_variables().dbtype()
    klustron_opt = ['SELECT', 'select', 'DROP', 'drop', 'ANALYZE', 'analyze', 'COPY', 'copy', 'EXPLAIN', 'SET', 'set', 'GRANT',
                    'grant']
    klustron_create = ['EXTENSION', 'SERVER', 'USER', 'FOREIGN', 'FUNCTION', 'TRIGGER', 'OR', 'type', 'TYPE', 'view', 'VIEW', 'TEMPORARY',
                       'temporary' ,'aggregate', 'AGGREGATE', 'TABLE', 'table', 'OPERATOR', 'operator', 'ROLE', 'role']
    other_db_create = ['']
    other_db_opt = ['INSERT', 'insert', 'UPDATE', 'update', 'DELETE', 'delete']
    if 'CREATE' in sql_list or 'create' in sql_list:
        if sql_list[1] in klustron_create:
            return 'create'
    elif sql_list[0] in klustron_opt:
        return 'klustron'
    elif sql_list[0] in other_db_opt:
        return dbtype
    else:
        return 'skip'

def rewrite_option(sqlsp):
    other_db_info = getconf(0)
    dbtype = get_variables().dbtype()
    if dbtype == 'mysql':
        if "host" in sqlsp or 'port' in sqlsp:
            #sql = "\tOPTIONS (host '%s', port '%s');" % (other_db_info['host'], other_db_info['port'])
            sql = ""
            for tmpsql in sqlsp:
                if tmpsql == 'OPTIONS':
                    sql += "\tOPTIONS "
                elif ':MYSQL_HOST' in tmpsql:
                    sql += str(tmpsql).replace(':MYSQL_HOST', " '%s'" % other_db_info['host'])
                elif ':MYSQL_PORT' in tmpsql:
                    sql += " " + str(tmpsql).replace(':MYSQL_PORT', " '%s'" % other_db_info['port'])
                else:
                    sql += ' ' + tmpsql
        elif 'username' in sqlsp or 'password' in sqlsp:
            #sql = "\tOPTIONS (username '%s', password '%s');" % (other_db_info['user'], other_db_info['pass'])
            sql = ""
            for tmpsql in sqlsp:
                if tmpsql == 'OPTIONS':
                    sql += "\tOPTIONS "
                elif ":MYSQL_USER_NAME" in tmpsql:
                    sql += str(tmpsql).replace(':MYSQL_USER_NAME', " '%s'" % other_db_info['user'])
                elif ":MYSQL_PASS" in tmpsql:
                    sql += str(tmpsql).replace(':MYSQL_PASS', " '%s'" % other_db_info['pass'])
                else:
                    sql += ' ' + tmpsql
        else:
            sql = ' '.join(sqlsp)
            print('script warning: this OPTIONS doesn\'t have node info or user info: %s' % sql)
        return sql

class get_value_field():
    def __init__(self, sql):
        self.sql = sql

    def get_insert(self):
        sql = self.sql
        sym_times, start_sym = 0, 0
        new_sql, new_sql_list = '', []
        try:
            tmpsql = sql.split('VALUES')[1]
        except:
            tmpsql = sql.split('values')[1]
        tmpsql_list = list(tmpsql)
        for sym_left in tmpsql_list:
            if '(' in sym_left:
                sym_times += 1
        for sym in tmpsql_list:
            new_sql += sym
            if '(' == sym:
                start_sym = 1
            elif ')' == sym:
                sym_times -= 1
            if sym_times == 0 and start_sym == 1:
                break
        sql_before_new_sql = sql.split(str(new_sql))[0]
        sql_after_new_sql = sql.split(str(new_sql))[1]
        new_sql_list = [sql_before_new_sql, new_sql, sql_after_new_sql]
        return new_sql_list

    def get_update(self):
        sql = self.sql
        split_list = ['SET']
        sqlsp = sql.split('SET')
        if 'WHERE' in sqlsp[1]:
            tmpsql = str(sqlsp[1])
            split_list.append('WHERE')
            tmpsp = tmpsql.split('WHERE')
            del sqlsp[1]
            for i in tmpsp:
                sqlsp.append(i)
        new_sql_list = ['%s%s' % (sqlsp[0], split_list[0])]
        new_sql_list.append(sqlsp[1])
        if len(split_list) > 1:
            tmpstr = '%s%s' % (split_list[1], sqlsp[2])
            new_sql_list.append(tmpstr)
        return new_sql_list

    def get_delete(self):
        sql = self.sql
        # DELETE FROM fdw126_ft1 WHERE stu_id = 1;
        sqlsp = sql.split(';')
        if 'WHERE' in sqlsp[0]:
            tmpsql = str(sqlsp[0]).split('WHERE')
            sql_before = '%s %s' % (tmpsql[0], 'WHERE')
            sql_middle = tmpsql[1]
            sql_after = ';'
        else:
            sql_before = sqlsp[0]
            sql_middle = ' '
            sql_after = ';'
        new_sql_list = [sql_before, sql_middle, sql_after]
        return new_sql_list


def srctb_sql(server_dict, sql):
    sql_list = sql.split(' ')
    get_value = get_value_field(sql)
    num = 0
    sql_opt = ['INSERT', 'UPDATE', 'DELETE', 'insert', 'update', 'delete']
    for sqlsp in sql_list:
        if sqlsp in sql_opt:
            if sqlsp == 'INSERT':
                newsql_list = get_value.get_insert()
                break
            if sqlsp == 'UPDATE':
                newsql_list = get_value.get_update()
                break
            if sqlsp == 'DELETE':
                newsql_list = get_value.get_delete()
                break
    # 这里是检查update类操作对应的远程表和远程数据库是什么，再返回一个sql和表名
    if 'INSERT' in sql_list:
        for i in sql_list:
            # 这里是找出表名在第几个元素里面，INSERT 和 INTO之后的一个就是表名了
            if i == 'INSERT' or i == 'INTO':
                num += 1
                continue
            else:
                break
    elif 'UPDATE' in sql_list:
        for i in sql_list:
            if i == 'update' or i == 'UPDATE':
                num += 1
                continue
            else:
                break
    elif 'DELETE' in sql_list:
        for i in sql_list:
            if i == 'DELETE' or i == 'delete' or i == 'FROM' or i == 'from':
                num += 1
                continue
            else:
                break
    tbname = newsql_list[0].split(' ')[num]
    stop_signal = 0
    for dbname in server_dict:
        for dst_t in server_dict[dbname]:
            if dst_t == tbname:
                src_t = server_dict[dbname][dst_t]
                stop_signal = 1
                break
        if stop_signal == 1:
            break
    if stop_signal == 0:
        return 'klustron'
    before_list = newsql_list[0].split(' ')
    before_list[num] = '`%s`' % src_t
    before_sql = ' '.join(before_list)
    newsql_list[0] = before_sql
    # 开始处理 有函数的那一段sql
    if "INSERT" in sql:
        value_lists = newsql_list[1]
        if 'CONFLICT' in value_lists:
            if 'DO UPDATE' in newsql_list[2]:
                after_sql = newsql_list[2].split('DO UPDATE SET')[1]
                before = value_lists.replace("ON CONFLICT", 'ON DUPLICATE KEY UPDATE ')
                tmp_list = before.split(' ')
                before_sql = ''
                for tmpsql in tmp_list:
                    if tmpsql == tmp_list[-1]:
                        break
                    before_sql += ' ' + tmpsql
                value_sql = before_sql + after_sql
                newsql_list[2] = ''
            else:
                value_list = value_lists.split('ON CONFLICT')[0]
                value_after = value_lists.split('ON CONFLICT')[1]
                #value_column = value_after.split("CONFLICT")[1]
                first_column = value_after.split(',')[0].replace('(', '')
                value_sql = translate_sql().function_tran_insert(value_list)
                first_value = value_sql.split(',')[0].replace('(', '')
                value_sql += ' ON DUPLICATE KEY UPDATE' + ' %s' % first_column + ' = %s' % first_value
        else:
            value_sql = translate_sql().function_tran_insert(value_lists)
    elif 'UPDATE' in sql:
        v_list = newsql_list[1]
        value_list, value = [], []
        if ',' in v_list:
            values = str(v_list).split(',')
            tmptimes, add_comma = 0, 0
            tmpsql = ''
            for tmpfield in values:
                if add_comma == 0:
                    tmpsql += tmpfield
                else:
                    tmpsql += ', %s' % tmpfield
                if '(' in tmpfield:
                    tmptimes += 1
                    add_comma = 1
                elif ')' in tmpfield:
                    tmptimes -= 1
                if tmptimes == 0:
                    value.append(tmpsql)
                    add_comma = 0
            for sql in value:
                valuesql = sql.split('=')
                value_list.append(valuesql)
        else:
            valuesql = v_list.split('=')
            value_list.append(valuesql)
        value_sql = translate_sql().function_tran_update(value_list)
        if len(value_sql) > 1:
            sql = ' AND '.join(value_sql)
        else:
            sql = ''.join(value_sql)
        value_sql = sql
    elif 'DELETE' in sql:
        value_sql = newsql_list[1]
    newsql_list[1] = value_sql
    if len(newsql_list) >= 3:
        if 'DO NOTHING' in newsql_list[2]:
            newsql_list[2] = newsql_list[2].replace('DO NOTHING', '')
        if 'ON CONFLICT' in newsql_list[2]:
            gets = run_sql()
            pri_key = gets.get_mysql_primary_key(dbname, src_t)
            p_key_pos = gets.get_mysql_primary_key(dbname, src_t)
            for key in p_key_pos:
                if key == pri_key[0]:
                    pos = list.index(list(p_key_pos), key)
            value_list = newsql_list[1].replace('(', '').replace(')', '').split(',')
            values = value_list[pos]
            newsql_list[2] = ' ON DUPLICATE KEY UPDATE %s = %s' % (pri_key, values)
    sql = ' '. join(newsql_list)
    tmplist = [dbname, sql]
    return tmplist