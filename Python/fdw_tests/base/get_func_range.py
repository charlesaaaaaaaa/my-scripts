class func_range():
    def __init__(self):
        pass

    def get_range(self, sql, func_name):
        sqllist = str(sql).split()
        print(sqllist)
        sql_lists = []
        if 'INSERT' in sqllist:
            sql_need = str(sql).split('VALUES')[1]
            sql_list = sql_need.split(')')
        for sql in sql_list:
            sqlsp = sql.split(' ')
            tmp_str = ''
            if func_name in sqlsp:
                start_num = list.index(sqlsp, func_name)
                end_num = len(sqlsp)
                for tmpstr in range(start_num, end_num):
                    tmp_str += ' ' + str(sqlsp[tmpstr])
                tmp_str += ')'
                sql_lists.append(tmp_str)
        print(sql_lists)
        return sql_lists
        # start_num = list.index(sql_list, 'decode')
        # end_num = start_num
        # func_str = ''
        # for num in range(start_num, len(sql_list)):
        #     tmplist = list(sql_list[num])
        #     if ')' in tmplist:
        #         end_num += 1
        #         break
        #     end_num += 1
        # for num in range(start_num, end_num):
        #     tmpsql = sql_list[num]
        #     func_str += ' ' + tmpsql
        # strsp = func_str.split(' ')
        # last_list = list(strsp[-1])
        # del_num_list = []
        # for i in range(len(last_list)):
        #     if last_list[i] == ')':
        #         del_num_list.append(i)
        # if len(del_num_list) > 1:
        #     for i in range(1, len(del_num_list)):
        #         del last_list[del_num_list[i]]
        #     del strsp[-1]
        #     last_str = ''.join(last_list)
        #     strsp.append(last_str)
        #     func_str = ' '.join(strsp)