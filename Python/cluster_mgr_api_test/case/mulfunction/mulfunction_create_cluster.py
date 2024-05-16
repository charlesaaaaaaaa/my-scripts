from case.mulfunction.general import *
import threading
from time import sleep
from base.api.post import *
from base.other.info import *
from base.other.write_log import *
from base.other.getconf import *

class case_test:
    def __init__(self):
        self.mgr_setting = getconf.get_conf_info().cluster_mgr()
        self.comp_list, self.stor_list = info.node_info().show_all_running_sever_nodes()

    def reinstall_clsuter(self):
        cluster_setting().delete_cluster_all()
        test_step().Create_cluster(1, 3, 1, 1, [])

    def case1_mulfunction(self, file_name):
        case_name = 'case1: 创建集群时，只重启元数据集群的主'
        print(case_name)
        cluster_setting().delete_cluster_all()
        lt = []
        def thread1():
            res = test_step().Create_cluster(1, 3, 1, 1, [])
            if res == 0:
                write_log.w2File().toOther(file_name, case_name)
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

    def case2_mulfunction(self, file_name):
        case_name = 'case2: 创建集群时，元数据集群的主设置只读'
        print(case_name)
        cluster_setting().delete_cluster_all()
        lt = []
        def thread1():
            res = test_step().Create_cluster(1, 3, 1, 1, [])
            if res == 0:
                write_log.w2File().toOther(file_name, case_name)
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

    def case3_mulfunction(self, file_name):
        # cluster_id, comps_num, comps_iplist
        case_name = 'case3: add_comps时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_ids = node_info().show_all_running_cluster_id()
        cluster_id = random.choices(cluster_ids)[0]

        def thread1():
            res = cluster_setting().add_comps(cluster_id, 1)

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

    def case4_mulfunction(self, file_name):
        case_name = 'case4: add_comps时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_ids = node_info().show_all_running_cluster_id()
        cluster_id = random.choices(cluster_ids)[0]

        def thread1():
            res = cluster_setting().add_comps(cluster_id, 1)

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

    def case5_mulfunction(self, file_name):
        # cluster_id, comp_id
        case_name = 'case5: del_comps时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        cluster_setting().add_comps(cluster_id, 1)
        comp_ids = node_info().show_all_running_computer()
        comp_id = random.choices(comp_ids)[0]

        def thread1():
            cluster_setting().del_comps(cluster_id, comp_id)

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

    def case6_mulfunction(self, file_name):
        case_name = 'case6: del_comps时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        cluster_setting().add_comps(cluster_id, 1)
        comp_ids = node_info().show_all_running_computer()
        comp_id = random.choices(comp_ids)[0]

        def thread1():
            cluster_setting().del_comps(cluster_id, comp_id)

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

    def case7_mulfunction(self, file_name):
        # add_shards(self, cluster_id, shards, nodes):
        case_name = 'case7: add_shard时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]

        def thread1():
            res = cluster_setting().add_shards(cluster_id, 1, 2)

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

    def case8_mulfunction(self, file_name):
        case_name = 'case8: add_shard时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]

        def thread1():
            res = cluster_setting().add_shards(cluster_id, 1, 2)

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

    def case9_mulfunction(self, file_name):
        case_name = 'case9: del_shard时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        cluster_setting().add_shards(cluster_id, 1, 2)
        new_shard_id = node_info().show_all_running_shard_id()[-1][0]

        def thread1():
            res = cluster_setting().del_shard(cluster_id, new_shard_id)

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

    def case10_mulfunction(self, file_name):
        case_name = 'case10: "del_shard时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        cluster_setting().add_shards(cluster_id, 1, 2)
        new_shard_id = node_info().show_all_running_shard_id()[-1][0]

        def thread1():
            res = cluster_setting().del_shard(cluster_id, new_shard_id)

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

    def case11_mulfunction(self, file_name):
        case_name = 'case11: 回档时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case12_mulfunction(self, file_name):
        # add_nodes(cluster_id, shard_id, nodes_num):
        case_name = 'case12: add_node时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        shard_id = node_info().show_all_running_shard_id()[0][0]

        def thread1():
            res = cluster_setting().add_nodes(cluster_id, shard_id, 1)

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

    def case13_mulfunction(self, file_name):
        case_name = 'case13: add_node时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        shard_id = node_info().show_all_running_shard_id()[0][0]

        def thread1():
            res = cluster_setting().add_nodes(cluster_id, shard_id, 1)

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

    def case14_mulfunction(self, file_name):
        # del_nodes(self, cluster_id, shard_id, stor_node_host, stor_node_port):
        case_name = 'case14: del_node时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        shard_id = node_info().show_all_running_shard_id()[0][0]
        cluster_setting().add_nodes(cluster_id, shard_id, 1)
        new_node_info = node_info().show_all_storage_with_id(shard_id)[-1]
        new_node_host, new_node_port = new_node_info[1], new_node_info[2]

        def thread1():
            res = cluster_setting().del_nodes(cluster_id, shard_id, new_node_host, new_node_port)

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

    def case15_mulfunction(self, file_name):
        case_name = 'case15: del_node时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []
        cluster_id = node_info().show_all_running_cluster_id()[0][0]
        shard_id = node_info().show_all_running_shard_id()[0][0]
        cluster_setting().add_nodes(cluster_id, shard_id, 1)
        new_node_info = node_info().show_all_storage_with_id(shard_id)[-1]
        new_node_host, new_node_port = new_node_info[1], new_node_info[2]

        def thread1():
            res = cluster_setting().del_nodes(cluster_id, shard_id, new_node_host, new_node_port)

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

    def case16_mulfunction(self, file_name):
        # repartition_tables(self, src_cluster_id, dst_cluster_id, repartition_tables)
        # "repartition_tables": "test_$$_public.t=>test1_$$_private.t2,test_$$_priv.ta=>test1_$$_priv1.tb"
        case_name = 'case16: table_repatition时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case17_mulfunction(self, file_name):
        case_name = 'case17: table_repatition时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case18_mulfunction(self, file_name):
        case_name = 'case18: 逻辑备份时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case19_mulfunction(self, file_name):
        case_name = 'case19: 逻辑备份时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case20_mulfunction(self, file_name):
        case_name = 'case20: 逻辑回档时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case21_mulfunction(self, file_name):
        case_name = 'case21: 逻辑回档时，元数据集群的主设置只读'
        print(case_name)
        self.reinstall_clsuter()
        lt = []

        def thread1():
            pass

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

    def case22_mulfunction(self, file_name):
        case_name = 'case22: create_rcr时，只重启元数据集群的主'
        print(case_name)
        self.reinstall_clsuter()
        test_step().Create_cluster(1, 3, 1, 1, [])
        lt = []
        cluster_ids = node_info().show_all_running_cluster_id()
        src_cluster_id = cluster_ids[-2]
        dst_cluster_id = cluster_ids[-1]

        def thread1():
            res = cluster_setting().create_rcr(src_cluster_id, dst_cluster_id)

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