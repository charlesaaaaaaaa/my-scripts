from base.other import info
from base.other import write_log, getconf, info, connect, sys_opt
from base.api import get
import requests
import time
import json
import random

class cluster_setting():
    def __init__(self, relay_get_status_time):
        # relay_get_status_time 就是在发送完api后多少s开始get status
        self.mgr_info = info.master().cluster_mgr()
        self.mgr_conf = getconf.get_conf_info().cluster_mgr()
        self.url = 'http://%s:%s/HttpService/Emit' % (self.mgr_info[0], self.mgr_info[1])
        self.mgr_settings = getconf.get_conf_info().cluster_mgr()
        self.relay_get_status_time = relay_get_status_time

    def random_nodes(self, node_num, node_list):
        # 在 节点ip列表 里面随机选择 node_num 个数的节点
        random_node_list = []
        if node_num == 1:
            random_node_list = random.choices(node_list)[0]
        else:
            for times in range(node_num):
                random_node = random.choices(node_list)[0]
                while random_node in random_node_list:
                    random_node = random.choices(node_list)[0]
                random_node_list.append(random_node)
        return random_node_list

    def select_nodes_in_order(self, node_num, node_type='server'):
        tb = 'comp_nodes'
        conf_iplist = self.mgr_settings['comp_iplists']
        if node_type == 'storage':
            tb = "shard_nodes"
            conf_iplist = self.mgr_settings['stor_iplists']
        sql = "select hostaddr, count(hostaddr) a from %s where status" \
              " = 'active' group by hostaddr order by a;" % tb
        ip_list = conf_iplist.replace(' ', '').split(',')
        if node_num >= len(ip_list):
            node_list = ip_list
            return node_list
        try:
            res = info.node_info().get_res(sql=sql)
            if not res:
                print(res)
                res = 0
        except:
            res = 0
        node_list = []
        print(res)
        if res == 0:
            for i in range(node_num):
                node_list.append(ip_list[i])
            return node_list
        if len(res) < len(ip_list):
            for i in res:
                ip_list.remove(i[0])
            if len(ip_list) >= node_num:
                for ip in range(node_num):
                    node_list.append(ip_list[ip])
            else:
                for ip in ip_list:
                    node_list.append(ip)
                node_num -= len(ip_list)
                for ip in range(node_num):
                    node_list.append(res[ip][0])
        else:
            for i in range(node_num):
                node_list.append(res[i][0])
        return node_list

    def get_status(self, job_id):
        # 检查job status
        result = 'done'
        write_log.w2File().tolog('检查任务状态，job_id == %s' % job_id)
        times = 1
        try:
            write_log.w2File().tolog('第 %s 次检查' % times)
            time.sleep(self.relay_get_status_time)
            job_status = get.status().job_status(job_id)
            res = job_status['status']
            while res != 'done':
                times += 1
                time.sleep(5)
                write_log.w2File().tolog('第 %s 次检查' % times)
                job_status = get.status().job_status(job_id)
                res = job_status['status']
                if res == "failed":
                    err_info = job_status['error_info']
                    write_log.w2File().tolog('ERROR: 调用api失败')
                    write_log.w2File().print_log('ERROR: %s' % err_info)
                    result = res
                    break
        except Exception as err:
            write_log.w2File().tolog(err)
            print(err)
            exit(1)
        print('job_status: %s' % job_status)
        return result

    def send_api_and_return_res(self, json_data, tmp_info):
        # 发送api的
        # 失败则返回1， 成功则返回其状态
        write_log.w2File().tolog(json_data)
        print(json_data)
        res = requests.post(self.url, json_data)
        res_dict = json.loads(res.text)
        job_id = res_dict['job_id']
        write_log.w2File().tolog(res_dict)
        # print(res_dict)
        # 检查job status
        job_status = self.get_status(job_id)
        if job_status == 'done':
            write_log.w2File().print_log(tmp_info + '成功')
            job_status = get.status().job_status(job_id)
            result = [job_status['status'], job_status['attachment']]
        elif job_status == 'failed':
            write_log.w2File().print_log(tmp_info + '失败')
            result = 0
        return result

    def send_api_and_return_metares(self, json_data, sql, tmp_info, sleep_time=0):
        # 发送api的
        # 但检查结果是直接在元数据集群里面找结果的，有部分的api get_status是有问题的
        # 如果要在sql里面加上job_id，则直接在sql里面加上"$job_id"就行
        write_log.w2File().tolog(json_data)
        print(json_data)
        res = requests.post(self.url, json_data)
        res_dict = json.loads(res.text)
        write_log.w2File().tolog(res_dict)
        # print(res_dict)
        if "$job_id" in sql:
            job_id = res_dict['job_id']
            print(job_id)
            sql = sql.replace('$job_id', str(job_id))

        print(sql)
        time.sleep(sleep_time)
        sql_res = info.node_info().get_res(sql)
        print(str(sql_res))
        sql_res = sql_res[0][0]
        while sql_res == "ongoing":
            time.sleep(5)
            sql_res = info.node_info().get_res(sql)[0][0]
        print("meta_sql: %s \n\tresult: %s" % (sql, sql_res))
        if sql_res == "done":
            write_log.w2File().print_log(tmp_info + '成功')
            result = 1
        else:
            write_log.w2File().print_log(tmp_info + '失败')
            result = 0
        return result

    def create_cluster(self, shard, nodes, comps, user_name='super_dba', nick_name='test_db', max_storage_size=1024,
                       max_connections=2000, cpu_cores=8, cpu_limit_node='quota', innodb_size=1024,
                       rocksdb_block_cache_size_M=1024, fullsync_level=1, data_storage_MB=1024, log_storage_MB=1024,
                       dbcfg=0, other_paras_dict=None):
        # 这个函数就是用来发送创建集群的api
        # 当前只有rbr，所以不用设置ha_mode
        # 共要给 13 个变量
        #   除开最后一个，其它12个都是create_cluster api里面必填的参数, 这12个参数的信息去api文档看，gitee上的文档有
        #       这12个变量名和api的参数变量名是一样的，可以直接对着api文档填写
        #   最后一个(other_paras_dict)是非必填的参数, 字典类型，字典值一定得是字符串，不能是其它类型的
        #     如：other_paras_dict={"install_proxysql": "1"}
        # 如果成功，会返回一个列表
        #   第0个是状态码
        #   第1个是新增分片的信息
        result = 1
        url = self.url
        time_stamp = int(time.time())
        para = {"nick_name": nick_name, "ha_mode": "rbr", "shards": str(shard),
                "nodes": str(nodes), "comps": str(comps), "max_storage_size": str(max_storage_size),
                "max_connections": str(max_connections), "cpu_cores": str(cpu_cores),
                "cpu_limit_node": str(cpu_limit_node),"innodb_size": str(innodb_size),
                "rocksdb_block_cache_size_M": str(rocksdb_block_cache_size_M), "data_storage_MB": str(data_storage_MB),
                "log_storage_MB": str(log_storage_MB), "dbcfg": str(dbcfg), "fullsync_level": str(fullsync_level)}
        if other_paras_dict:
            para.update(other_paras_dict)
        # 这里通过函数获取可以安装计算节点和存储节点并正在运行的机器ip
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
        stor_nodes_need = int(shard) * int(nodes)
        comps = int(comps)
        comp_iplists_info = self.mgr_settings['comp_iplists']
        if comp_iplists_info != 'all':
            comp_list = comp_iplists_info.replace(' ', '').split(',')
        stor_iplists_info = self.mgr_settings['stor_iplists']
        if stor_iplists_info != 'all':
            stor_list = stor_iplists_info.replace(' ', '').split(',')
        # 这里开始判断，如果要用到的计算节点数量或者存储节点数量小于可以安装的节点
        #   则随机从可安装的节点里面选择其中几个
        #   否则直接把所有可安装的节点全选上
        if stor_nodes_need < len(stor_list):
            #storage_iplists = self.random_nodes(stor_nodes_need, stor_list)
            storage_iplists = self.select_nodes_in_order(node_num=stor_nodes_need, node_type='storage')
            #if stor_nodes_need == 1:
            #    storage_iplists = storage_iplists.split(' ')
        else:
            storage_iplists = stor_list
        if comps < len(comp_list):
            computer_iplists = self.select_nodes_in_order(node_num=comps, node_type='server')
            #computer_iplists = self.random_nodes(comps, comp_list)
            #if comps == 1:
            #    computer_iplists = computer_iplists.split(' ')
        else:
            computer_iplists = comp_list
        iplist = {"storage_iplists": storage_iplists, "computer_iplists": computer_iplists}
        para.update(iplist)
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "create_cluster",
                "timestamp": str(time_stamp),
                "user_name": user_name,
                "paras": para
            }, indent=4
        )
        write_log.w2File().tolog(json_data)
        print(json_data)
        res = requests.post(url, data=json_data)
        if res.status_code == 200:
            write_log.w2File().tolog('调用 create_cluster 成功, 等待安装完成')
            write_log.w2File().tolog(json_data)
        post_res = json.loads(res.text)
        write_log.w2File().tolog(post_res)
        print(post_res)
        job_id = int(post_res['job_id'])
        write_log.w2File().print_log('api发送完毕，开始检查任务状态')
        # 检查job status
        time.sleep(5)
        job_status = self.get_status(job_id)
        if job_status == 'done':
            write_log.w2File().print_log('创建集群成功')
            job_status = get.status().job_status(job_id)
            result = [job_status['status'], job_status['attachment']]
        elif job_status == 'failed':
            write_log.w2File().print_log('创建集群失败')
            result = 0
        return result

    def add_shards(self, cluster_id, shards, nodes):
        # 这里只要给cluster_id, shards, nodes, shard是要几个shard
        # storage_iplists 会自动生成, nodes是要一个shard几个节点， 目前最小为2
        # 如果成功，会返回一个列表
        #   第0个是状态码
        #   第1个是新增分片的信息
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
        stor_iplists_info = self.mgr_settings['stor_iplists']
        if stor_iplists_info != 'all':
            stor_list = stor_iplists_info.replace(' ', '').split(',')
        stor_nodes_need = int(shards) * int(nodes)
        # 这里开始判断，如果要用到的计算节点数量或者存储节点数量小于可以安装的节点
        #   则随机从可安装的节点里面选择其中几个
        #   否则直接把所有可安装的节点全选上
        if stor_nodes_need < len(stor_list):
            storage_iplists = self.random_nodes(stor_nodes_need, stor_list)
        else:
            storage_iplists = stor_list
        time_stamp = int(time.time())
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "add_shards",
                "timestamp": str(time_stamp),
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": str(cluster_id),
                    "shards": str(shards),
                    "nodes": str(nodes),
                    "storage_iplists":
                        storage_iplists
                }
            }, indent=4
        )
        tmp_info = 'add_shards cluster_id[%s] shards[%s] nodes[%s] ' % (cluster_id, shards, nodes)
        res = self.send_api_and_return_res(json_data, tmp_info)
        return res

    def delete_clsuter(self, cluster_id=None):
        if cluster_id == None:
            cluster_ids = info.node_info().show_all_running_cluster_id()
            try:
                cluster_id_1 = cluster_ids[0]
                print("当前存在的cluster_id有: %s" % str(cluster_ids))
            except Exception as err:
                print('当前无正在运行的cluster')
                exit(0)
            exit(0)
        time_stamp = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "delete_cluster",
            "timestamp": "%s" % time_stamp,
            "user_name": "kunlun_test",
            "paras": {
                "cluster_id": "%s" % cluster_id
                }
            }, indent=4
        )
        tmp_info = 'delete_cluster cluster_id = %s ' % cluster_id
        res = self.send_api_and_return_res(json_data, tmp_info)
        if res == 0:
            return res
        return 1

    def delete_cluster_all(self):
        # 会删除当前所有正在运行的集群
        # 没有的话会跳过这个函数
        cluster_ids = info.node_info().show_all_running_cluster_id()
        if not cluster_ids:
            write_log.w2File().print_log('当前无正在运行的群集，跳过')
            return 1
        for cluster_id in cluster_ids:
            time_stamp = int(time.time())
            json_data = json.dumps({
                    "version": "1.0",
                    "job_id": "",
                    "job_type": "delete_cluster",
                    "timestamp": "%s" % time_stamp,
                    "user_name": "kunlun_test",
                    "paras": {
                        "cluster_id": "%s" % cluster_id[0]
                    }
                }, indent=4
            )
            tmp_info = 'delete_cluster cluster_id = %s ' % cluster_id
            res = self.send_api_and_return_res(json_data, tmp_info)
            if res == 0:
                return res
        return 1

    def add_comps(self, cluster_id, comps_num):
        # 新增计算节点
        # 在id为几的cluster上新增，要增加几个计算节点，要增加的计算节点的ip列表
        # 这里只要给cluster_id, comps_num(要增加的计算节点个数)
        # storage_iplists 会自动生成
        # 如果成功，会返回一个列表
        #   第0个是状态码
        #   第1个是新增分片的信息
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
        comp_iplists_info = self.mgr_settings['stor_iplists']
        if comp_iplists_info != 'all':
            comps_iplist = comp_iplists_info.replace(' ', '').split(',')
        # 这里开始判断，如果要用到的计算节点数量或者存储节点数量小于可以安装的节点
        #   则随机从可安装的节点里面选择其中几个
        #   否则直接把所有可安装的节点全选上
        if int(comps_num) < len(comp_list):
            comps_iplist = self.random_nodes(comps_num, comp_list)
        else:
            comps_iplist = comp_list
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "add_comps",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "comps": "%s" % comps_num,
                    "computer_iplists":
                        comps_iplist
                }
            }, indent=4
        )
        tmp_info = 'add_comps '
        res = self.send_api_and_return_res(json_data, tmp_info)
        return res

    def del_comps(self, cluster_id, comp_id):
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "delete_comp",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "comp_id": "%s" % comp_id
                }
            }, indent=4
        )
        tmp_info = 'del_comps cluster_id = [%s] and comp_id = [%s]' % (cluster_id, comp_id)
        res = self.send_api_and_return_res(json_data, tmp_info)
        return res

    def del_shard(self, cluster_id, shard_id):
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "delete_shard",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "shard_id": "%s" % shard_id
                }
            }, indent=4
        )
        tmp_info = 'del_comps cluster_id = [%s] and sahrd_id = [%s]' % (cluster_id, shard_id)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def add_nodes(self, cluster_id, shard_id, nodes_num):
        # 增加存储节点
        # 这里只要给cluster_id, shards, nodes, shard是要几个shard
        # storage_iplists 会自动生成, nodes是要一个shard几个节点， 目前最小为2
        # 如果成功，会返回一个列表
        #   第0个是状态码
        #   第1个是新增分片的信息
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
        stor_iplists_info = self.mgr_settings['stor_iplists']
        if stor_iplists_info != 'all':
            stor_list = stor_iplists_info.replace(' ', '').split(',')
        stor_nodes_need = int(nodes_num)
        # 这里开始判断，如果要用到的计算节点数量或者存储节点数量小于可以安装的节点
        #   则随机从可安装的节点里面选择其中几个
        #   否则直接把所有可安装的节点全选上
        if stor_nodes_need < len(stor_list):
            stor_iplists = self.random_nodes(stor_nodes_need, stor_list)
        else:
            stor_iplists = stor_list
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "add_nodes",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "shard_id": "%s" % shard_id,
                    "nodes": "%s" % nodes_num,
                    "storage_iplists":
                        stor_iplists
                }
            }, indent=4
        )
        tmp_info = 'add_nodes '
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def del_nodes(self, cluster_id, shard_id, stor_node_host, stor_node_port):
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "delete_node",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "shard_id": "%s" % shard_id,
                    "hostaddr": "%s" % stor_node_host,
                    "port": "%s" % stor_node_port
                }
            }, indent=4
        )
        tmp_info = 'del_nodes storage node [%s: %s] ' % (stor_node_host, stor_node_port)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def repartition_tables(self, src_cluster_id, dst_cluster_id, repartition_tables):
        # 表重分布
        # "repartition_tables":"test_$$_public.t=>test1_$$_private.t2,test_$$_priv.ta=>test1_$$_priv1.tb"
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "table_repartition",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "src_cluster_id": "%s" % src_cluster_id,
                    "dst_cluster_id": "%s" % dst_cluster_id,
                    "repartition_tables": "%s" % repartition_tables
                }
            }, indent=4
        )
        tmp_info = 'repartition_tables src_cluster_id [%s] - dst_cluster_id [%s] ' % (src_cluster_id, dst_cluster_id)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def logical_backup(self, cluster_id, backup_type, backup_info):
        # 表逻辑备份
        # backup_type = db|schema|table
        # backup_info: 一个列表，列表里面有两个二级字典，第0个字典是源，第1个字典是目标项。每个字典要包含db_table和备份时间
        #       [
        #           {
        #             "db_table":"postgres_$$_public",
        #             "backup_time":"01:00:00-02:00:00"
        #           },
        #           {
        #             "db_table":"postgres_$$_test",
        #             "backup_time":"01:00:00-02:00:00"
        #           }
        #     	]
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "logical_backup",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "backup_type": "%s" % backup_type,
                    "backup":
                        backup_info
                }
            }, indent=4
        )
        tmp_info = 'logical_backup cluster_id[%s] backup_type[%s] ' % (cluster_id, backup_type)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def cluster_restore(self, src_cluster_id, dst_cluster_id, restore_time):
        # 集群回档（按时间点恢复集群）
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "cluster_restore",
                "timestamp": str(time_stamp),
                "paras": {
                    "src_cluster_id": "%s" % src_cluster_id,
                    "dst_cluster_id": "%s" % dst_cluster_id,
                    "restore_time": "%s" % restore_time
                }
            }, indent=4
        )
        tmp_info = 'cluster_restore src_cluster_id [%s] dst_cluster_id [%s] restore_time [%s] ' \
                   % (src_cluster_id, dst_cluster_id, restore_time)
        # 去元数据集群上查结果
        # sql = 'select status from restore_log  where general_log_id = $job_id order by id desc limit 1;'
        # res = self.send_api_and_return_metares(json_data=json_data, sql=sql, tmp_info=tmp_info, sleep_time=30)
        # 使用 get_status 查结果
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def logical_restore(self, src_cluster_id, dst_cluster_id, restore_type, restore_info):
        # 表逻辑恢复（回档）
        # restore_type = db|schema|table
        # "restore":[{
        # 		"db_table":"postgres_$$_public.t1",
        # 		"restore_time":"2022-10-20 19:20:15"
        # 	},{
        # 		"db_table":"postgres_$$_public.t2",
        # 		"restore_time":"2022-10-20 19:20:15"
        # 	}]
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "logical_restore",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "src_cluster_id": "%s" % src_cluster_id,
                    "dst_cluster_id": "%s" % dst_cluster_id,
                    "restore_type": "%s" % restore_type,
                    "restore":
                        restore_info
                }
            }, indent=4
        )
        tmp_info = 'logical_restore src_cluster_id [%s] dst_cluster_id [%s] restore_type [%s] ' \
                   % (src_cluster_id, dst_cluster_id, restore_type)
        # 去元数据集群上查结果
        # sql = 'select status from restore_log  where general_log_id = $job_id order by id desc limit 1;'
        # res = self.send_api_and_return_metares(json_data=json_data, sql=sql, tmp_info=tmp_info, sleep_time=30)

        # 直接用get_status查
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def create_rcr(self, src_cluster_id, dst_cluster_id, meta_info=None):
        # 建立rcr数据同步, 用户发起对两个cluster建立rcr数据同步
        # "meta_db": "127.0.0.1:57001,127.0.0.2:57002"
        if not meta_info:
            meta_info = info.node_info().show_all_meta_ip_port_by_clustermgr_format()
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "create_rcr",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                   "master_info": {
                        "meta_db": "%s" % meta_info,
                        "cluster_id": "%s" % src_cluster_id
                    },
                   "cluster_id": "%s" % dst_cluster_id,
                   "skip_sync_roles": "jenkins,agent,kunlun"
                }
            }, indent=4
        )
        tmp_info = 'create_rcr meta_db=[%s] src_cluster_id=[%s] dst_cluster_id=[%s] ' % (meta_info, src_cluster_id,
                                                                                             dst_cluster_id)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def create_rcr_with_thelatest_clusters(self):
        the_latest_cluster_id_sql = 'select id from db_clusters where status = "inuse" order by id desc limit 1;'
        second_lastest_cluster_id_sql = 'select id from db_clusters where status = "inuse" order by id desc limit 1, 1;'
        meta_master_info = info.master().metadata()
        the_latest_cluster_id = connect.My(host=meta_master_info[0], port=meta_master_info[1], user=meta_master_info[2],
                                           pwd=meta_master_info[3], db='kunlun_metadata_db').sql_with_result(the_latest_cluster_id_sql)[0][0]
        second_lastest_cluster_id = connect.My(host=meta_master_info[0], port=meta_master_info[1], user=meta_master_info[2],
                                           pwd=meta_master_info[3], db='kunlun_metadata_db').sql_with_result(second_lastest_cluster_id_sql)[0][0]
        res = self.create_rcr(second_lastest_cluster_id, the_latest_cluster_id)
        return res

    def manualsw_rcr(self, meta_info, src_cluster_id, dst_cluster_id, delay=30):
        time_stamp = int(time.time())
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "manualsw_rcr",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                   "master_info": {
                        "meta_db": "%s" % meta_info,
                        "cluster_id": "%s" % src_cluster_id
                    },
                    "cluster_id": "%s" % dst_cluster_id,
                    "allow_sw_delay": "%s" % delay
                }
            }, indent=4
        )
        tmp_info = 'manualsw_rcr meta_db=[%s] src_cluster_id=[%s] dst_cluster_id=[%s] ' % (meta_info, src_cluster_id,
                                                                                         dst_cluster_id)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def delete_rcr(self, num=1):
        # num是元数据信息中正在运行的rcr里面第几个，第一个就是1，第二个就是2
        rcr_infos = info.node_info().show_all_running_rcr_info()
        total_rcr = len(rcr_infos)
        if total_rcr < num:
            write_log.w2File().print_log('当前正在运行的rcr个数为[%s], 指定的序号[%s]超过最大数，故跳过' % (total_rcr, num))
            return 1
        else:
            num = num - 1
            rcr_info = rcr_infos[num]

        time_stamp = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "delete_rcr",
            "timestamp": "%s" % time_stamp,
            "user_name": "kunlun_test",
            "paras": {
                "master_info": {
                "meta_db": "%s" % rcr_info[0],
                "cluster_id": "%s" % rcr_info[1]
                },
            "cluster_id": "%s" % rcr_info[2]
            }
        }, indent=4)
        tmp_info = 'delete_rcr meta_db=[%s] src_cluster_id=[%s] dst_cluster_id=[%s] ' % (rcr_info[0], rcr_info[1],
                                                                                         rcr_info[2])
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def set_noswitch(self, cluster_id, shard_id, timeout_second):
        # 免切设置
        time_stamp = int(time.time())
        json_data = json.dumps({
                "job_id": "",
                "job_type": "set_noswitch",
                "version": "1.0",
                "timestamp": "%s" % time_stamp,
                "user_name": "super_dba",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "shard_id": "%s" % shard_id,
                    "timeout": "%s" % timeout_second,
                    "type": "1"
                }
            }, indent=4
        )
        tmp_info = 'set_noswitch cluster_id [%s] shard_id [%s] timeout [%s] ' % (cluster_id, shard_id, timeout_second)
        write_log.w2File().tolog(json_data)
        res = requests.post(self.url, json_data)
        res_dict = json.loads(res.text)
        print(res_dict)
        error_code = res_dict['error_code']
        if error_code == "0":
            print(tmp_info + '成功')
            return 1
        else:
            print(tmp_info + '失败')
            return 0

    def delete_all_storage_replice(self):
        # 清除所有存储shard备节点
        all_replice_nodes = info.node_info().show_all_running_storage_replice()
        for replice_nodes in all_replice_nodes:
            self.del_nodes(replice_nodes[0], replice_nodes[1], replice_nodes[2], replice_nodes[3])

    def set_all_shard_noswitch(self, timeout_second):
        # 把所有shard都设置为免切模式
        all_shard_info = info.node_info().show_all_running_cluster_id_and_shard_id()
        for shard_info in all_shard_info:
            self.set_noswitch(shard_info[0], shard_info[1], timeout_second)

    def rebuild_node(self, shard_id, cluster_id, node_host, node_port, need_backup=0, hdfs_host='hdfs', pv_limit=10, allow_pull_from_master=1,
                     allow_replica_delay=15):
        # 重建存储节点
        time_stamp = int(time.time())
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "rebuild_node",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "shard_id": "%s" % shard_id,
                    "cluster_id": "%s" % cluster_id,
                    "rb_nodes": [
                        {
                            "hostaddr": "%s" % node_host,
                            "port": "%s" % node_port,
                            "need_backup": "%s" % need_backup,
                            "hdfs_host": "%s" % hdfs_host,
                            "pv_limit": "%s" % pv_limit
                        }
                    ],
                    "allow_pull_from_master": "%s" % allow_pull_from_master,
                    "allow_replica_delay": "%s" % allow_replica_delay
                }
            }, indent=4
        )
        tmp_info = 'rebuild node cluster_id[%s] shard_id[%s] host[%s] port[%s]' % (cluster_id, shard_id, node_host,
                                                                                   node_port)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def manual_backup_cluster(self, cluster_id):
        time_stamp = int(time.time())
        nick_name = info.node_info().show_cluster_nick_name(cluster_id=cluster_id)
        json_data = json.dumps({
                "version": "1.0",
                "job_id": "",
                "job_type": "manual_backup_cluster",
                "timestamp": "%s" % time_stamp,
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": "%s" % cluster_id,
                    "nick_name": "%s" % nick_name
                }
            }, indent=4
        )
        tmp_info = 'manual backup cluster_id[%s]' % cluster_id
        #meta_sql = "select status from cluster_general_job_log where " \
        #           "job_type='shard_coldbackup' order by id desc limit 1"
        #res = self.send_api_and_return_metares(json_data=json_data, sql=meta_sql, tmp_info=tmp_info)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def expand_cluster(self, cluster_id, src_shard_id, dst_shard_id, table_list):
        stamp_time = int(time.time())
        json_data = json.dumps({
              "version": "1.0",
              "job_id": "",
              "job_type": "expand_cluster",
              "timestamp": "%s" % stamp_time,
              "user_name": "kunlun_test",
              "paras": {
                "cluster_id": "%s" % cluster_id,
                "src_shard_id": "%s" % src_shard_id,
                "dst_shard_id": "%s" % dst_shard_id,
                "table_list": table_list
              }
            }, indent=4
        )
        tmp_info = 'manual backup cluster_id[%s] src_shard_id[%s] dst_shard_id[%s] ' \
                   'table_list[%s]' % (cluster_id, src_shard_id, dst_shard_id, table_list)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def control_instance(self, host, port, machine_type, control_type):
        stamp_time = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "control_instance",
            "timestamp": "%s" % stamp_time,
            "paras": {
                "hostaddr": "%s" % host,
                "port": "%s" % port,
                "machine_type": "%s" % machine_type,
                "control": "%s" % control_type
                }
            }
        )
        tmp_info = 'control instance host[%s] port[%s] manchine_type[%s] control_type[%s]' % (host, port, machine_type,
                                                                                              control_type)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def update_cluster_coldback_time_period(self, cluster_id, time_period_str=None):
        # 应该是用来修改冷备时间的api
        # time_period_str == "01:00:00-02:00:00", 应该是这个格式
        stamp_time = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "update_cluster_coldback_time_period",
            "timestamp": "%s" % stamp_time,
            "user_name": "kunlun_test",
            "paras": {
                   "cluster_id": "%s" % cluster_id,
                   "time_period_str": "%s" % time_period_str
                     }
            }, indent=4
        )
        tmp_info = 'update cluster coldback time period cluster_id[%s] time_period[%s]' % (cluster_id, time_period_str)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res

    def update_instance_cgroup(self, ip, port, node_type='mysql', cpu_cores=8, cgroup_mode='quota'):
        # node_type = [mysql]|[pg], cgroup_mode = [quota]|[share]
        # 修改 MySQL 或者 PostgreSQL 实例的资源隔离参数
        stamp_time = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "update_instance_cgroup",
            "timestamp": "%s" % stamp_time,
            "user_name": "kunlun_test",
            "paras": {
                "ip": "%s" % ip,
                "port": "%s" % port,
                "type": "%s" % node_type,
                "cpu_cores": "%s" % cpu_cores,
                "cgroup_mode": "%s" % cgroup_mode
                }
            }, indent=4
        )
        tmp_info = 'update_instance_cgroup ip=[%s], port[%s], type[%s], cpu_cores[%s], cgroup_mode[%s]' \
                   '' % (ip, port, node_type, cpu_cores, cgroup_mode)
        res = self.send_api_and_return_res(json_data=json_data, tmp_info=tmp_info)
        return res
