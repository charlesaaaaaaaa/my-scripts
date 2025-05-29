import bin.load.mongo
from xpanel_case import cluster_manage, load, verify_results
from bin import other_opt, connection
import time
import random


class TestCase:
    def __init__(self):
        self.conf = other_opt.getconf().getXpanelInfo()
        self.driver = load.loading().load()
        self.ele = other_opt.getElements()

    def the_first_opt_status(self):
        # 查看操作记录里面的第一条记录名称和状态名
        # 返回两个值，操作记录名和操作记录状态
        driver = self.driver
        ele = self.ele.cluster_manage()
        # 不管在什么界面都要刷新一下，把乱掉的xpath初始化一下
        driver.reflush()
        # 点击操作记录
        time.sleep(1)
        driver.click_Xpath(ele['opt_history'])
        # 获取第一行记录的操作名称和操作状态
        opt_res = driver.gettxt_Xpanth(ele['the_first_opt_result'])
        opt_name = driver.gettxt_Xpanth(ele['the_first_opt_name'])
        time.sleep(1)
        return opt_name, opt_res

    def get_opt_history_result(self, opt_name):
        # 循环调用上面的 the_first_opt_status 函数
        # 直接结果为非 ongoing, 要给一个opt_name, 就是操作的名称，如主备切换，重做备机节点等
        # 返回 非ongoing状态 或者 0，当为0时代表当前第一个操作记录名不是指定的操作名
        history_opt_name, opt_res = self.the_first_opt_status()
        print(history_opt_name, opt_res)
        if opt_name == history_opt_name:
            while 'ongoing' in opt_res:
                time.sleep(2)
                history_opt_name, opt_res = self.the_first_opt_status()
            print(history_opt_name, opt_res)
            if 'done' in opt_res:
                return 1
            else:
                return 0
        else:
            print('第一个操作记录非 [%s]' % opt_name)
            return 0

    def prepare(self, thirdparty_db='mariadb', table_engine=None, partition=0, drop_createdb=1, db_name='testdb', tb_name='testtb'):
        # 删除所有的可能存在的集群并新建一个新集群
        try:
            install_cluster = ['mysql', 'mariadb']
            if thirdparty_db in install_cluster:
                res = cluster_manage.cluster_list().add_new_cluster(show_case=0, cluster_name='%s_master' % thirdparty_db,
                                                                    dont_set_var=1, dont_check_status=1)
                assert res[1] != 0
                # 再新建一个新集群
                res = cluster_manage.cluster_list().add_new_cluster(show_case=0, dont_delete_clsuter=1, cluster_name='%s_slave' % thirdparty_db,
                                                                    dont_set_var=1, dont_check_status=1)
                assert res[1] != 0
                time.sleep(30)
            var_list = ['lock_wait_timeout', 'net_read_timeout', 'net_write_timeout', 'innodb_lock_wait_timeout']
            comp = connection.meta().all_comps_mysqlport()[0]
            print('开始创建klustron同步表')
            # for comp in info:
            print('操作%s:%s' % (comp[0], comp[1]), end='')
            conn = connection.My(host=comp[0], port=comp[1], user=comp[2], password=comp[3], db='public')
            for var in var_list:
                conn.sql('set global %s = 300;' % var)
            if thirdparty_db == 'tdengine':
                # 计算节点上设置个参数，才能运行下面的sql
                # conn.sql("set extra_syntax_mode='TdEngine';")
                # db_name = 'device_shenzhen'
                p_key = 'receive_time'
                # tb_name = 'meter_tj'
                if drop_createdb == 1:
                    conn.sql('CREATE DATABASE IF NOT EXISTS device_shenzhen;')
                    conn.sql('DROP TABLE IF EXISTS %s.%s;' % (db_name, tb_name))
                create_table_sql = "set extra_syntax_mode='TdEngine'; CREATE TABLE IF NOT EXISTS %s.%s (receive_time TIMESTAMP primary key, " \
                                   "mode TEXT, t1 TEXT, t2 TEXT, t3 TEXT, low_pressure INT, low_pressure_recovery INT, magnetic_interference INT" \
                                   ', magnetic_interference_recovery INT, open_lid INT, open_lid_recovery INT, power_down INT, ' \
                                   'power_down_recovery INT, high_pressure INT, high_pressure_recovery INT, batt_status TEXT, ' \
                                   'batt_voltage INT, batt_rep_times INT, center1 TEXT, center2 TEXT, port1 TEXT, port2 TEXT, ' \
                                   'min_presure DOUBLE, max_presure DOUBLE, initial_flow DOUBLE, constant_flow DOUBLE, sim_number ' \
                                   'TEXT, billing_flag INT, meter_datatype TINYINT, meter_readnum DOUBLE, meter_balance INT, ' \
                                   'platform_last_balance INT, platform_price TEXT, platform_balance INT, platform_last_reading DOUBLE, ' \
                                   'meter_volume DOUBLE, meter_time TIMESTAMP, meter_temperature DOUBLE, meter_pressure DOUBLE, ' \
                                   'meter_instantflow DOUBLE, meter_valvestate TINYINT, raw_data TEXT) TAGS (device_id TEXT, sno TEXT, ' \
                                   'model_id TEXT, type_id TEXT, supplier_id TEXT, supplier_device_code TEXT, cust_num TEXT)' % (db_name, tb_name)
            elif thirdparty_db == 'mongodb' or thirdparty_db == 'es':
                p_key = '__sys_obj_id__'
                if drop_createdb == 1:
                    conn.sql('CREATE DATABASE IF NOT EXISTS %s;' % db_name)
                    conn.sql('DROP TABLE IF EXISTS %s.%s;' % (db_name, tb_name))
                create_table_sql = "CREATE TABLE IF NOT EXISTS %s.%s (__sys_obj_id__ VARCHAR PRIMARY KEY,doc LONGTEXT,optype " \
                                   "enum('insert','update','delete') DEFAULT 'insert')" % (db_name, tb_name)
            print('库：【%s】' % db_name)
            conn.close()
            if thirdparty_db not in install_cluster:
                engine_str = ''
                if partition == 1:
                    partition_str = 'partition by hash(%s) partitions 64 with ' % p_key
                    if table_engine:
                        engine_str = "(ENGINE='%s'" % table_engine
                        if table_engine == 'rocksdb':
                            engine_str += ", column_family='cf_%s_%s'" % (thirdparty_db, tb_name)
                        engine_str += ');'
                    else:
                        engine_str = "(ENGINE='innodb');"
                    create_table_sql += partition_str + engine_str
                else:
                    if table_engine:
                        create_table_sql += " with (ENGINE='%s');" % table_engine
                conn = connection.My(host=comp[0], port=comp[1], user=comp[2], password=comp[3], db=db_name)
                print(create_table_sql)
                conn.sql(create_table_sql)
                conn.close()
            return [thirdparty_db, 1]
        except Exception as err:
            print(str(err))
            return [thirdparty_db, 0]

    def create_rcr(self, thirdparty_db):
        # 创建rcr连接
        ele = self.ele.rcr_server()
        driver = self.driver
        # driver.reflush()
        print('创建两个新增集群的rcr连接')
        time.sleep(1)
        print('第一级导航栏的[rcr服务] -- [新增rcr]')
        driver.click_Xpath(ele['rcr_server_button'])
        driver.click_Xpath(ele['add_rcr_button'])
        time.sleep(1)
        print('点击 [主元数据] 下拉框 -- ', end='')
        driver.click_Xpath(ele['add_rcr_master_meta_button'])
        txt, num = '', 1
        try:
            tmp_ele = ele['add_rcr_master_meta_opt_range'] + 'li/span'
            txt = driver.gettxt_Xpanth(tmp_ele)
            assert 'system' in txt
        except:
            while 'system' not in txt:
                tmp_ele = ele['add_rcr_master_meta_opt_range'] + 'li[%s]/span' % num
                txt = driver.gettxt_Xpanth(tmp_ele)
                num += 1
        print('点击第一个选项 [%s]' % txt)
        driver.click_Xpath(tmp_ele)
        print('点击[主集群下拉框] -- 第一个选项：', end='')
        time.sleep(1)
        driver.click_Xpath(ele['add_rcr_master_cluster'])
        txt = driver.gettxt_Xpanth(ele['add_rcr_master_cluster_opt_1'])
        time.sleep(1)
        print('[%s]' % txt)
        driver.click_Xpath(ele['add_rcr_master_cluster_opt_1'])
        print('点击 [备元数据] 下拉框 -- ', end='')
        time.sleep(1)
        driver.click_Xpath(ele['add_rcr_slave_meta_button'])
        txt, num = '', 1
        try:
            tmp_ele = ele['add_rcr_slave_meta_opt_range'] + 'li/span'
            txt = driver.gettxt_Xpanth(tmp_ele)
            assert 'system' in txt
        except:
            while 'system' not in txt:
                tmp_ele = ele['add_rcr_slave_meta_opt_range'] + 'li[%s]/span' % num
                txt = driver.gettxt_Xpanth(tmp_ele)
                num += 1
        print('点击第一个选项 [%s]' % txt)
        driver.click_Xpath(tmp_ele)
        time.sleep(1)
        print('点击[备集群下拉框] -- 第一个选项：', end='')
        driver.click_Xpath(ele['add_rcr_slave_master'])
        time.sleep(1)
        txt = driver.gettxt_Xpanth(ele['add_rcr_slave_master_opt_1'])
        print('[%s]' % txt)
        driver.click_Xpath(ele['add_rcr_slave_master_opt_1'])
        print('点击 [确认]，30s后开始去[操作记录]界面查看结果')
        driver.click_Xpath(ele['add_rcr_submit_button'])
        time.sleep(30)
        res = self.get_opt_history_result(opt_name='新增RCR')
        return [thirdparty_db, res]

    def gen_data(self, thirdparty_db='mysql'):
        try:
            if thirdparty_db == 'mysql' or thirdparty_db == 'mariadb':
                # 在配置文件的%s_host_port和%s_user_pass获取第一个节点的信息来灌数据, 目前是灌到test.test1里面
                host_port = self.conf['%s_host_port' % thirdparty_db].replace(', ', ',').split(',')[0]
                host_source = host_port.split(':')[0]
                port_source = host_port.split(':')[1]
                user_pass = self.conf['%s_user_pass' % thirdparty_db].replace(', ', ',').split(',')[0]
                user_source = user_pass.split('@')[0]
                pass_source = user_pass.split('@')[1]
                cmd = 'python3 xpanel_case/rcr2cdc/mysql_load.py --host %s --port %s --user %s --pwd %s --dbname test --tbname test1 ' \
                      '--create_table y' % (host_source, port_source, user_source, pass_source)
                my_conn = connection.My(host=host_source, port=int(port_source), user=user_source, password=pass_source, db='mysql')
                my_conn.sql('create database if not exists test;')
                my_conn.close()
                res = other_opt.run_shell(cmd)
            # 这是就是固定在rcr主集群计算节点postgres库下创建schema test
            source_comp = connection.meta().all_comps()[0]
            drop_sql = 'drop schema if exists test cascade;'
            sql = 'create schema if not exists test;'
            pg = connection.pgsql(node_info_list=source_comp, db='postgres')
            pg.sql(drop_sql)
            pg.sql(sql)
            pg.close()
            return [thirdparty_db, 1]
        except Exception as err:
            print(str(err))
            return [thirdparty_db, 0]

    def add_metadata_node(self, thirdparty_db='mariadb', index=None, delete=0):
        ele = self.ele.metadata_nodelist()
        cele = self.ele.cluster_manage()
        driver = self.driver
        conf = self.conf
        thirdparty_db_host_port_list = conf['%s_host_port' % thirdparty_db].replace(' ', '').split(',')
        thirdparty_db_user_pass_list = conf['%s_user_pass' % thirdparty_db].replace(' ', '').split(',')
        if delete == 1:
            print('开始尝试删除多出的元数据节点')
            time.sleep(1)
        else:
            print('本次无需删除元数据节点，跳过')
            time.sleep(1)
        while delete == 1:
            try:
                driver.click_Xpath(ele['metadata_node_list_button'])
                driver.click_Xpath(ele['metadata_node_delete_button'])
                time.sleep(2)
                txt = driver.gettxt_Xpanth('//div[@class="el-message-box__message"]/p')
                # 当为0时说明两次获取文本皆失败了，故不存在这个多的元数据节点了
                assert txt != 0
                codes = txt.split('=')[1]
                driver.send_Xpath(cele['warning_code_input'], codes)
                time.sleep(2)
                driver.click_Xpath(cele['warning_code_commit'])
                driver.reflush()
            except Exception as err:
                print('当前已无多出的元数据节点')
                delete = 0
        try:
            for num in range(len(thirdparty_db_host_port_list)):
                if num != 0:
                    driver.reflush()
                print('开始新增元数据[%s]' % thirdparty_db_host_port_list[num])
                print('点击 [元数据节点列表] -- [新增元数据]')
                driver.click_Xpath(ele['metadata_node_list_button'])
                time.sleep(1)
                driver.click_Xpath(ele['add_metadata_button'])
                time.sleep(1)
                current_host_port = str(thirdparty_db_host_port_list[num]).split(':')
                current_user_pass = str(thirdparty_db_user_pass_list[num]).split('@')
                cur_host, cur_port = current_host_port[0], current_host_port[1]
                cur_user, cur_pass = current_user_pass[0], current_user_pass[1]
                if num == 0:
                    metadata_name = '%s_source' % thirdparty_db
                else:
                    metadata_name = '%s_target' % thirdparty_db
                print('将 [%s] 输入到 [元数据名称] 输入框' % metadata_name)
                driver.clearAndSend_Xpath(elements=ele['add_metadata_name_input'], txt=metadata_name)
                time.sleep(1)
                print('点击元数据类型下拉框，并选择', end='')
                driver.click_Xpath(ele['add_metadata_type_button'])
                time.sleep(1)
                db_type = thirdparty_db
                if db_type == 'mariadb':
                    db_type = 'mysql'
                # txt, num = '', 0
                # while txt != db_type:
                #     num += 1
                #     type_ele = ele['add_metadata_type_opt_range'] + 'li[%s]/span' % num
                #     txt = driver.gettxt_Xpanth(type_ele)
                type_ele = '//li[@class="el-select-dropdown__item"]//span[text()="%s"]' % thirdparty_db
                txt = driver.gettxt_Xpanth(type_ele)
                print('[%s]' % txt)
                driver.click_Xpath(type_ele)
                time.sleep(1)
                print('将 [%s] 输入 [ip] 输入框' % cur_host)
                driver.clearAndSend_Xpath(elements=ele['add_metadata_ip_input'], txt=cur_host)
                time.sleep(1)
                print('将 [%s] 输入 [端口号] 输入框' % cur_port)
                driver.clearAndSend_Xpath(elements=ele['add_metadata_port_input'], txt=cur_port)
                time.sleep(1)
                if thirdparty_db != 'es':
                    print('将 [%s] 输入 [数据库用户名] 输入框' % cur_user)
                    driver.clearAndSend_Xpath(elements=ele['add_metadata_user_name_input'], txt=cur_user)
                    time.sleep(1)
                    print('将 [%s] 输入 [密码] 输入框' % cur_pass)
                    driver.clearAndSend_Xpath(elements=ele['add_metadata_pass_input'], txt=cur_pass)
                    time.sleep(1)
                else:
                    print('将 [%s] 输入 [_index] 输入框' % index)
                    driver.clearAndSend_Xpath('//input[@class="el-input__inner" and @placeholder="请输入数据库名称"]', txt=index)
                    time.sleep(3)
                print('点击 [保存]\n')
                driver.click_Xpath(elements=ele['add_metadata_save_button'])
                time.sleep(5)
            return [thirdparty_db, 1]
        except Exception as err:
            print(str(err))
            return [thirdparty_db, 0]

    def create_cdc_server(self, thirdparty_db='mariadb', delete=0):
        # 创建cdc服务，并不是创建cdc连接
        ele = self.ele.cdc_server()
        driver = self.driver
        conf = self.conf
        # driver.reflush()
        time.sleep(15)
        driver.click_Xpath(ele['cdc_server_button'])
        time.sleep(1)
        driver.click_Xpath(ele['cdc_server_level2_button'])
        if delete == 1:
            print('尝试删除已存在的cdc服务')
            while True:
                try:
                    res = driver.click_Xpath(elements='//button[@class="el-button el-button--danger el-button--mini"]//span[text()="删除 "]')
                    assert res != 0
                    res = driver.click_Xpath(ele['cdc_server_delete_commit'])
                    assert res != 0
                except:
                    driver.click_Xpath(ele['cdc_server_delete_button_2'])
                    driver.click_Xpath(ele['cdc_server_delete_commit'])
                    break
        else:
            print('本次无需删除已存在的cdc服务，跳过')
        time.sleep(1)
        print('根据配置文件创建cdc服务')
        # 获取配置文件里面的cdc和对应的第三方数据库连接信息
        cdc_info_list = conf['cdc'].replace(' ', '').split(',')
        print('点击 第一级导航栏的[cdc服务] -- 第二级导航栏的[cdc服务]')
        driver.click_Xpath(ele['cdc_server_button'])
        time.sleep(1)
        driver.click_Xpath(ele['cdc_server_level2_button'])
        # 根据cdc信息列表[cdc_info_list]的长度来进行for循环创建cdc服务
        for i in range(len(cdc_info_list)):
            print('第[%s]次点击[新增cdc]' % str(i + 1))
            driver.click_Xpath(ele['add_cdc_server_button'])
            # 当前循环的cdc信息就是类似 host:port, 如果配置文件没有写错的话
            cdc_info = cdc_info_list[i].split(':')
            cdc_host, cdc_port = cdc_info[0], cdc_info[1]
            time.sleep(2)
            print('将 [%s] 输入 [ip地址] 输入框' % cdc_host)
            driver.clearAndSend_Xpath(elements='//input[@class="el-input__inner" and @placeholder="请输入IP地址"]', txt=cdc_host)
            # driver.clear_send_css(css_element=".el-input__inner[placeholder='请输入IP地址']", txt=cdc_host)
            print('再将 [%s] 输入 [端口号] 输入框' % cdc_port)
            driver.clearAndSend_Xpath(elements='//input[@class="el-input__inner" and @placeholder="请输入端口"]', txt=cdc_port)
            # driver.clear_send_css(css_element='.el-input__inner[placeholder="请输入端口"]', txt=cdc_port)
            print('点击 [确认]\n')
            driver.click_Xpath(ele['add_cdc_submit_button'])
            time.sleep(3)
        print('开始检查cdc服务是否创建正确')
        for i in range(len(cdc_info_list)):
            ele_num = i + 1
            print('点击 [重置]')
            driver.click_Xpath(ele['reset_cdc_ui_button'])
            print('当前第[%s]行rcr服务: ' % ele_num, end='')
            host_ele = ele['cdc_server_level2_ip_range'] + 'tr[%s]/td[3]/div/a/span' % ele_num
            txt = driver.gettxt_Xpanth(host_ele)
            print('host[%s] ' % txt, end='')
            port_ele = ele['cdc_server_level2_host_range'] + 'tr[%s]/td[4]/div' % ele_num
            txt = driver.gettxt_Xpanth(port_ele)
            print('port[%s] ' % txt, end='')
            status_ele = ele['cdc_server_level2_status_range'] + "tr[%s]/td[6]/div/span" % ele_num
            txt = driver.gettxt_Xpanth(status_ele)
            print('status[%s] ' % txt)
            if txt != '服务中':
                print('该cdc服务不处于[服务中]状态，故测试失败')
                return [thirdparty_db, 0]
        return [thirdparty_db, 1]

    def create_status_table(self, db='public'):
        print('开始创建klustron状态表')
        mysql_pro = connection.meta().all_comps_mysqlport()
        rcr_master = mysql_pro[0]
        print('%s@%s,%s:%s, db=[%s]' % (rcr_master[2], rcr_master[3], rcr_master[0], rcr_master[1], db))
        conn = connection.My(host=rcr_master[0], port=rcr_master[1], user=rcr_master[2], password=rcr_master[3], db=db)
        sql_list = ['drop table if exists kunlun_cdc_dump_state;',
                    'CREATE TABLE kunlun_cdc_dump_state(job_id varchar(64) not NULL, repl_info varchar(1024) default "", '
                    'commit_sql_num int default 0, PRIMARY KEY(`job_id`));']
        for sql in sql_list:
            print(sql)
            conn.sql(sql)
        conn.close()

    def create_cdc_task(self, thirdparty_db='mariadb', sync_level='db', klustron_mode='target', schema='public', table='test1', cdc_task_name=None):
        # 创建cdc连接, sync_level=[db]|[table]|[schema], db就是db下面所有的都同步，table就选择其中一个, schema只有在klustron_mode='source'时用
        # klustron_mode = [target]|[source], 当为target时，则上游为第三方数据库，下游为klustron。为source时上游klustron，下游第三方数据库
        ele = self.ele.cdc_server()
        driver = self.driver
        conf = self.conf
        meta_info = verify_results.Meta_Info().metadata_info_format()
        source_db = '%s_source' % thirdparty_db
        target_db = '%s_target' % thirdparty_db
        # 这里的所有source master target salve都是对于cdc而言的，当为source master时说明在多源任务里面这个cdc是处于上游的
        # klustron_master = '%s_master' % thirdparty_db
        # klustron_slave = '%s_slave' % thirdparty_db
        klustron_master = 'master'
        klustron_slave = 'slave'
        print('点击 第一级导航栏的[cdc服务]')
        time.sleep(1)
        try:
            driver.click_Xpath(ele['cdc_server_button'])
            print('检查是否存在 [default]分组, 不存在则刷新页面')
            reflush = 1
            while reflush >= 1:
                print('点击新增cdc任务')
                driver.click_Xpath(ele['add_cdc_task'])
                if klustron_mode == 'target':
                    task_name = '%s_source' % thirdparty_db
                    if cdc_task_name:
                        task_name += cdc_task_name
                else:
                    task_name = '%s_target' % thirdparty_db
                    if cdc_task_name:
                        task_name += cdc_task_name
                print('点击【cdc服务】下拉框')
                driver.click_Xpath('//div[@class="el-select"]//div[@class="el-input el-input--suffix"]//span[@class="el-input__suffix"]', index=1)
                time.sleep(1)
                txt = driver.gettxt_Xpanth('//li[@class="el-select-dropdown__item selected"]//span', index=3)
                print(txt)
                time.sleep(3)
                if txt != 'default':
                    # print('不存在default分组，刷新页面')
                    reflush += 1
                    if reflush >= 10:
                        print('不存在default分组，检查超过10次，请检查cdc进程是否正常')
                        return [thirdparty_db, 0]
                    else:
                        print('不存在default分组，刷新页面')
                    driver.reflush()
                else:
                    print('存在default分组，进行下一步')
                    driver.click_Xpath('//li[@class="el-select-dropdown__item selected"]//span', index=3)
                    driver.reflush()
                    break
            driver.click_Xpath(ele['add_cdc_task'])
            print('输入【任务名称】 为 [%s]' % task_name)
            driver.clearAndSend_Xpath(ele['cdc_task_name_input'], task_name)
            time.sleep(1)
            print('点击数据库类型下拉框', end='')
            driver.click_Xpath(ele['add_cdc_task_db_type'])
            time.sleep(1)
            if klustron_mode == 'source':
                db_type = 'klustron'
            else:
                db_type = thirdparty_db
                if db_type == 'mariadb':
                    db_type = 'mysql'
            time.sleep(1)
            # driver.select_listopt_element 这个方法就是用来点击对应的下拉框列表项的，这个地方太多下拉框了
            driver.select_listopt_element(start_part=ele['cdc_db_type_range'], change_part='li', end_part='/span', txt_info=db_type)
            time.sleep(1)
            print('点击源库信息 下拉框')
            driver.click_Xpath(ele['source_db_info_button'])
            time.sleep(1)
            if klustron_mode == 'source':
                print('选择klustron集群： ', end='')
                # 这里就是选择备的那个klustron集群， 这个备说的是于整个多源里，这个cdc任务是备节点
                driver.select_listopt_element(start_part=ele['source_db_opt_range'], change_part='li', end_part='/span', txt_info='system')
                time.sleep(1)
                driver.select_listopt_element(start_part=ele['source_db_cluster_opt_range'], change_part='li', end_part='/span',
                                              txt_info=klustron_slave)
                time.sleep(1)
                print('点击 源库-库/表 下拉框')
                time.sleep(1)
                driver.click_Xpath(ele['source_db_table_button'])
                print('选择库 ', end='')
                if sync_level == 'db':
                    driver.select_listopt_element(start_part=ele['source_db_table_dblevel_range_opt'], change_part='li', end_part='/span',
                                                  txt_info='postgres', click_end_part='/label/span/span')
                    time.sleep(1)
                elif sync_level == 'table':
                    driver.select_listopt_element(start_part=ele['source_db_table_dblevel_range_opt'], change_part='li', end_part='/span',
                                                  txt_info='postgres')
                    time.sleep(1)
                    print('选择schema ', end='')
                    if sync_level == 'schema':
                        driver.select_listopt_element(start_part=ele['source_db_table_tablelevel_range_opt'], change_part='li', end_part='/span',
                                                      txt_info='public', click_end_part='/label/span/span')
                        time.sleep(1)
                    else:
                        driver.select_listopt_element(start_part=ele['source_db_table_tablelevel_range_opt'], change_part='li', end_part='/span',
                                                      txt_info=schema)
                        time.sleep(1)
                if sync_level == 'table':
                    print('选择表 ', end='')
                    driver.select_listopt_element(start_part=ele['source_db_table_pgtablelevel_range_opt'], change_part='li', end_part='/span',
                                                  txt_info=table, click_end_part='/label/span/span')
                    # driver.click_Xpath(elements='//span[@class="el-cascader-node__label" and text()="%s"]' % table)
                    # time.sleep(1)
                print('点击 导入方式', end='')
                driver.click_Xpath(ele['input_func_button'])
                time.sleep(1)
                print(' -- [全量]')
                driver.click_Xpath(ele['input_all'])
                time.sleep(1)
                print('点击 [目标库设置]')
                driver.click_Xpath(ele['target_db_setting_button'])
                time.sleep(1)
            else:
                # 当klustron在下游时，就是cdc任务是在上游时
                print('选择第三方源: ', end='')
                driver.select_listopt_element(start_part=ele['source_db_opt_range'], change_part='li', end_part='/span', txt_info=source_db)
                # 第三方源只有为mysql或者mariadb才有全量，其它源都要自己手动填写库表
                if thirdparty_db == 'mysql' or thirdparty_db == 'mariadb':
                    print('点击 源库-库/表 下拉框')
                    time.sleep(1)
                    driver.click_Xpath(ele['source_db_table_button'])
                    time.sleep(1)
                    print('选择库 ', end='')
                    if sync_level == 'db':
                        driver.select_listopt_element(start_part=ele['source_db_table_dblevel_range_opt'], change_part='li', end_part='/span',
                                                      txt_info='test', click_end_part='/label/span/span')
                        time.sleep(1)
                    elif sync_level == 'table':
                        driver.select_listopt_element(start_part=ele['source_db_table_dblevel_range_opt'], change_part='li', end_part='/span',
                                                      txt_info='test')
                        time.sleep(1)
                    if sync_level == 'table':
                        print('选择表 ', end='')
                        driver.select_listopt_element(start_part=ele['source_db_table_tablelevel_range_opt'], change_part='li', end_part='/span',
                                                      txt_info='test1', click_end_part='/label/span/span')
                        time.sleep(1)
                    print('点击 导入方式', end='')
                    driver.click_Xpath(ele['input_func_button'])
                    time.sleep(1)
                    print(' -- [全量]')
                    driver.click_Xpath(ele['input_all'])
                    time.sleep(1)
                    print('点击 [目标库设置]')
                    driver.click_Xpath(ele['target_db_setting_button'])
                    time.sleep(1)
                else:
                    # 这里是不同的第三方源cdc任务主页面的一些不同的设置
                    if thirdparty_db == 'tdengine':
                        table_info = 'device_shenzhen.meter_tj'
                        print("【目标表】输入[%s]" % table_info)
                        driver.clear_send_css(css_element='.el-input__inner[placeholder="目标表名称"]', txt=table_info)
                        time.sleep(1)
                    elif thirdparty_db == 'mongodb':
                        thirdparty_db_hp = conf['%s_host_port' % thirdparty_db].replace(' ', '').split(',')
                        database_info = 'mongodb://%s/' % (thirdparty_db_hp[0])
                        print("[数据库]输入[%s]" % database_info)
                        time.sleep(3)
                        driver.clearAndSend_Xpath(elements='//input[@class="el-input__inner" and @placeholder="m.meta_db"]', txt=database_info)
                        time.sleep(1)
                    # 这里是不同的第三方源的shard参数设置
                    print("点击 [shard参数]")
                    driver.click_Xpath(elements='//div[@class="el-form-item__content"]//button[@class="el-button el-button--primary el-button--mini"]',
                                       index=0)
                    time.sleep(1)
                    if thirdparty_db == "tdengine":
                        binlog_file_txt = 'device_shenzhen.meter_tj'
                        print("填写 [binlog file] == [%s]" % binlog_file_txt)
                        driver.clear_send_css(css_element='.el-input__inner[placeholder="binlog file"]', txt='%s' % binlog_file_txt)
                        time.sleep(1)
                        binlog_pos_txt = 'ts>=">=2020-08-15 12:00:00.000"'
                        print('填写 [binlog pos] == [%s]' % binlog_pos_txt)
                        driver.clear_send_css(css_element='.el-input__inner[placeholder="binlog pos"]', txt='%s' % binlog_pos_txt)
                        time.sleep(1)
                        gtid_set_txt = 'ts'
                        print('填写 [gtid set] = [%s]' % gtid_set_txt)
                        driver.clear_send_css(css_element='.el-input__inner[placeholder="gtid set"]', txt='%s' % gtid_set_txt)
                        time.sleep(1)
                    elif thirdparty_db == 'mongodb':
                        binlog_file_txt = 'testdb'
                        print("填写 [binlog file] == [%s]" % binlog_file_txt)
                        driver.clearAndSend_Xpath(elements='//div[@class="el-form-item__content"]//div[@class="el-input el-input--suffix"]/input',
                                                  txt=binlog_file_txt, index=6)
                        time.sleep(1)
                        binlog_pos_txt = table
                        print('填写 [binlog pos] == [%s]' % binlog_pos_txt)
                        driver.clearAndSend_Xpath(elements='//div[@class="el-form-item__content"]//div[@class="el-input el-input--suffix"]/input',
                                              txt=binlog_pos_txt, index=7)
                        time.sleep(1)
                        # gtid_set_txt = str(bin.load.mongo.LoadMg().get_first_id())
                        gtid_set_txt = '000000000000000000000000'
                        print('填写 [gtid set] = [%s], 长度 [%s]' % (gtid_set_txt, len(gtid_set_txt)))
                        driver.clearAndSend_Xpath(elements='//div[@class="el-form-item__content"]//div[@class="el-input el-input--suffix"]/input',
                                                  txt=gtid_set_txt, index=8)
                        time.sleep(1)
                    elif thirdparty_db == 'es':
                        print('点击 [索引名称] 下拉框')
                        driver.click_Xpath(elements='//div[@class="el-input el-input--suffix"]//input[@class="el-input__inner" and '
                                                    '@placeholder="请选择"]', index=2)
                        print('点击 [%s]' % table)
                        try:
                            driver.click_Xpath(elements='//li[@class="el-select-dropdown__item"]//span[text()="%s"]' % table)
                        except:
                            print('尝试点击第二个元素')
                            driver.click_Xpath(elements='//li[@class="el-select-dropdown__item hover"]//span[text()="%s"]' % table)
                    print('点击 [确认]')
                    driver.click_Xpath(elements='//div[@class="dialog-footer"]//button[@class="el-button el-button--primary"]/span')
                    time.sleep(1)
                    print('点击 [目标库设置]')
                    driver.click_Xpath(ele['target_db_setting_button_2'])
            time.sleep(1)
            print('开始点击 [同步插件] 下拉框 两次，第一次为清空选项 -- 选择 ')
            driver.click_Xpath(ele['sync_extension_button'])
            time.sleep(1)
            driver.click_Xpath(ele['sync_extension_button'])
            time.sleep(1)
            # 对应第三方数据库为源表时要用的插件， db和exten_list 一一对应
            # if klustron_mode == 'master':
            #     driver.select_listopt_element(start_part=ele['sync_extension_opt_range'], change_part='li', end_part='/span', txt_info='event_sql')
            if klustron_mode == 'source':
                db = ['mysql', 'mariadb', 'tdengine', 'mongodb', 'es']
                exten_list = ['event_sql', 'event_sql', 'event_tdengine', 'event_mongodb', 'event_es']
                for i in range(len(db)):
                    if db[i] == thirdparty_db:
                        exten_name = exten_list[i]
                # driver.select_listopt_element(start_part=ele['sync_extension_opt_range'], change_part='li', end_part='/span', txt_info=exten_name)
                # print(driver.gettxt_Xpanth('//*[@class="el-select-dropdown__item"]//span[text()="%s"]' % exten_name))
                time.sleep(1)
                driver.click_Xpath('//*[@class="el-select-dropdown__item"]//span[text()="%s"]' % exten_name)
                print('点击 [目标db] -- ', end='')
                time.sleep(1)
                driver.click_Xpath('//div[@class="el-input el-input--suffix"]//input[@placeholder="请选择目标表集群"]')
                time.sleep(1)
                # driver.click_class('.el-input__inner[placeholder="请选择目标表集群"]')
                if klustron_mode == 'source':
                    db_name = '%s_target(%s)' % (thirdparty_db, thirdparty_db)
                    driver.click_Xpath('//li[@class="el-select-dropdown__item"]//span[text()="%s"]' % db_name)
                    time.sleep(1)
                else:
                    db_name = '%s_source(%s)' % (thirdparty_db, thirdparty_db)
                    driver.click_Xpath('//li[@class="el-select-dropdown__item"]//span[text()="%s"]' % db_name)
                    time.sleep(1)
                random_num = random.randint(1, 100000)
                print('日志名额外添加[%s]' % random_num)
                driver.send_Xpath(elements='//input[@class="el-input__inner" and @placeholder="日志名称"]', txt=random_num)
                time.sleep(1)
                # 现在用的是7.15.0的es，所以不用v8了
                # if thirdparty_db == 'es':
                #     print('点击[es_version]下拉框，', end='')
                #     time.sleep(1)
                #     driver.click_Xpath('//input[@class="el-input__inner" and @placeholder="ES版本"]')
                #     print('选择[v8]')
                #     time.sleep(1)
                #     driver.click_Xpath('//li[@class="el-select-dropdown__item"]//span[text()="v8"]')
            if klustron_mode == 'target':
                time.sleep(1)
                print('点击插件[event_sql]')
                driver.click_Xpath('//*[@class="el-select-dropdown__item"]//span[text()="%s"]' % 'event_sql')
                print('sleep 1s并点击[目标DB]')
                time.sleep(1)
                driver.click_Xpath('//input[@class="el-input__inner" and @placeholder="试试搜索"]', index=1)
                print('sleep 1s并点击[system(Klustron)]')
                time.sleep(1)
                driver.click_Xpath('//span[@class="el-cascader-node__label" and text()="system(Klustron)"]')
                db_name = klustron_master
                print('sleep 1s并点击[%s]' % db_name)
                time.sleep(1)
                driver.click_Xpath(elements='//span[@class="el-cascader-node__label" and text()="%s"]' % db_name)
                random_num = random.randint(1, 100000)
                time.sleep(1)
                print('修改日志名, 额外加上[%s]' % random_num)
                driver.send_Xpath(elements='//input[@class="el-input__inner" and @placeholder="test1"]', index=1, txt=random_num)
                time.sleep(1)

            def press_commit():
                print('点击 [确认]，这里只出现一次找不到xpath是正常的，因为这个[确认]的文本有两种写法，只能遍历两次')
                try:
                    res = driver.click_Xpath('//button[@class="el-button el-button--primary"]//span[text()="确认"]')
                    time.sleep(1)
                    assert res != 0
                except:
                    driver.click_Xpath('//button[@class="el-button el-button--primary"]//span[text()=" 确认 "]', index=2)
                    time.sleep(1)
            press_commit()
            time.sleep(1)
            if klustron_mode == 'source' and thirdparty_db == 'mongodb':
                print('再次点击添加 -- 确定')
                driver.click_Xpath('//span[text()=" 添加"]')
                time.sleep(1)
                press_commit()
            print('点击 [确认] 添加cdc任务')
            driver.click_Xpath(ele['add_cdc_task_save_button'])
            print('30s后去[操作记录]界面检查结果')
            time.sleep(30)
        except Exception as err:
            print(str(err))
            return [thirdparty_db, 0]
        res = self.get_opt_history_result(opt_name='add_cdc_worker_list')
        if res == 0:
            return [thirdparty_db, 0]
        return [thirdparty_db, 1]
