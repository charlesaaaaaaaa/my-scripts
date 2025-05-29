import random
from bin.other_opt import *
from xpanel_case.load import *
from xpanel_case.verify_results import *
from xpanel_case import consfailover_case
from bin.load import load_data

class cluster_list():
    def __init__(self):
        self.driver = loading().load()
        self.elements = getElements().cluster_manage()
        self.conf = getconf().getXpanelInfo()

    def the_first_opt_status(self):
        # 查看操作记录里面的第一条记录名称和状态名
        # 返回两个值，操作记录名和操作记录状态
        driver = self.driver
        ele = self.elements
        # 不管在什么界面都要刷新一下，把乱掉的xpath初始化一下
        driver.reflush()
        # 点击操作记录
        sleep(1)
        driver.click_Xpath(ele['opt_history'])
        # 获取第一行记录的操作名称和操作状态
        opt_res = driver.gettxt_Xpanth(ele['the_first_opt_result'])
        opt_name = driver.gettxt_Xpanth(ele['the_first_opt_name'])
        sleep(1)
        return opt_name, opt_res

    def get_opt_history_result(self, opt_name):
        # 循环调用上面的 the_first_opt_status 函数
        # 直接结果为非 ongoing, 要给一个opt_name, 就是操作的名称，如主备切换，重做备机节点等
        # 返回 非ongoing状态 或者 0，当为0时代表当前第一个操作记录名不是指定的操作名
        history_opt_name, opt_res = self.the_first_opt_status()
        print(history_opt_name, opt_res)
        if opt_name == history_opt_name:
            while 'ongoing' in opt_res:
                sleep(2)
                history_opt_name, opt_res = self.the_first_opt_status()
            print(history_opt_name, opt_res)
            if 'done' in opt_res:
                return 1
            else:
                return 0
        else:
            print('第一个操作记录非 [%s]' % opt_name)
            return 0

    @timer
    def delete_all_cluster(self, show_case=1, consfailover=0):
        driver = self.driver
        ele = self.elements
        case = '删除集群'
        if show_case == 1:
            print('=== 现在测试用例为 %s ===' % case)
        res = 0
        def review_status(elements, succdict, second_elements ,errordict):
            # 两个elememt, 可以相同也可以不相同，但第一个一定要给成功的提示语，第二个一定要给失败的提示语
            global a
            times = 1
            a = 1
            while True:
                if a == 0:
                    break
                try:
                    percent = driver.gettxt_Xpanth(elements)
                    assert percent == succdict
                    print(percent)
                    a = 1
                    return a
                    break
                except:
                    try:
                        tinfo = driver.gettxt_Xpanth(second_elements, errordict)
                        if tinfo == errordict:
                            print(errordict)
                            a = 0
                            return 0
                    except:
                        pass
                    if times < 600:
                      times += 1
                      if percent == errordict:
                          print(errordict)
                          a = 0
                          return a
                      sleep(1)
                    else:
                        print('当前新建集群超过10分钟，失败')
                        a = 0
                        return a

        # 现在尝试能否删除存在的集群，不存在集群的话就直接跳过
        delete_times = 0
        try:
            print('try to delete clusters ...')
            while True:
                txt = ''
                driver.click_Xpath(ele['cluster_list_setting_button'])
                driver.click_Xpath(ele['cluster_list_setting_delete_cluster_button'])
                sleep(1)
                txt = driver.gettxt_Xpanth(ele['warning_info'])
                print(txt)
                codes = txt.split('=')[1]
                driver.send_Xpath(ele['warning_code_input'], codes)
                sleep(1)
                driver.click_Xpath(ele['warning_code_commit'])
                if consfailover != 0:
                    if consfailover == 1:
                        res = consfailover_case.kill_metadata_master()
                    if consfailover == 2:
                        res = consfailover_case.kill_cluster_mgr_master()
                    if consfailover == 3:
                        res = consfailover_case.restart_xpanel_server()
                    if res == 1:
                        res = self.get_opt_history_result(case)
                    return [case, res]
                # review_status(ele['cluster_delete_info'], '删除完成100%', ele['cluster_delete_second_info'], '删除shard失败')
                res = 1
                driver.click_Xpath(ele['cluster_delete_info_close'])
                delete_times += 1
        except:
            if res == 1:
                if delete_times >= 1:
                    print('已删除所有集群')
                else:
                    print('当前没有正在运行的集群')
                return [case, 1]
            elif res == 0:
                return [case, 0]

    @timer
    def add_new_cluster(self, db_shard_num=0, db_shard_node_num=0, pg_select_node=0, dont_delete_clsuter=0, dont_check_status=0, show_case=1,
                        cluster_name=None, consfailover=0, dont_set_var=0, install_proxysql=0, close_page=1):
        # db_shard_num: 创建的集群shard数量，默认0时，调用配置文件值
        # db_shard_node_num: 每个shard的副本数，默认0时，调用配置文件值
        # pg_select_node: 计算节点个数，默认0时，调用配置文件值
        # dont_delete_clsuter: 为0时会在创建之前删除所有的可能存在的集群，默认0时，会删除集群
        # dont_check_status: 不检查集群状态，默认为0时，会检查集群状态
        # show_case: 展示现在在做什么； cluster_name: 新增的cluster_name
        # consfailover: 1 - 3, 分别对应三个故障操作
        # dont_set_var: 不去设置超时变量
        # install_proxysql: 安装proxysql集群
        resList = []
        result = 1
        caseName = "新增集群"
        if show_case == 1:
            print('=== 现在测试用例为 %s ===' % caseName)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        if not cluster_name:
            cluster_name = conf['cluster_name']
        if db_shard_num == 0:
            db_shard_num = conf['shard_num']
        if db_shard_node_num == 0:
            db_shard_node_num = conf['shard_node_num']
        if pg_select_node == 0:
            pg_select_node = conf['pg_node']
        driver.click_Xpath(ele['cluster_list'])
        # 检查状态安装或者删除集群的状态
        global a
        #a = 1
        def review_status(elements, succdict, second_elements ,errordict):
            # 两个elememt, 可以相同也可以不相同，但第一个一定要给成功的提示语，第二个一定要给失败的提示语
            global a
            times = 1
            a = 1
            while True:
                if a == 0:
                    break
                try:
                    percent = driver.gettxt_Xpanth(elements)
                    assert percent == succdict
                    print(percent)
                    a = 1
                    return a
                    break
                except:
                    try:
                        tinfo = driver.gettxt_Xpanth(second_elements, errordict)
                        if tinfo == errordict:
                            print(errordict)
                            a = 0
                            return 0
                    except:
                        pass
                    if times < 600:
                      times += 1
                      if percent == errordict:
                          print(errordict)
                          a = 0
                          return a
                      sleep(1)
                    else:
                        print('当前新建集群超过10分钟，失败')
                        a = 0
                        return a

        delete_times = 0
        if dont_delete_clsuter == 0:
            try:
                print('现在尝试能否删除存在的集群，不存在集群的话就直接跳过')
                print('try to delete clusters ...')
                while True:
                    txt = ''
                    driver.click_Xpath(ele['cluster_list_setting_button'])
                    driver.click_Xpath(ele['cluster_list_setting_delete_cluster_button'])
                    sleep(1)
                    txt = driver.gettxt_Xpanth(ele['warning_info'])
                    print(txt)
                    codes = txt.split('=')[1]
                    driver.send_Xpath(ele['warning_code_input'], codes)
                    sleep(1)
                    driver.click_Xpath(ele['warning_code_commit'])
                    self.get_opt_history_result(opt_name='删除集群')
                    # review_status(ele['cluster_delete_info'], '删除完成100%', ele['cluster_delete_second_info'], '删除shard失败')
                    # driver.click_Xpath(ele['cluster_delete_info_close'])
                    delete_times += 1
                    print('点击 集群管理')
                    driver.click_Xpath(ele['cluster_manage_button'])
                    print('点击 集群列表')
                    driver.click_Xpath(ele['cluster_list'])
            except:
                if delete_times >= 1:
                    print('已删除所有集群')
                else:
                    print('当前没有正在运行的集群')
        print('点击 增加集群')
        driver.click_class('el-icon-plus')
        sleep(3)
        # driver.click_Xpath(ele['cluster_list_add_cluster_button'])
        print('填写 集群名 [%s]' % cluster_name)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_business_name'], cluster_name)
        print('点击 下一步')
        driver.click_Xpath(ele['cluster_list_add_cluster_next_1'])
        print('根据本脚本配置文件选择存储节点及计算节点')
        driver.click_Xpath(ele['cluster_list_add_cluster_dblist_button'])
        rangeHead = ele['cluster_list_add_cluster_dblist_button_range']
        #循环点三个db的节点选项
        db_list = str(conf['stor_list']).replace(' ', '').split(',')
        comp_list = str(conf['comp_list']).replace(' ', '').split(',')
        i, num = 1, 1
        sleep(1)
        # for i in range(1, int(db_shard_node_num) + 1):
        while i <= int(db_shard_node_num):
            rangeTail = 'li[%s]/span' % num
            eles = rangeHead + rangeTail
            txt = driver.gettxt_Xpanth(eles)
            if txt in db_list:
                print(txt)
                driver.click_Xpath(eles)
                i += 1
            num += 1
        driver.click_Xpath(ele['cluster_list_add_cluster_dblist_button_end'])
        driver.click_Xpath(ele['cluster_list_add_cluster_pglist_button'])
        rangeHead = ele['cluster_list_add_cluster_pglist_button_range']
        sleep(1)
        # 循环点三个pg的节点选项
        i, num = 1, 1
        while i <= int(db_shard_node_num):
            rangeTail = 'li[%s]/span' % i
            eles = rangeHead + rangeTail
            txt = driver.gettxt_Xpanth(eles)
            if txt in comp_list:
                print(txt)
                i += 1
                driver.click_Xpath(eles)
            num += 1
        driver.click_Xpath(ele['cluster_list_add_cluster_next_2'])
        print('shard_num = [%s], shard_nodes = [%s], pg_nodes = [%s]' % (db_shard_num, db_shard_node_num, pg_select_node))
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shard_num'], db_shard_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shardnode_num'], db_shard_node_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_pg_totalnum'], pg_select_node)
        if install_proxysql == 1:
            print('点击 [安装proxysql]')
            driver.click_Xpath(ele['cluster_list_install_proxysql'])
        print('点击 下一步 -- 确认')
        driver.click_Xpath(ele['cluster_list_add_cluster_next_3'])
        driver.click_Xpath(ele['cluster_list_add_cluster_commit_button'])
        if consfailover != 0:
            if consfailover == 1:
                res = consfailover_case.kill_metadata_master()
            if consfailover == 2:
                res = consfailover_case.kill_cluster_mgr_master()
            if consfailover == 3:
                res = consfailover_case.restart_xpanel_server()
            if res == 1:
                res = self.get_opt_history_result(caseName)
            return [caseName, res]
        sleep(10)
        print('检查结果')
        #resList.append(review_status(ele['install_db_info'], '新增shard成功', '新增shard失败'))
        #resList.append(review_status(ele['install_pg_info'], '新增computer成功', '新增computer失败'))
        # resList.append(review_status(ele['install_cluster_second_info'], '新增集群成功', ele['install_cluster_second_info'], '新增集群失败'))
        resList.append(self.get_opt_history_result('新增集群'))
        for i in resList:
            if i == 0:
                result = 0
                return [caseName, result]
        # 检查所有计算节点都要冒烟成功
        if dont_set_var == 0:
            set_storage_variables()
        if result == 1 and dont_check_status == 0:
            result = Verify().comps()
        if close_page == 1:
            driver.close()
        res = [caseName, result]
        return res

    @timer
    def config_variables(self):
        driver = self.driver
        ele = self.elements
        shard_node_num = int(self.conf['shard_node_num'])
        variableList = ['bg_worker_threads', 'bind_address', 'binlog_cache_size', 'binlog_checksum', 'binlog_encryption', 'binlog_format', 'binlog_group_commit_sync_delay', 'binlog_group_commit_sync_no_delay_count', 'binlog_order_commits', 'binlog_rotate_encryption_master_key_at_startup', 'binlog_row_image', 'binlog_row_metadata', 'binlog_rows_query_log_events', 'binlog_row_value_options', 'binlog_transaction_dependency_history_size', 'binlog_transaction_dependency_tracking', 'block_encryption_mode', 'character-set-server', 'collation-server', 'core-file-size', 'ddc_mode', 'default_authentication_plugin', 'default-storage-engine', 'default-table-encryption', 'default_table_encryption', 'default-tmp-storage-engine', 'default_tmp_storage_engine', 'disabled_storage_engines', 'disconnect_on_net_write_timeout', 'early-plugin-load', 'enable_fullsync', 'enable_global_mvcc', 'encrypt_tmp_files', 'enforce_gtid_consistency', 'extra_max_connections', 'fullsync_consistency_level', 'fullsync_fsync_ack_least_event_bytes', 'fullsync_fsync_ack_least_txns', 'fullsync_fsync_ack_wait_max_milli_secs', 'fullsync_relaylog_fsync_ack_level', 'fullsync_timeout', 'fullsync_warning_timeout', 'gmvcc_register_txns_at_readview_creation', 'gtid_mode', 'ha_role', 'innodb_adaptive_hash_index', 'innodb_adaptive_hash_index_parts', 'innodb_adaptive_max_sleep_delay', 'innodb_buffer_pool_dump_at_shutdown', 'innodb_buffer_pool_instances', 'innodb_buffer_pool_load_at_startup', 'innodb_buffer_pool_size', 'innodb_data_file_path', 'innodb_ddl_buffer_size', 'innodb_ddl_threads', 'innodb_default_encryption_key_id', 'innodb_doublewrite', 'innodb_empty_free_list_algorithm', 'innodb_encryption_rotate_key_age', 'innodb_encryption_rotation_iops', 'innodb_encryption_threads', 'innodb_encrypt_online_alter_logs', 'innodb_extend_and_initialize', 'innodb_fill_factor', 'innodb_flushing_avg_loops', 'innodb_flush_log_at_trx_commit', 'innodb_flush_method', 'innodb_flush_neighbors', 'innodb_fsync_threshold', 'innodb_global_mvcc_skip_row_on_wait_timeout', 'innodb_io_capacity', 'innodb_io_capacity_max', 'innodb_large_prefix', 'innodb_lock_wait_timeout', 'innodb_log_buffer_size', 'innodb_log_compressed_pages', 'innodb_log_files_in_group', 'innodb_log_file_size', 'innodb_lru_scan_depth', 'innodb_max_dirty_pages_pct', 'innodb_max_global_mvcc_read_wait_ms', 'innodb_max_purge_lag', 'innodb_old_blocks_time', 'innodb_open_files', 'innodb_page_size', 'innodb_parallel_dblwr_encrypt', 'innodb_parallel_read_threads', 'innodb_print_all_deadlocks', 'innodb_purge_batch_size', 'innodb_purge_threads', 'innodb_read_io_threads', 'innodb_redo_log_encrypt', 'innodb_report_concur_waits_interval', 'innodb_rollback_segments', 'innodb_sleep_wait_for_free_block', 'innodb_stats_auto_recalc', 'innodb_stats_persistent', 'innodb_strict_mode', 'innodb_sync_array_size', 'innodb_sys_tablespace_encrypt', 'innodb_temp_data_file_path', 'innodb_temp_tablespace_encrypt', 'innodb_thread_concurrency', 'innodb_thread_sleep_delay', 'innodb_undo_log_encrypt', 'innodb_undo_tablespaces', 'innodb_use_fdatasync', 'innodb_write_io_threads', 'join_buffer_size', 'key_buffer_size', 'keyring_file_data', 'local_infile', 'lock_wait_timeout', 'log', 'log-bin', 'log_bin_trust_function_creators', 'log-error', 'log_error_verbosity', 'log_fullsync_replica_acks', 'log_slave_updates', 'log_statements_unsafe_for_binlog', 'log_timestamps', 'long_query_time', 'lower_case_table_names', 'master_info_repository', 'max_allowed_packet', 'max_binlog_size', 'max_connect_errors', 'max_connections', 'max_heap_table_size', 'max_prepared_stmt_count', 'max_relay_log_size', 'metadata_locks_hash_instances', 'myisam_sort_buffer_size', 'mysqlx_max_allowed_packet', 'mysqlx_max_connections', 'net_read_timeout', 'net_write_timeout', 'notify_group_commit_follower_wait', 'open_files_limit', 'optimizer_switch', 'performance_schema', 'pid-file', 'plugin_load', 'plugin_load_add', 'print_extra_info_verbosity', 'prompt', 'query_alloc_block_size', 'query_cache_size', 'query_prealloc_size', 'read_buffer_size', 'read_rnd_buffer_size', 'relay-log', 'relay_log_info_repository', 'replicate-same-server-id', 'replicate_wild_ignore_table', 'report_huge_txn_binlog_threshold', 'rocksdb_block_cache_size', 'rocksdb_block_size', 'rocksdb_deadlock_detect', 'rocksdb_default_cf_options', 'rocksdb_lock_wait_timeout', 'rocksdb_max_background_compactions', 'rocksdb_max_background_flushes', 'rocksdb_max_background_jobs', 'rocksdb_max_open_files', 'rocksdb_max_total_wal_size', 'rocksdb_override_cf_options', 'rocksdb_perf_context_level', 'rocksdb_table_cache_numshardbits', 'secure_auth', 'secure_file_priv', 'server-id', 'skip_fullsync_replica_acks_older_than', 'skip_name_resolve', 'slave_net_timeout', 'slave_parallel_type', 'slave_parallel_workers', 'slave_preserve_commit_order', 'slave_rows_search_algorithms', 'slave_skip_errors', 'slow_logging_start_point', 'slow_query_log', 'slow_query_log_file', 'socket', 'sort_buffer_size', 'sql_mode', 'ssl-ca', 'ssl-cert', 'ssl-key', 'super_read_only', 'sync_frm', 'sync_master_info', 'sync_relay_log', 'sync_relay_log_info', 'table_definition_cache', 'table_encryption_privilege_check', 'table_open_cache', 'thread_cache_size', 'thread_handling', 'thread_pool_eager_mode', 'thread_pool_listen_eager_mode', 'thread_pool_max_threads', 'thread_pool_oversubscribe', 'thread_pool_oversubscribe_congest', 'thread_pool_queue_congest_nwaiters', 'thread_pool_queue_congest_req_timeout', 'thread_pool_size', 'thread_pool_stall_limit', 'thread_stack', 'tmp_table_size', 'tp_add_conn_time_warn_threshold_us', 'transaction-isolation', 'transaction_write_set_extraction']
        #rangeTimes = 1
        rangeTimes = len(variableList)
        errTimes = 0
        caseName = "参数配置"
        print('=== 现在测试用例为 %s ===' % caseName)
        node_info_start = ele['node_role_info_range']
        #variableList = ['fullsync_timeout']
        for i in range(rangeTimes):
            #keys = random.choice(variableList)
            keys = variableList[i]
            value = random.randint(500, 3000)
            driver.click_Xpath(ele['cluster_list_info'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['cluster_list_shard_list'])
            node_role = '备'
            for node_times in range(1, shard_node_num + 1):
                node_role_after = 'tr[%d]/td[4]/div/span' % node_times
                node_role_xpath = node_info_start + node_role_after
                node_role = driver.gettxt_Xpanth(node_role_xpath)
                node_host_after = 'tr[%d]/td[2]/div/span' % node_times
                node_host_xpath = node_info_start + node_host_after
                node_port_after = 'tr[%d]/td[3]/div' % node_times
                node_port_xpath = node_info_start + node_port_after
                node_host = driver.gettxt_Xpanth(node_host_xpath)
                node_port = driver.gettxt_Xpanth(node_port_xpath)
                if node_role == '主':
                    print('当前节点 %s : %s 为 主节点， 继续下一步 。。。' % (node_host, node_port))
                    break
                elif node_role == '备':
                    print('当前节点 %s : %s 为 备节点， 继续寻找主节点 。。。' % (node_host, node_port))
            if node_times == shard_node_num and node_role != '主':
                print('当前未找到主节点，用例失败')
                return [caseName, 0]
            print('开始对主节点变量进行设置')
            more_button_after = 'tr[%d]/td[9]/div/span/span/button/span' % node_times
            more_button = node_info_start + more_button_after
            driver.moveToXpanth(more_button)
            sleep(1)
            driver.click_Xpath(ele['instance_variable_button'])
            print('第 %d 次设置变量：%s = %s' % (i+1, keys, value))
            driver.clearAndSend_Xpath(ele['search_variable_name_input'], keys)
            driver.click_Xpath(ele['search_variable_name_button'])
            sleep(1)
            driver.click_Xpath(ele['set_variable_button'])
            driver.clearAndSend_Xpath(ele['set_variable_input'], value)
            driver.click_Xpath(ele['set_variable_save_button'])
            sleep(3)
            trytimes = 0
            while True:
                trytimes += 1
                try:
                    infos = driver.gettxt_Xpanth(ele['set_variable_alert_info'])
                except:
                    if trytimes >= 10:
                        print('设置变量超过10秒，用例失败')
                        return [caseName, 0]
                if infos == ' 设置实例变量成功 ':
                    print(infos)
                    break
            driver.click_Xpath(ele['close_alert_button'])
            sleep(1)
            driver.moveToXpanth(more_button)
            sleep(1)
            driver.click_Xpath(ele['instance_variable_button'])
            driver.clearAndSend_Xpath(ele['search_variable_name_input'], keys)
            driver.click_Xpath(ele['search_variable_name_button'])
            getValue = driver.gettxt_Xpanth(ele['get_variable_info'])
            driver.click_Xpath(ele['get_variable_close_button'])
            print('获取%s值：' % keys)
            # driver.clearAndSend_Xpath(ele['get_variable_input'], "show variables like '%s';" % keys)
            # driver.click_Xpath(ele['get_variable_save_button'])
            # info = driver.gettxt_Xpanth(ele['get_alert_info'])
            # getValue = info.split('=')[1]
            if int(getValue) == value:
                print('\t%s' % getValue)
            else:
                print('失败，当前 % s设置的值 %s 与获取的值 %s 不同' % (keys, value, getValue))
                errTimes += 1
        if errTimes > 0:
            print('本次测试失败 %s 次, 共测试 %s 次' % (errTimes, rangeTimes))
            a = 0
        else:
            print("本次测试 %s 次，全都成功" % (rangeTimes))
            a = 1
        res = [caseName, a]
        return res

    @timer
    def monitor(self):
        driver = self.driver
        ele = self.elements
        caseName = '实时监控'
        print('=== 现在测试用例为 %s ===' % caseName)
        driver.click_Xpath(ele['cluster_list_info'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_shard_list'])
        monHead = ele['cluster_dbinfo_masterornot_range']
        ipHead = ele['cluster_dbinfo_ip_range']
        hostHead = ele['cluster_dbinfo_host_range']
        for i in range(1, 4):
            monTail = 'tr[%s]/td[4]/div/span' % i
            mon = monHead + monTail
            monTxt = driver.gettxt_Xpanth(mon)
            ipTail = 'tr[%s]/td[2]/div/span' % i
            ip = ipHead + ipTail
            ipTxt = driver.gettxt_Xpanth(ip)
            hostTail = 'tr[%s]/td[3]/div' % i
            host = hostHead + hostTail
            hostTxt = driver.gettxt_Xpanth(host)
            print('当前选中节点 %s: %s 为 %s 节点' % (ipTxt, hostTxt, monTxt) )
            if monTxt == '备':
                break
        disable_button = ele['cluster_dbinfo_disable_button_range']
        disable_ele = disable_button + 'tr[%s]/td[9]/div/button[3]/span' % i
        disableTxt = driver.gettxt_Xpanth(disable_ele)
        if disableTxt == '禁用 ':
            print('当前按钮为禁用， 点击中')
            driver.click_Xpath(disable_ele)
        else:
            print("当前备节点 %s: %s 的禁用按钮不存在，失败" % (ipTxt, hostTxt))
            a = 0
            res = [caseName, a]
            return res
        txt = driver.gettxt_Xpanth(ele['warning_info'])
        wanCode = str(txt).split('=')[1]
        driver.clearAndSend_Xpath(ele['warning_input'], wanCode)
        driver.click_Xpath(ele['disable_node_commit_button'])

        def check_alter_info(elements, caseName, rightTxt, errTxt):
            times = 0
            while True:
                try:
                    txt = driver.gettxt_Xpanth(elements)
                    assert txt == rightTxt
                    print(txt)
                    break
                except:
                    times += 1
                    if times == 150:
                        print('时间超过150，失败')
                        a = 0
                        res = [caseName, a]
                        return res
                    try:
                        if txt == errTxt:
                            a = 0
                            res = [caseName, a]
                            return res
                    except:
                        pass
                    sleep(1)
        check_alter_info(ele['disable_info'], caseName, ' 禁用成功 ', ' 禁用失败 ')
        driver.click_Xpath(ele['disable_alert_close_button'])
        sleep(5)
        driver.reflush()
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_shard_list'])
        restartHead = ele['restart_button_range']
        restart_ele = restartHead + 'tr[%s]/td[9]/div/button[1]/span' % i
        print('点击重启中。。。')
        driver.click_Xpath(restart_ele)
        txt = driver.gettxt_Xpanth(ele['warning_info_restart'])
        restart_code = txt.split('=')[1]
        driver.clearAndSend_Xpath(ele['warning_input_restart'], restart_code)
        driver.click_Xpath(ele['resatart_node_commit_button'])
        check_alter_info(ele['restart_info'], caseName, ' 重启成功 ', ' 重启失败 ')
        driver.click_Xpath(ele['restart_alter_close_button'])
        errTimes = 0
        while True:
            try:
                txt = driver.gettxt_Xpanth(ele['get_node_status'])
                assert txt == '运行中'
                print(txt)
                print('本次测试成功')
                break
            except:
                errTimes += 1
                if errTimes >= 60:
                    a = 0
                    res = [caseName, a]
                    return res
                sleep(1)
        a = 1
        res = [caseName, a]
        return res

    @timer
    def add_storage(self, consfailover=0):
        case = '添加存储节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            conf = getconf().getXpanelInfo()
            db_list = str(conf['stor_list']).replace(' ', '').split(',')
            print('进入集群列表设置界面')
            driver.click_Xpath(ele['cluster_list_setting_button'])
            sleep(2)
            print('点击shard列表, 点击 增加存储节点')
            driver.click_Xpath(ele['cluster_shard_list'])
            sleep(2)
            driver.click_Xpath(ele['add_storage_node_button'])
            print('点击 选择计算机, 选择 计算节点')
            driver.click_Xpath(ele['choice_server'])
            # 如果对应的host在配置文件的存储节点列表里面的话，直接点击然后退出
            num = 1
            while True:
                server_host = ele['server_list_range']
                server_host += 'li[%s]/span' % num
                txt = driver.gettxt_Xpanth(server_host)
                if txt in db_list:
                    driver.click_Xpath(server_host)
                    break
                num += 1
            print('点击 选择计算机，主要是用来收回下拉框的')
            driver.click_Xpath(ele['choice_server'])
            print('点击 shard名称选项，点击 第一个shard选择')
            driver.click_Xpath(ele['select_shard_name'])
            driver.click_Xpath(ele['shard_name_1'])
            print('存储节点数量改为1')
            driver.clearAndSend_Xpath(ele['shard_num_input'], 1)
            print('点击 确认')
            driver.click_Xpath(ele['add_shard_commit'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            sleep(2)
            print('检查xpanel结果')
            res = self.get_opt_history_result('添加存储节点')
            # txt = driver.gettxt_Xpanth(ele['add_replica_res_txt'])
            # txt_bak = txt
            # print(txt_bak)
            # while '正在添加存储节点' in txt:
            #     # 当两个文件不一样的时候把新文本给到备文本，然后打印备文本，一样就不打印了
            #     if txt != txt_bak:
            #         txt_bak = txt
            #         print(txt_bak)
            #     sleep(1)
            #     txt = driver.gettxt_Xpanth(ele['add_replica_res_txt'])
            # print(txt)
            # if txt == '添加存储节点成功':
            #     res = 1
            # else:
            #     res = 0
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    @timer
    def add_comp(self, consfailover=0):
        case = '添加计算节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            conf = getconf().getXpanelInfo()
            comp_list = str(conf['comp_list']).replace(' ', '').split(',')
            print(' 点进集群设置')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            print('点击 左边的 计算节点列表, 点击 添加计算节点')
            driver.click_Xpath(ele['computer_node_list'])
            driver.click_Xpath(ele['add_computer_button'])
            print('点击 选择计算机 下拉框, 选择 计算机host')
            driver.click_Xpath(ele['choice_computer_server'])
            num = 1
            while True:
                eles = ele['computer_server_list_range'] + 'li[%s]/span' % num
                txt = driver.gettxt_Xpanth(eles)
                if txt in comp_list:
                    driver.click_Xpath(eles)
                    break
                num += 1
            print('点击 选择计算机 下拉框, 把下拉框收起来')
            driver.click_Xpath(ele['choice_computer_server'])
            print('清空并发送数字1到计算节点个数文本框里面')
            driver.clearAndSend_Xpath(ele['computer_node_count'], 1)
            print('点击 确定')
            driver.click_Xpath(ele['add_computer_submit'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            print('检查结果')
            res = self.get_opt_history_result('添加计算节点')
            # txt = driver.gettxt_Xpanth(ele['add_computer_res_txt'])
            # txt_bak = ''
            # while '正在添加计算节点' in txt:
            #     sleep(1)
            #     if txt != txt_bak:
            #         txt_bak = txt
            #         print(txt_bak)
            #     txt = driver.gettxt_Xpanth(ele['add_computer_res_txt'])
            # print(txt)
            # if txt == '添加计算节点成功':
            #     res = 1
            # else:
            #     res = 0
            # print('点击 弹窗的 x 关掉弹窗')
            # driver.click_Xpath(ele['add_computer_close_res'])
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    @timer
    def del_comp(self, consfailover=0):
        case = '删除计算节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            print('点击 集群列表 -- 设置 -- 计算节点列表')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['computer_node_list'])
            print('开始计算有几个计算节点')
            num = 0
            while True:
                num += 1
                try:
                    txt = driver.gettxt_Xpanth(ele['comp_node_host_range'] + 'tr[%s]/td[2]/div/span' % num)
                    assert 'xPaTh FaIl' not in txt
                except:
                    num -= 1
                    print('当前有[%s]个计算节点' % num)
                    break
            print('点击 最上面的那行计算节点的删除键')
            driver.click_Xpath(ele['delete_top1_computer'])
            print('获取 确认码')
            num = 1
            while True:
                try:
                    eles = '/html/body/div[%s]' % num + ele['delete_computer_range_tail']
                    txt = driver.gettxt_Xpanth(eles)
                    if '是否继续?code' in txt:
                        txt = str(txt).split('=')[1]
                        break
                except:
                    pass
                num += 1
            print('把 确认码 输入到文本框里')
            eles = '/html/body/div[%s]' % num + ele['delete_computer_code_input_tail']
            driver.clearAndSend_Xpath(eles, txt)
            print('点击 确认')
            eles = '/html/body/div[%s]' % num + ele['delete_computer_commit_tail']
            print(eles)
            driver.click_Xpath(eles)
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            print('检查结果')
            sleep(30)
            res = self.get_opt_history_result('删除计算节点')
            # txt = driver.gettxt_Xpanth(ele['delete_computer_res_txt'])
            # txt_bak = ''
            # while '正在删除计算节点' in txt:
            #     if txt != txt_bak:
            #         txt_bak = txt
            #         print(txt_bak)
            # print(txt)
            # if txt == '删除计算节点成功':
            #     res = 1
            # else:
            #     res = 0
            # print('点击 x 关掉弹窗')
            # driver.click_Xpath(ele['delete_computer_close_button'])
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    @timer
    def del_replica(self, consfailover=0):
        case = '删除存储节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            print('点击 集群列表 -- 设置 -- 存储节点列表')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['cluster_list_shard_list'])
            print('点击 第一个存储节点的 删除键')
            driver.click_Xpath(ele['delele_storage_button'])
            print('把确认case输入到输入框里面')
            txt = driver.gettxt_Xpanth(ele['delete_storage_tips'])
            txt = txt.split('=')[1]
            driver.clearAndSend_Xpath(ele['delete_storage_code_input'], txt)
            print('点击 确认')
            driver.click_Xpath(ele['delete_storage_commit'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            sleep(1)
            print('检查结果')
            res = self.get_opt_history_result('删除存储节点')
            # txt = driver.gettxt_Xpanth(ele['delete_storage_res_txt'])
            # txt_bak = ''
            # while '正在删除存储节点' in txt:
            #     if txt != txt_bak:
            #         txt_bak = txt
            #         print(txt_bak)
            #     txt = driver.gettxt_Xpanth(ele['delete_storage_res_txt'])
            # print(txt)
            # if txt == '删除存储节点成功':
            #     print('succ')
            #     res = 1
            # else:
            #     print('fail')
            #     res = 0
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    @timer
    def rebuild_node(self, consfailover=0):
        case = '重做备机'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        print('点击 集群列表 -- 设置 -- shard列表')
        driver.click_Xpath(ele['cluster_list'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_list_shard_list'])
        print('鼠标放在 更多 上面以显示出重做备机的选项')
        driver.moveToXpanth(ele['rebuild_node_more_button'])
        print('点击 重做备机')
        driver.click_Xpath(ele['rebuild_node_button'])
        print('点击 确认')
        sleep(1)
        driver.click_Xpath(ele['rebuild_node_commit'])
        if consfailover != 0:
            if consfailover == 1:
                res = consfailover_case.kill_metadata_master()
            if consfailover == 2:
                res = consfailover_case.kill_cluster_mgr_master()
            if consfailover == 3:
                res = consfailover_case.restart_xpanel_server()
            if res == 1:
                res = self.get_opt_history_result(case)
            return [case, res]
        sleep(20)
        print('获取结果')
        res = self.get_opt_history_result('重做备机节点')
        # txt = ''
        # try:
        #     txt = driver.gettxt_Xpanth(ele['rebuild_node_res_txt'])
        # except:
        #     pass
        # while 'xPaTh FaIl' in txt:
        #     try:
        #         txt = driver.gettxt_Xpanth(ele['rebuild_node_res_txt'])
        #         sleep(3)
        #     except:
        #         pass
        # print(txt)
        # if txt == '重做备机节点成功':
        #     res = 1
        # else:
        #     res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    @timer
    def manual_swich_master(self, consfailover=0):
        case = '主备切换'
        print('=== 现在测试用例为 %s ===' % case)
        ele = self.elements
        driver = self.driver
        try:
            print('点击 集群列表 -- 设置')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            print('点击 一级主备切换， 然后再点击下面的二级主备切换进入到主备切换页面')
            driver.click_Xpath(ele['manual_switch_level_1'])
            driver.click_Xpath(ele['manual_switch_level_2'])
            print('点击 shard名称 下拉框，然后点击第一个选项', end='')
            driver.click_Xpath(ele['manual_switch_shard_name'])
            txt = driver.gettxt_Xpanth(ele['manual_switch_shard_name_1'])
            print(' [%s]' % txt)
            driver.click_Xpath(ele['manual_switch_shard_name_1'])
            print('点击 备机节点 下拉框， 然后点击第一个选项', end='')
            driver.click_Xpath(ele['manual_switch_replace_list'])
            master_node_front = driver.gettxt_Xpanth(ele['manual_switch_replace_1'])
            txt = driver.gettxt_Xpanth(ele['manual_switch_replace_1'])
            print(' [%s]' % txt)
            driver.click_Xpath(ele['manual_switch_replace_1'])
            print('点击 保存(确认？)')
            driver.click_Xpath(ele['manual_switch_commit_button'])
            sleep(1)
            print('获取 弹窗里面的code码，然后输入到输入框里', end='')
            txt = driver.gettxt_Xpanth(ele['manual_switch_code_txt'])
            txt = txt.split('=')[1]
            driver.clearAndSend_Xpath(ele['manual_switch_code_input'], txt)
            print('code = [%s]' % txt)
            print('点击 确认')
            driver.click_Xpath(ele['manual_switch_commit_button_2'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            sleep(30)
            print('点击 弹窗的 x 关闭按钮, 然后刷新页面快速返回集群列表页面')
            driver.click_Xpath(ele['manual_switch_close_alert_button'])
            # print('获取 操作记录里面第一个记录的状态，只要不是done都是认为api失败了')
            # opt_status = self.get_opt_history_result(case)
            # if opt_status != ' done ':
            #     print(opt_status)
            #     return [case, 0]
            driver.reflush()
            print('遍历 集群存储节点列表，查看哪个是主，确认后直接退出')
            try:
                driver.click_Xpath(ele['cluster_manage_button'])
            except:
                driver.click_Xpath(ele['cluster_manage_button_1'])
            try:
                driver.click_Xpath(ele['cluster_list'])
            except:
                driver.click_Xpath(ele['cluster_list_1'])
            for i in range(1, 10):
                tail = 'tr[%s]/td[5]/div/span' % i
                head = ele['manual_switch_member_status_range']
                master_xpath = head + tail
                txt = driver.gettxt_Xpanth(master_xpath)
                if txt == '主':
                    break
            print('查看host 和port')
            host = driver.gettxt_Xpanth(ele['manual_switch_storage_host_range'] + 'tr[%s]/td[1]/div' % i)
            port = driver.gettxt_Xpanth(ele['manual_switch_storage_port_range'] + 'tr[%s]/td[2]/div' % i)
            master_node_info = '%s(%s)' % (host, port)
            print('当前主节点是 [%s], 选择的切主的备节点是 [%s]' % (master_node_info, master_node_front))
            if master_node_info == master_node_front:
                res = 1
            else:
                res = 0
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        if res == 1:
            res = self.get_opt_history_result(opt_name='主备切换')
        return [case, res]

    @timer
    def unswitch_setting(self, consfailover=0):
        case = '免切设置'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        try:
            print('点击 集群免切设置 -- 免切设置')
            driver.click_Xpath(ele['cluster_unswitch_settings'])
            driver.click_Xpath(ele['unswitch_setting'])
            sleep(1)
            print('点击 all(集群)')
            driver.click_Xpath(ele['unswitch_cluster_all'])
            print('点击 选择sahrd -- 第一个shard', end='')
            driver.click_Xpath(ele['unswitch_shard_name'])
            txt = driver.gettxt_Xpanth(ele['unswitch_shard_1'])
            print(' [%s]' % txt)
            driver.click_Xpath(ele['unswitch_shard_1'])
            unswitch_timeout = 10000
            print('设置 超时时间 [%s]' % unswitch_timeout)
            driver.clearAndSend_Xpath(ele['unswitch_cluster_timeout_input'], unswitch_timeout)
            print('点击确认')
            driver.click_Xpath(ele['unswitch_commit_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            # 这里做操作
            sleep(2)
            txt = driver.gettxt_Xpanth(ele['unswitch_delete_shard'])
            if txt == '删除 ':
                print('存在删除免切键，故免切设置成功')
            else:
                print('不存在删除免切键，故免切设置失败')
                return [case, 0]
            print('开始删除免切设置， 点击删除')
            driver.click_Xpath(ele['unswitch_delete_shard'])
            txt = driver.gettxt_Xpanth(ele['unswitch_delete_code_txt'])
            txt = txt.split('=')[1]
            print('获取 确认码[%s], 并输入到输入框里' % txt)
            driver.clearAndSend_Xpath(ele['unswitch_delete_code_input'], txt)
            print('点击 确认')
            driver.click_Xpath(ele['unswitch_delete_commit_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            sleep(1)
            print('检查是否存在 删除免切键')
            txt = driver.gettxt_Xpanth(ele['unswitch_delete_shard'])
            if txt == '删除 ':
                print('存在删除免切键，故删除免切设置失败')
                return [case, 0]
            else:
                print('不存在删除免切键，故删除免切设置成功')
            res = 1
        except Exception as err:
            print(err)
            res = 0
        if res == 1:
            # 检查所有计算节点都要冒烟成功
            res = Verify().comps()
        return [case, res]

    def add_shard(self, consfailover=0):
        case = '添加(扩容)shard'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        try:
            print('点击 集群列表 -- 设置 -- shard列表')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['cluster_list_shard_list'])
            print('点击 添加shard ')
            driver.click_Xpath(ele['add_shard_button'])
            print('点击 选择计算机下拉框')
            driver.click_Xpath(ele['add_shard_choice_server'])
            print('点击 配置的ip')
            server_iplist, num = [], 1
            stor_list = conf['stor_list']
            while True:
                try:
                    eles = ele['add_shard_server_range'] + 'li[%s]/span' % num
                    txt = driver.gettxt_Xpanth(eles)
                    assert 'xPaTh' not in txt
                    server_iplist.append(txt)
                except:
                    break
                num += 1
            num = 0
            for i in server_iplist:
                num += 1
                if i in stor_list:
                    driver.click_Xpath(ele['add_shard_server_range'] + 'li[%s]/span' % num)
                    print(i)
            print('填写shard个数为[1], 副本数为[2]')
            driver.clearAndSend_Xpath(ele['add_shard_count_input'], 1)
            driver.clearAndSend_Xpath(ele['add_shard_nodes_input'], 2)
            print('点击 确认')
            driver.click_Xpath(ele['add_shard_commit_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            res = self.get_opt_history_result('添加shard')
            print('检查结果')
            # txt = driver.gettxt_Xpanth(ele['add_shard_result_txt'])
            # while txt == '正在添加shard':
            #     sleep(1)
            #     txt = driver.gettxt_Xpanth(ele['add_shard_result_txt'])
            # print(txt)
            # if txt == '添加shard成功':
            #     res = 1
            #     print('等待30s后检查计算节点')
            #     sleep(30)
            # else:
            #     res = 0
            if res == 1:
                # 检查所有计算节点都要冒烟成功
                res = Verify().comps()
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def del_shard(self, consfailover=0):
        case = '删除(缩容)shard'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        try:
            print('点击 集群列表 -- 设置 -- shard列表')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['cluster_list_shard_list'])
            print('点击 删除')
            driver.click_Xpath(ele['delete_shard_button'])
            txt = driver.gettxt_Xpanth(ele['delete_shard_code_txt']).split('=')[1]
            # txt = driver.gettxt_Xpanth(ele['delete_shard_code_txt'])
            print(txt)
            print('获取确认code[%s]并填入输入框' % txt)
            driver.clearAndSend_Xpath(ele['delete_shard_code_input'], txt)
            print('点击 确认')
            driver.click_Xpath(ele['delete_shard_commit_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 1:
                    res = self.get_opt_history_result(case)
                return [case, res]
            print('检查结果')
            res = self.get_opt_history_result('删除shard')
            # txt = driver.gettxt_Xpanth(ele['delete_shard_result_txt'])
            # while txt == '正在删除shard':
            #     sleep(1)
            #     txt = driver.gettxt_Xpanth(ele['delete_shard_result_txt'])
            # print(txt)
            # if txt == '删除shard成功':
            #     res = 1
            # else:
            #     res = 0
            if res == 1:
                # 检查所有计算节点都要冒烟成功
                res = Verify().comps()
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def manual_backup(self, consfailover=0):
        case = '物理(全量)备份'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        try:
            print('开始创建1个集群')
            res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_check_status=1)
            driver.reflush()
            if res[1] == 0:
                return [case, res[1]]
            comp = Meta_Info().all_comps()[-1]
            sleep(5)
            Verify().load_worker(comp_info=comp, threads=1)
            print('点击 集群列表 -- 设置 -- 备份恢复')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['backup_restore_button'])
            print('点击 全量备份 -- 发起全量备份')
            driver.click_Xpath(ele['manual_backup_button'])
            driver.click_Xpath(ele['send_manualbackup_api_button'])
            print('点击 确定')
            driver.click_Xpath(ele['manual_backup_commit_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            print('检查结果\nsleep 30s后点击全量备份记录')
            sleep(30)
            driver.click_Xpath(ele['manual_backup_history'])
            print('查看每个任务的状态')
            res_list = []
            # 先把所有的任务状态给到一个列表里面
            while res_list == []:
                num = 0
                while True:
                    num += 1
                    try:
                        driver.click_Xpath(ele['manual_backup_reset'])
                        eles = ele['manual_backup_status_range'] + 'tr[%s]/td[7]/div/span' % num
                        txt = driver.gettxt_Xpanth(eles)
                        assert 'xPaTh FaIl' not in txt
                        print(txt)
                        res_list.append(txt)
                    except Exception as err:
                        print(err)
                        break
                sleep(5)
            print(res_list)
            # 当这个列表里面有 ongoing 的时候，则会不断获取对应的xpath文本
            while 'ongoing' in res_list:
                num = 0
                driver.click_Xpath(ele['manual_backup_reset'])
                for i in res_list:
                    num += 1
                    if i == 'ongoing':
                        eles = ele['manual_backup_status_range'] + 'tr[%s]/td[7]/div/span' % num
                        txt = driver.gettxt_Xpanth(eles)
                        list_index = num - 1
                        res_list[list_index] = txt
                print(res_list)
                sleep(5)
            print(res_list)
            err_times = 0
            # 统计这个列表里面有几个非'done'的元素
            # 有1个以上则代表任务起码有1个失败了，所以就不用进行后面的结果检查了，直接认为失败
            for i in res_list:
                if i != 'done':
                    err_times += 1
            if err_times == 0:
                res = 1
            else:
                res = 0
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def manual_restron(self, consfailover=0):
        case = '物理恢复(回档)'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        try:
            print('开始创建另一个集群')
            res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_delete_clsuter=1, dont_check_status=1)
            driver.reflush()
            if res[1] == 0:
                return [case, res[1]]
            print('点击 集群列表 -- 设置 -- 备份恢复')
            driver.click_Xpath(ele['cluster_list'])
            sleep(1)
            driver.click_Xpath(ele['cluster_list_setting_button'])
            sleep(1)
            driver.click_Xpath(ele['backup_restore_button'])
            sleep(1)
            print('点击 全量回档')
            driver.click_Xpath(ele['cluster_restore_button'])
            sleep(1)
            print('点击 原集群名称下拉框')
            driver.click_Xpath(ele['cluster_restore_cluster_name'])
            sleep(1)
            txt = driver.gettxt_Xpanth(ele['cluster_restore_first_opt_name'])
            sleep(1)
            print('点击 第一个选项 [%s]' % txt)
            driver.click_Xpath(ele['cluster_restore_first_opt_name'])
            sleep(1)
            print('点击 回档时间')
            driver.click_Xpath(ele['cluster_restore_time'])
            sleep(1)
            print('点击 此刻')
            driver.click_Xpath(ele['cluster_restore_current_time'])
            sleep(1)
            print('点击 回档')
            driver.click_Xpath(ele['cluster_restore_commit_button'])
            sleep(1)
            print('点击 确定')
            driver.click_Xpath(ele['cluster_restore_commit2_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            sleep(1)
            print('检查结果')
            # txt = driver.gettxt_Xpanth(ele['cluster_restore_result_txt'])
            # print(txt)
            # while txt == ' 正在回档集群... ':
            #     sleep(1)
            #     txt = driver.gettxt_Xpanth(ele['cluster_restore_result_txt'])
            res = self.get_opt_history_result(opt_name='回档集群')
            if res == 1:
                res = Verify().comps()
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def logic_backup(self, consfailover=0):
        case = '逻辑备份'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        try:
            print('开始创建1个集群')
            res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_check_status=1, show_case=0, close_page=0)
            driver.reflush()
            if res[1] == 0:
                return [case, res[1]]
            comp = Meta_Info().all_comps()[-1]
            print(comp)
            sleep(5)
            try:
                Verify().load_worker(comp_info=comp, threads=1)
            except Exception as err:
                print(err)
            print('点击 集群列表 -- 设置 -- 备份恢复')
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['backup_restore_button'])
            print('点击 逻辑备份')
            driver.click_Xpath(ele['logic_backup_button'])
            sleep(3)
            print('点击 备份对象下拉框 并选择 库 -- schema -- 表')
            driver.click_Xpath(ele['logic_backup_object'])
            ele_list = ['logic_backup_object_db', 'logic_backup_object_schema', "logic_backup_object_table"]
            for i in ele_list:
                txt = driver.gettxt_Xpanth(ele[i])
                print('    选择 [%s]' % txt)
                driver.click_Xpath(ele[i])
            print('选择 逻辑备份时间')
            driver.click_Xpath(ele['logic_backup_time_start'])
            start_time = driver.gettxt_Xpanth(ele['logic_backup_time_start_opt1'])
            print('start_time = %s' % start_time)
            sleep(3)
            driver.click_Xpath(ele['logic_backup_time_start_opt1'])
            driver.click_Xpath(ele['logic_backup_time_end'])
            end_time = driver.gettxt_Xpanth(ele['logic_backup_time_end_opt1'])
            print('end_time = %s' % end_time)
            sleep(3)
            driver.click_Xpath(ele['logic_backup_time_end_opt1'])
            print('点击 保存 并/home/charles/daily_smoke/daily_conf/cluster_mgr_api_test等待30s后检查')
            driver.click_Xpath(ele['logic_backup_save_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            sleep(30)
            res = self.get_opt_history_result(opt_name=case)
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def logic_restore(self, consfailover=0):
        case = '逻辑恢复'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        print('开始创建另一个集群')
        try:
            res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_delete_clsuter=1, dont_check_status=1,
                                       show_case=0, close_page=0)
            driver.reflush()
            if res[1] == 0:
                return [case, res[1]]
            print('等待600s后每1分钟检查一次冷备节点')
            sleep(600)
            res = Meta_Info().wait_backup_node()
            if res == 0:
                return [case, 0]
            sleep(30)
            print('点击 集群列表 -- 设置 -- 备份恢复')
            driver.click_Xpath(ele['cluster_list'])
            sleep(1)
            driver.click_Xpath(ele['cluster_list_setting_button'])
            sleep(1)
            driver.click_Xpath(ele['backup_restore_button'])
            sleep(1)
            comps = Meta_Info().all_comps()
            print('点击 逻辑恢复')
            driver.click_Xpath(ele['logic_restore_button'])
            print('点击 原集群名称 下拉框, ', end='')
            driver.click_Xpath(ele['logic_restore_res_cluster_name'])
            txt = driver.gettxt_Xpanth(ele['logic_restore_res_cluster_name_opt1'])
            print('点击 第一个选项[%s]' % txt)
            driver.click_Xpath(ele['logic_restore_res_cluster_name_opt1'])
            print('点击 备份记录, ', end='')
            driver.click_Xpath(ele['logic_restore_backup_history'])
            txt = driver.gettxt_Xpanth(ele['logic_restore_backup_history_opt1'])
            print('点击 第一个记录[%s]' % txt)
            driver.click_Xpath(ele['logic_restore_backup_history_opt1'])
            print('点击 起时时间, ', end='')
            driver.click_Xpath(ele['logic_restore_start_time'])
            txt = driver.gettxt_Xpanth(ele['logic_restore_current_time'])
            print('点击 此刻')
            sleep(300)
            try:
                res = driver.click_Xpath(ele['logic_restore_current_time'])
                assert res == 1
            except Exception as err:
                print(err)
                print('点击另一个[此刻]按钮元素')
                driver.click_Xpath(ele['logic_restore_current_time_bak1'])
                assert res == 1
            print('点击 保存')
            driver.click_Xpath(ele['logic_restore_save_button'])
            if consfailover != 0:
                if consfailover == 1:
                    res = consfailover_case.kill_metadata_master()
                if consfailover == 2:
                    res = consfailover_case.kill_cluster_mgr_master()
                if consfailover == 3:
                    res = consfailover_case.restart_xpanel_server()
                if res == 0:
                    return [case, res]
            print('等待30s后开始检查结果')
            sleep(30)
            res = self.get_opt_history_result(opt_name=case)
            if res == 1:
                res = Verify().review_worker(res_comp_info=comps[0], dst_comp_info=comps[-1])
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def repartition_table(self):
        case = '表重分布'
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        # 创建第一个集群
        res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_check_status=1, dont_set_var=1, close_page=0)
        if res == 0:
            return [case, 0]
        driver.reflush()
        # 创建第二个集群
        res = self.add_new_cluster(db_shard_num=1, db_shard_node_num=2, pg_select_node=1, dont_check_status=1, dont_delete_clsuter=1, close_page=0)
        if res == 0:
            return [case, 0]
        cluster_ids = Meta_Info().all_cluster_id_name()
        target_name = cluster_ids[0][1]
        comp_infos = Meta_Info().all_comps()
        print('给两个集群的计算节点创建相同结构的表')
        for i in range(-1, 1):
            res = load_data.create_table(node_info=comp_infos[i])
            if res == 0:
                return [case, 0]
        print('对源表准备数据')
        load_data.load_worker(node_info=comp_infos[-1])
        driver.reflush()
        print('点击 集群列表 -- 设置 -- 表重分布')
        driver.click_Xpath(ele['cluster_list'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['repart_table_button'])
        print('选择目标表集群为', end='')
        driver.click_Xpath(ele['repart_table_target_cluster'])
        txt, tmp_ele, num = '', '', 0
        while target_name not in txt:
            num += 1
            tmp_ele = ele['target_cluster_range'] + 'li[%s]/span' % num
            txt = driver.gettxt_Xpanth(tmp_ele)
        print(' [%s]' % txt)
        driver.click_Xpath(tmp_ele)
        print('源表 选择为', end='')
        driver.click_Xpath(ele['repart_table_souce_table'])
        txt = driver.gettxt_Xpanth(ele['source_table_db_opt1'])
        print(' [%s] ' % txt, end='')
        driver.click_Xpath(ele['source_table_db_opt1'])
        txt = driver.gettxt_Xpanth(ele['source_table_schema_opt1'])
        print('-- [%s] ' % txt, end='')
        driver.click_Xpath(ele['source_table_schema_opt1'])
        txt = driver.gettxt_Xpanth(ele['source_table_table_opt1'])
        print('-- [%s]' % txt)
        driver.click_Xpath(ele['source_table_table_opt1'])
        print('目标表选择为', end='')
        driver.click_Xpath(ele['repart_table_target_table'])
        txt = driver.gettxt_Xpanth(ele['target_table_db_opt1'])
        print(' [%s] ' % txt, end='')
        driver.click_Xpath(ele['target_table_db_opt1'])
        txt = driver.gettxt_Xpanth(ele['target_table_schema_opt1'])
        print('-- [%s] ' % txt, end='')
        driver.click_Xpath(ele['target_table_schema_opt1'])
        txt = driver.gettxt_Xpanth(ele['target_table_table_opt1'])
        print('-- [%s] ' % txt)
        driver.click_Xpath(ele['target_table_table_opt1'])
        print('点击 不替换目标表名')
        driver.click_Xpath(ele['no_replace_target_tbname'])
        print('点击 提交')
        driver.click_Xpath(ele['repart_table_commit'])
        print('开始检查')
        res = self.get_opt_history_result(case)
        if res == 1:
            res = load_data.diff_tabls(source_node_info=comp_infos[-1], target_node_info=comp_infos[0])
        return [case, res]
