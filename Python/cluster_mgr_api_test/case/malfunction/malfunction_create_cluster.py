from case.malfunction.general import *
import threading
from time import sleep
from base.api.post import *
from base.other.info import *
from base.other.sys_opt import *
from base.other.write_log import *
from base.other.getconf import *

class case_test:
    def __init__(self):
        self.mgr_setting = getconf.get_conf_info().cluster_mgr()
        self.comp_list, self.stor_list = info.node_info().show_all_running_sever_nodes()

    def reinstall_clsuter(self):
        res1 = cluster_setting(0).delete_cluster_all()
        res2 = test_step().Create_cluster(1, 3, 1, 1, [], 0)
        if res2 != 0 and res1 != 0:
            return 1
        else:
            return 0

    def show_shard_id(self, cluster_id):
        sql = "select shard_id from shard_nodes where db_cluster_id = %s and member_state = 'source';" % cluster_id
        res = node_info().get_res(sql)[0][0]
        return res

    def back_times(self):
        now_hour = int(time.strftime('%H'))
        new_hour = now_hour + 1
        minutes_second = time.strftime(':%M:%S')
        if now_hour < 10:
            now_hour = '0{}'.format(now_hour)
        if new_hour < 10:
            new_hour = '0{}'.format(new_hour)
        now_time = '{}{}'.format(now_hour, minutes_second)
        new_time = '{}{}'.format(new_hour, minutes_second)
        backup_time = '{}=>{}'.format(now_time, new_time)
        return backup_time

    def len_case(self, case_name):
        en_part = case_name.split(': ')[0]
        zh_part = case_name.split(': ')[1]
        tlen = 2
        tlen += len(en_part)
        for i in zh_part:
            if i.isascii():
                tlen += 1
            else:
                tlen += 2
        empty_part = 50 - tlen
        res = '%s%s' % (case_name, empty_part * ' ')
        print(tlen)
        return res

    def case1_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case1: 创建集群时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = cluster_setting(0).delete_cluster_all()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            def thread1():
                global case_status
                res = test_step().Create_cluster(1, 3, 1, 1, [], 300)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '
            def thread2():
                test_step().restart_meta_master()
            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res_num = test_step().review_metadata_compupter()
            if res_num == 1:
                case_status += '| 成功 |'
            elif res_num == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            tmp_res = 0
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case2_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case2: 创建集群时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = cluster_setting(0).delete_cluster_all()
            if res_num == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            def thread1():
                global case_status
                res = test_step().Create_cluster(1, 3, 1, 1, [], 300)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '
            def thread2():
                test_step().set_meta_master_only()
            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case3_malfunction(self, file_name):
        tmp_res = 0
        # cluster_id, comps_num, comps_iplist
        case_name = 'case3: add_comps时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            cluster_id = random.choices(cluster_ids)[0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_comps(cluster_id, 1)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '
            def thread2():
                test_step().restart_meta_master()
            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]


    def case4_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case4: add_comps时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            cluster_id = random.choices(cluster_ids)[0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_comps(cluster_id, 1)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case5_malfunction(self, file_name):
        tmp_res = 0
        # cluster_id, comp_id
        case_name = 'case5: del_comps时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            res = cluster_setting(0).add_comps(cluster_id, 1)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            comp_ids = node_info().show_all_running_computer_with_id()
            comp_id = random.choices(comp_ids)[-1][0]

            def thread1():
                global case_status
                res = cluster_setting(300).del_comps(cluster_id, comp_id)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case6_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case6: del_comps时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            res = cluster_setting(0).add_comps(cluster_id, 1)
            if res == 0:
                res_num += 1
            comp_ids = node_info().show_all_running_computer_with_id()
            comp_id = random.choices(comp_ids)[-1][0]

            def thread1():
                global case_status
                res = cluster_setting(300).del_comps(cluster_id, comp_id)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case7_malfunction(self, file_name):
        tmp_res = 0
        # add_shards(self, cluster_id, shards, nodes):
        case_name = 'case7: add_shard时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_shards(cluster_id, 1, 2)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case8_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case8: add_shard时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_shards(cluster_id, 1, 2)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case9_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case9: del_shard时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            res = cluster_setting(0).add_shards(cluster_id, 1, 2)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            new_shard_id = node_info().show_all_running_shard_id()[-1][0]

            def thread1():
                global case_status
                res = cluster_setting(300).del_shard(cluster_id, new_shard_id)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case10_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case10: "del_shard时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            res = cluster_setting(0).add_shards(cluster_id, 1, 2)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            new_shard_id = node_info().show_all_running_shard_id()[-1][0]

            def thread1():
                global case_status
                res = cluster_setting(300).del_shard(cluster_id, new_shard_id)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case11_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case11: 回档时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case11'
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            res = test_step().Create_cluster(1, 3, 1, 1, [], 0)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            dst_cluster_id = cluster_ids[-1]
            restore_time = time.strftime('%Y-%m-%s %H:%M:%S')

            def thread1():
                global case_status
                res = cluster_setting(300).cluster_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                           restore_time=restore_time)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case12_malfunction(self, file_name):
        tmp_res = 0
        # add_nodes(cluster_id, shard_id, nodes_num):
        case_name = 'case12: add_node时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            shard_id = node_info().show_all_running_shard_id()[0][0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_nodes(cluster_id, shard_id, 1)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case13_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case13: add_node时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            shard_id = node_info().show_all_running_shard_id()[0][0]

            def thread1():
                global case_status
                res = cluster_setting(300).add_nodes(cluster_id, shard_id, 1)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case14_malfunction(self, file_name):
        tmp_res = 0
        # del_nodes(self, cluster_id, shard_id, stor_node_host, stor_node_port):
        case_name = 'case14: del_node时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            shard_id = node_info().show_all_running_shard_id()[0][0]
            res = cluster_setting(0).add_nodes(cluster_id, shard_id, 1)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            new_node_info = node_info().show_all_storage_with_id(shard_id)[-1]
            new_node_host, new_node_port = new_node_info[1], new_node_info[2]

            def thread1():
                global case_status
                res = cluster_setting(300).del_nodes(cluster_id, shard_id, new_node_host, new_node_port)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case15_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case15: del_node时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            lt = []
            cluster_id = node_info().show_all_running_cluster_id()[0][0]
            shard_id = node_info().show_all_running_shard_id()[0][0]
            res = cluster_setting(0).add_nodes(cluster_id, shard_id, 1)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            new_node_info = node_info().show_all_storage_with_id(shard_id)[-1]
            new_node_host, new_node_port = new_node_info[1], new_node_info[2]

            def thread1():
                global case_status
                res = cluster_setting(300).del_nodes(cluster_id, shard_id, new_node_host, new_node_port)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case16_malfunction(self, file_name):
        tmp_res = 0
        # repartition_tables(self, src_cluster_id, dst_cluster_id, repartition_tables)
        # "repartition_tables": "test_$$_public.t=>test1_$$_private.t2,test_$$_priv.ta=>test1_$$_priv1.tb"
        case_name = 'case16: table_repatition时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case16'
        dst_tbname = 'case16_dst'
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            res = test_step().Create_cluster(1, 2, 1, 1, [], 0)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            src_shard_id = self.show_shard_id(src_cluster_id)
            dst_cluster_id = cluster_ids[-1]
            dst_shard_id = self.show_shard_id(dst_cluster_id)
            repartition_tables = '%s_$$_public.%s=>%s_$$_public.%s' % (db, src_tbname, db, dst_tbname)

            def thread1():
                global case_status
                res = cluster_setting(300).repartition_tables(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                              repartition_tables=repartition_tables)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(dst_cluster_id, dst_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case17_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case17: table_repatition时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case17'
        dst_tbname = 'case17_dst'
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            res = test_step().Create_cluster(1, 2, 1, 1, [], 0)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            src_shard_id = self.show_shard_id(src_cluster_id)
            dst_cluster_id = cluster_ids[-1]
            dst_shard_id = self.show_shard_id(dst_cluster_id)
            repartition_tables = '%s_$$_public.%s=>%s_$$_public.%s' % (db, src_tbname, db, dst_tbname)

            def thread1():
                global case_status
                res = cluster_setting(300).repartition_tables(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                              repartition_tables=repartition_tables)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(dst_cluster_id, dst_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case18_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case18: 逻辑备份时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case18'
        dst_tbname = 'case18_dst'
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-1]
            src_shard_id = self.show_shard_id(src_cluster_id)

            def thread1():
                global case_status
                backup_info = []
                db_table = '{}_$$_public.'.format(db)
                backup_time = self.back_times()
                src_backup_info = {"db_table": '{}{}'.format(db_table, src_tbname), "backup_time": backup_time}
                dst_backup_info = {"db_table": '{}{}'.format(db_table, dst_tbname), "backup_time": backup_time}
                backup_info.append(src_backup_info)
                backup_info.append(dst_backup_info)
                res = cluster_setting(300).logical_backup(src_cluster_id, 'table', backup_info)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case19_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case19: 逻辑备份时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case19'
        dst_tbname = 'case19_dst'
        try:
            res = self.reinstall_clsuter()
            if res == 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-1]
            src_shard_id = self.show_shard_id(src_cluster_id)

            def thread1():
                global case_status
                backup_info = []
                db_table = '{}_$$_public.'.format(db)
                backup_time = self.back_times()
                src_backup_info = {"db_table": '{}{}'.format(db_table, src_tbname), "backup_time": backup_time}
                dst_backup_info = {"db_table": '{}{}'.format(db_table, dst_tbname), "backup_time": backup_time}
                backup_info.append(src_backup_info)
                backup_info.append(dst_backup_info)
                res = cluster_setting(300).logical_backup(src_cluster_id, 'table', backup_info)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case20_malfunction(self, file_name):
        tmp_res = 0
        # logical_restore(self, src_cluster_id, dst_cluster_id, restore_type, restore_info):
        case_name = 'case20: 逻辑回档时，只重启元数据集群的主'
        db = 'postgres'
        src_tbname = 'case20'
        dst_tbname = 'case20_dst'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            restore_time = time.strftime('%Y-%m-%s %H:%M:%S')
            res = test_step().Create_cluster(1, 3, 1, 1, [], 0)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt, restore_info = [], []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            src_shard_id = self.show_shard_id(src_cluster_id)
            dst_cluster_id = cluster_ids[-1]
            dst_shard_id = self.show_shard_id(dst_cluster_id)
            src_restore_info = {"db_table": '%s_$$_public.%s' % (db, src_tbname), "restore_time": restore_time}
            dst_restore_info = {"db_table": '%s_$$_public.%s' % (db, dst_tbname), "restore_time": restore_time}
            restore_info.append(src_restore_info)
            restore_info.append(dst_restore_info)

            def thread1():
                global case_status
                res = cluster_setting(300).logical_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                           restore_type='table', restore_info=restore_info)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(dst_cluster_id, dst_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]



    def case21_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case21: 逻辑回档时，元数据集群的主设置只读'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        db = 'postgres'
        src_tbname = 'case21'
        dst_tbname = 'case21_dst'
        try:
            self.reinstall_clsuter()
            src_pg_info = node_info().show_all_running_computer()[-1]
            create_insert_table(pg_connect_info=src_pg_info, db=db, table_name=src_tbname)
            restore_time = time.strftime('%Y-%m-%s %H:%M:%S')
            test_step().Create_cluster(1, 3, 1, 1, [], 0)
            lt, restore_info = [], []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            src_shard_id = self.show_shard_id(src_cluster_id)
            dst_cluster_id = cluster_ids[-1]
            dst_shard_id = self.show_shard_id(dst_cluster_id)
            src_restore_info = {"db_table": '%s_$$_public.%s' % (db, src_tbname), "restore_time": restore_time}
            dst_restore_info = {"db_table": '%s_$$_public.%s' % (db, dst_tbname), "restore_time": restore_time}
            restore_info.append(src_restore_info)
            restore_info.append(dst_restore_info)

            def thread1():
                global case_status
                res = cluster_setting(300).logical_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                           restore_type='table', restore_info=restore_info)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().set_meta_master_only()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
            src_tb_content = node_info().show_signal_master_storage_table(src_cluster_id, src_shard_id, db, src_tbname)
            dst_tb_content = node_info().show_signal_master_storage_table(dst_cluster_id, dst_shard_id, db, dst_tbname)
            if src_tb_content == dst_tb_content:
                print('同步成功')
            else:
                print('同步失败')
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]

    def case22_malfunction(self, file_name):
        tmp_res = 0
        case_name = 'case22: create_rcr时，只重启元数据集群的主'
        print(case_name)
        global case_status
        case_status = '| %s ' % self.len_case(case_name)
        try:
            res_num = 0
            res = self.reinstall_clsuter()
            if res == 0:
                res_num += 1
            res = test_step().Create_cluster(1, 3, 1, 1, [], 0)
            if res == 0:
                res_num += 1
            if res_num != 0:
                case_status += '| 失败 '
                tmp_res = 1
            else:
                case_status += '| 成功 '
            lt = []
            cluster_ids = node_info().show_all_running_cluster_id()
            src_cluster_id = cluster_ids[-2]
            dst_cluster_id = cluster_ids[-1]

            def thread1():
                global case_status
                res = cluster_setting(300).create_rcr(src_cluster_id, dst_cluster_id)
                if res == 0:
                    case_status += '| 失败 '
                    tmp_res = 1
                else:
                    case_status += '| 成功 '

            def thread2():
                test_step().restart_meta_master()

            t1 = threading.Thread(target=thread1)
            t2 = threading.Thread(target=thread2)
            t1.start()
            sleep(2)
            t2.start()
            lt.append(t1)
            lt.append(t2)
            for i in lt:
                i.join()
            res = test_step().review_metadata_compupter()
            if res == 1:
                case_status += '| 成功 |'
            elif res == 2:
                case_status += '| 不存在 |'
                tmp_res = 1
        except Exception as err:
            print(err)
            sleep(300)
            case_status += '| %s |' % err
        write_log.w2File().toOther(file_name=file_name, txt=case_status)
        return [case_name, tmp_res]
