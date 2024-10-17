import random
from bin.other_opt import *
from xpanel_case.load import *

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
        print(opt_name, opt_res)
        return opt_name, opt_res

    def get_opt_history_result(self, opt_name):
        # 循环调用上面的 the_first_opt_status 函数
        # 直接结果为非 ongoing, 要给一个opt_name, 就是操作的名称，如主备切换，重做备机节点等
        # 返回 非ongoing状态 或者 0，当为0时代表当前第一个操作记录名不是指定的操作名
        history_opt_name, opt_res = self.the_first_opt_status()
        if history_opt_name == opt_name:
            while opt_res == 'ongoing':
                opt_name, opt_res = self.the_first_opt_status()
                sleep(2)
            return opt_res
        else:
            print('第一个操作记录非 主备切换')
            return 0

    def delete_all_cluster(self):
        driver = self.driver
        ele = self.elements
        case = '删除集群'
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
                review_status(ele['cluster_delete_info'], '删除完成100%', ele['cluster_delete_second_info'], '删除shard失败')
                res = 1
                driver.click_Xpath(ele['cluster_delete_info_close'])
                delete_times += 1
        except:
            if res == 1:
                if delete_times >= 1:
                    print('delete all clusters done')
                else:
                    print('Currently, not exists any cluster, skip')
                return [case, 1]
            elif res == 0:
                return [case, 0]

    @timer
    def add_new_cluster(self):
        resList = []
        result = 1
        caseName = "创建集群"
        print('=== 现在测试用例为 %s ===' % caseName)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        cluster_name = conf['cluster_name']
        db_shard_num = conf['shard_num']
        db_shard_node_num = conf['shard_node_num']
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
                review_status(ele['cluster_delete_info'], '删除完成100%', ele['cluster_delete_second_info'], '删除shard失败')
                driver.click_Xpath(ele['cluster_delete_info_close'])
                delete_times += 1
        except:
            if delete_times >= 1:
                print('delete all clusters done')
            else:
                print('Currently, not exists any cluster, skip')
        driver.click_Xpath(ele['cluster_list_add_cluster_button'])
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_business_name'], cluster_name)
        driver.click_Xpath(ele['cluster_list_add_cluster_next_1'])
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
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shard_num'], db_shard_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shardnode_num'], db_shard_node_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_pg_totalnum'], pg_select_node)
        driver.click_Xpath(ele['cluster_list_add_cluster_next_3'])
        driver.click_Xpath(ele['cluster_list_add_cluster_commit_button'])
        sleep(10)
        #检查集群是否完成
        #resList.append(review_status(ele['install_db_info'], '新增shard成功', '新增shard失败'))
        #resList.append(review_status(ele['install_pg_info'], '新增computer成功', '新增computer失败'))
        resList.append(review_status(ele['install_cluster_info'], '安装完成100%', ele['install_cluster_second_info'], '新增集群失败'))
        for i in resList:
            if i == 0:
                result = 0
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

    def add_repartition(self):
        case = '添加存储节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            conf = getconf().getXpanelInfo()
            db_list = str(conf['stor_list']).replace(' ', '').split(',')
            # 进入集群列表设置界面
            driver.click_Xpath(ele['cluster_list_setting_button'])
            sleep(2)
            # 点击shard列表
            driver.click_Xpath(ele['cluster_shard_list'])
            sleep(2)
            # 点击 增加存储节点
            driver.click_Xpath(ele['add_storage_node_button'])
            # 点击 选择计算机
            driver.click_Xpath(ele['choice_server'])
            # 这是就是遍历这个计算机host列表
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
            # 点击 选择计算机，主要是用来收回下拉框的
            driver.click_Xpath(ele['choice_server'])
            # 点击 shard名称选项
            driver.click_Xpath(ele['select_shard_name'])
            # 点击 第一个shard选择
            driver.click_Xpath(ele['shard_name_1'])
            # 存储节点数量改为1
            driver.clearAndSend_Xpath(ele['shard_num_input'], 1)
            # 点击 确认
            driver.click_Xpath(ele['add_shard_commit'])
            sleep(2)
            # 检查xpanel结果
            txt = driver.gettxt_Xpanth(ele['add_replica_res_txt'])
            txt_bak = txt
            print(txt_bak)
            while '正在添加存储节点' in txt:
                # 当两个文件不一样的时候把新文本给到备文本，然后打印备文本，一样就不打印了
                if txt != txt_bak:
                    txt_bak = txt
                    print(txt_bak)
                sleep(1)
                txt = driver.gettxt_Xpanth(ele['add_replica_res_txt'])
            print(txt)
            if txt == '添加存储节点成功':
                res = 1
            else:
                res = 0
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def add_comp(self):
        case = '添加计算节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            conf = getconf().getXpanelInfo()
            comp_list = str(conf['comp_list']).replace(' ', '').split(',')
            # 点进集群设置
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            # 点击 左边的 计算节点列表
            driver.click_Xpath(ele['computer_node_list'])
            # 点击 添加计算节点
            driver.click_Xpath(ele['add_computer_button'])
            # 点击 选择计算机 下拉框
            driver.click_Xpath(ele['choice_computer_server'])
            # 选择 计算机host
            num = 1
            while True:
                eles = ele['computer_server_list_range'] + 'li[%s]/span' % num
                txt = driver.gettxt_Xpanth(eles)
                if txt in comp_list:
                    driver.click_Xpath(eles)
                    break
                num += 1
            # 点击 选择计算机 下拉框, 把下拉框收起来
            driver.click_Xpath(ele['choice_computer_server'])
            # 清空并发送数字1到计算节点个数文本框里面
            driver.clearAndSend_Xpath(ele['computer_node_count'], 1)
            # 点击 确定
            driver.click_Xpath(ele['add_computer_submit'])
            # 检查结果
            txt = driver.gettxt_Xpanth(ele['add_computer_res_txt'])
            txt_bak = ''
            while '正在添加计算节点' in txt:
                sleep(1)
                if txt != txt_bak:
                    txt_bak = txt
                    print(txt_bak)
                txt = driver.gettxt_Xpanth(ele['add_computer_res_txt'])
            print(txt)
            if txt == '添加计算节点成功':
                res = 1
            else:
                res = 0
            # 点击 弹窗的 x 关掉弹窗
            driver.click_Xpath(ele['add_computer_close_res'])
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def del_comp(self):
        case = '删除计算节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            conf = getconf().getXpanelInfo()
            # 点击 集群列表 -- 设置 -- 计算节点列表
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['computer_node_list'])
            # 开始计算有几个计算节点
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
            # 点击 最上面的那行计算节点的删除键
            driver.click_Xpath(ele['delete_top1_computer'])
            # 获取 确认码
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
            # 把 确认码 输入到文本框里
            eles = '/html/body/div[%s]' % num + ele['delete_computer_code_input_tail']
            driver.clearAndSend_Xpath(eles, txt)
            # 点击 确认
            eles = '/html/body/div[%s]' % num + ele['delete_computer_commit_tail']
            print(eles)
            driver.click_Xpath(eles)
            # 检查结果
            sleep(30)
            txt = driver.gettxt_Xpanth(ele['delete_computer_res_txt'])
            txt_bak = ''
            while '正在删除计算节点' in txt:
                if txt != txt_bak:
                    txt_bak = txt
                    print(txt_bak)
            print(txt)
            if txt == '删除计算节点成功':
                res = 1
            else:
                res = 0
            # 点击 x 关掉弹窗
            driver.click_Xpath(ele['delete_computer_close_button'])
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def del_replica(self):
        case = '删除存储节点'
        print('=== 现在测试用例为 %s ===' % case)
        try:
            driver = self.driver
            ele = self.elements
            # 点击 集群列表 -- 设置 -- 存储节点列表
            driver.click_Xpath(ele['cluster_list'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['cluster_list_shard_list'])
            driver.click_Xpath(ele['delele_storage_button'])
            txt = driver.gettxt_Xpanth(ele['delete_storage_tips'])
            txt = txt.split('=')[1]
            driver.clearAndSend_Xpath(ele['delete_storage_code_input'], txt)
            driver.click_Xpath(ele['delete_storage_commit'])
            sleep(1)
            txt = driver.gettxt_Xpanth(ele['delete_storage_res_txt'])
            txt_bak = ''
            while '正在删除存储节点' in txt:
                if txt != txt_bak:
                    txt_bak = txt
                    print(txt_bak)
                txt = driver.gettxt_Xpanth(ele['delete_storage_res_txt'])
            print(txt)
            if txt == '删除存储节点成功':
                print('succ')
                res = 1
            else:
                print('fail')
                res = 0
        except Exception as err:
            print(err)
            res = 0
        return [case, res]

    def rebuild_node(self):
        case = '重做备机'
        print('=== 现在测试用例为 %s ===' % case)
        driver = self.driver
        ele = self.elements
        # 集群列表 = cluster_list， 设置 = cluster_list_setting_button, shard列表 = cluster_list_shard_list
        driver.click_Xpath(ele['cluster_list'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_list_shard_list'])
        # 鼠标放在 更多 上面以显示出重做备机的选项
        driver.moveToXpanth(ele['rebuild_node_more_button'])
        # 点击 重做备机
        driver.click_Xpath(ele['rebuild_node_button'])
        # 点击 确认
        sleep(1)
        driver.click_Xpath(ele['rebuild_node_commit'])
        sleep(20)
        # 获取结果
        txt = ''
        try:
            txt = driver.gettxt_Xpanth(ele['rebuild_node_res_txt'])
        except:
            pass
        while 'xPaTh FaIl' in txt:
            try:
                txt = driver.gettxt_Xpanth(ele['rebuild_node_res_txt'])
                sleep(3)
            except:
                pass
        print(txt)
        if txt == '重做备机节点成功':
            res = 1
        else:
            res = 0

        return [case, res]

    def manual_swich_master(self):
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
            sleep(30)
            print('点击 弹窗的 x 关闭按钮, 然后刷新页面快速返回集群列表页面')
            driver.click_Xpath(ele['manual_switch_close_alert_button'])
            print('获取 操作记录里面第一个记录的状态，只要不是done都是认为api失败了')
            opt_status = self.get_opt_history_result(case)
            if opt_status != ' done ':
                print(opt_status)
                return [case, 0]
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
        return [case, res]

