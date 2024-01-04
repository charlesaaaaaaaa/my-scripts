import base64
import subprocess
from base.get_conf import *
from base.conntion import *

class translate_sql():
    def __init__(self):
        self.dbtype = get_variables().dbtype()
        self.conn = dbs(1, 'postgres')

    def function_tran_insert(self, function_list):
        sql_list, sym_times, menbers, tmpsql = [], 0, 0, ''
        func_list = list(function_list)
        for sym in func_list:
            if '(' == sym:
                sym_times += 1
                menbers = 1
            elif ')' == sym:
                sym_times -= 1
            if menbers == 1:
                tmpsql += sym
            if menbers == 0 and sym == ',':
                tmpsql = ''
            if menbers == 1 and sym_times == 0:
                sql_list.append(tmpsql)
                menbers = 0
        sql_list_copy = []
        for sql in sql_list:
            newsql = str(sql).replace('(', '[', 1)
            times = 0
            for sym in list(sql):
                if sym == ')':
                    times += 1
            times -= 1
            newsql = str(newsql).replace(')', ']')
            newsql = str(newsql).replace(']', ')', times)
            sql_list_copy.append(newsql)
        times = 0
        newsql_list = []
        for sql in sql_list_copy:
            tmpsql = ''
            tmplist = []
            start_signal, num, end_signal = 0, 0, 0
            sql = sql.replace('[', '')
            sql = sql.replace(']', '')
            sqlist = sql.split(',')
            for member in sqlist:
                memlist = list(member)
                if '(' in memlist:
                    start_signal = 1
                    for sym in memlist:
                        if sym == '(':
                            times += 1
                elif ')' in memlist:
                    for sym in memlist:
                        if sym == ')':
                            times -= 1
                        if times == 0:
                            end_signal = 1

                if start_signal == 1:
                    if num == 0:
                        tmpsql += member
                        num = 1
                    else:
                        tmpsql += ',' + member
                if times == 0:
                    if end_signal == 0:
                        tmpsql = member
                    start_signal = 0
                    end_signal = 0
                    try:
                        tmpsql = int(tmpsql)
                    except:
                        pass
                    tmplist.append(tmpsql)
                    tmpsql = ''
                    num = 0
            newsql_list.append(tmplist)
        sql_list = []
        for sqlist in newsql_list:
            tmplist = []
            for sql in sqlist:
                sqls = 'select %s' % sql
                if sql == ' NULL' or sql == 'NULL':
                    res = 'this value is NULL'
                else:
                    res = dbs(2, 'postgres').execsql_noprint(sqls)
                if type(sql) == int:
                    res = int(res)
                tmplist.append(res)
            sql_list.append(tmplist)
        #add
        for value in sql_list:
            tmptxt = ''
            num = 0
            for txt in value:
                if num == 0:
                    tmptxt += '('
                    num = 1
                else:
                    tmptxt += ', '
                # else:
                #     if type(txt) != int:
                #         txt = "'%s'" % txt
                #     tmptxt += ', '
                if type(txt) != int:
                    txt = "'%s'" % txt
                try:
                    if '\\x' in txt:
                        txt = txt.replace('\\x', '0x')
                        txt = txt.replace("'", '')
                except:
                    pass
                try:
                    txt = int(txt)
                except:
                    pass
                if txt == "'this value is NULL'":
                    tmptxt += 'NULL'
                else:
                    tmptxt += str(txt)
            if value == sql_list[0]:
                tmpsql += tmptxt + ')'
            else:
                tmpsql += ',' + tmptxt + ')'
        #tmpsql += ')'
        return tmpsql

    def function_tran_update(self, function_list):
        connect_sym = ''
        sql_list = []
        for value in function_list:
            minor_connect_sym = '='
            for sql in value:
                if sql == value[0]:
                    key = sql
                elif sql == value[1]:
                    sqls = 'select %s' % sql
                    value = dbs(2, 'postgres').execsql_noprint(sqls)
            replace_sym_before = ['\\x']
            replace_sym_after = ['0x']
            for replace_sym in replace_sym_before:
                if replace_sym in value:
                    index_num = list.index(replace_sym_before, replace_sym)
                    value = value.replace(replace_sym, replace_sym_after[index_num])
            if type(value) != int:
                add_sym = 1
                for sym in replace_sym_after:
                    if sym in value:
                        add_sym = 0
                        break
                if add_sym == 1:
                    value = "'%s'" % value
            tmpstr = '%s = %s' % (key, value)
            sql_list.append(tmpstr)
        return sql_list

    def function_tran_delete(self, function_list):
        pass

    def decode(self, tran_list):
        # pg内置的decode函数是 文本/二进制字符串转换函数 ， 不是oracle的自定义排序函数
        # decode ( string text, format text ) → bytea, https://www.postgresql.org/docs/current/functions-binarystring.html#ENCODE-FORMAT-BASE64
        # tran_list = ['content', 'format']
        formats = tran_list[1]
        content = tran_list[0]
        if formats == 'base64':
            res = base64.b64decode(bytes(content, encoding='gbk'))
        elif formats == 'hex':
            res = '\\x%s' % content
        elif formats == 'excape':
            res = content.decode()


class use_tools():
    def __init__(self):
        self.dbtype = get_variables().dbtype()