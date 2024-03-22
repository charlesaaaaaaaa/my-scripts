from base.other import info
from base.other import write_log
from base.api import get
import requests
import time
import json
import random

class cluster_setting():
    def __init__(self):
        self.mgr_info = info.master().cluster_mgr()
        self.url = 'http://%s:%s/HttpService/Emit' % (self.mgr_info[0], self.mgr_info[1])

    def random_nodes(self, node_num, node_list):
        # 在 节点ip列表 里面随机选择 node_num 个数的节点
        random_node_list = []
        for times in range(node_num):
            random_node = random.choices(node_list)
            while random_node in random_node_list:
                random_node = random.choices(node_list)
            random_node_list.append(random_node)
        return random_node_list

    def get_status(self, job_id):
        # 检查job status
        result = 'done'
        job_status = get.status().job_status(job_id)
        res = job_status['status']
        while res != 'done':
            time.sleep(5)
            job_status = get.status().job_status(job_id)
            res = job_status['status']
            if res == "failed":
                write_log.w2File().tolog('ERROR: 调用api失败')
                result = res
                break
        return result


    def create_cluster(self, user_name, nick_name, shard, nodes, comps, max_storage_size, max_connections,
                       cpu_cores, cpu_limit_node, innodb_size, rocksdb_block_cache_size_M, fullsync_level,
                       data_storage_MB, log_storage_MB, other_paras_dict):
        # 这个函数就是用来发送创建集群的api
        # 当前只有rbr，所以不用设置ha_mode
        # 共要给 13 个变量
        #   除开最后一个，其它12个都是create_cluster api里面必填的参数, 这12个参数的信息去api文档看，gitee上的文档有
        #       这12个变量名和api的参数变量名是一样的，可以直接对着api文档填写
        #   最后一个(other_paras_dict)是非必填的参数
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
                "log_storage_MB": str(log_storage_MB), "fullsync_level": str(fullsync_level)}
        if other_paras_dict != {}:
            para.update(other_paras_dict)
        # 这里通过函数获取可以安装计算节点和存储节点并正在运行的机器ip
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
        stor_nodes_need = int(shard) * int(nodes)
        comps = int(comps)
        # 这里开始判断，如果要用到的计算节点数量或者存储节点数量小于可以安装的节点
        #   则随机从可安装的节点里面选择其中几个
        #   否则直接把所有可安装的节点全选上
        if stor_nodes_need < len(stor_list):
            storage_iplists = self.random_nodes(stor_nodes_need, stor_list)
        else:
            storage_iplists = stor_list
        if comps < len(comp_list):
            computer_iplists = self.random_nodes(comps, comp_list)
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
            }
        )
        res = requests.post(url, data=json_data)
        if res.status_code == 200:
            write_log.w2File().tolog('调用 create_cluster 成功, 等待安装完成')
            write_log.w2File().tolog(json_data)
        post_res = json.loads(res.text)
        write_log.w2File().tolog(post_res)
        print(post_res)
        job_id = int(post_res['job_id'])
        # 检查job status
        job_status = self.get_status(job_id)
        if job_status == 'done':
            write_log.w2File().tolog('创建集群成功')
            print('创建集群成功')
            job_status = get.status().job_status(job_id)
            result = [job_status['status'], job_status['attachment']]
        elif job_status == 'failed':
            write_log.w2File().tolog('创建集群失败')
            print('创建集群失败')
            result = 0
        return result

    def add_shards(self, cluster_id, shards, nodes):
        # 这里只要给cluster_id, shards, nodes
        # storage_iplists 会自动生成
        # 如果成功，会返回一个列表
        #   第0个是状态码
        #   第1个是新增分片的信息
        result = 1
        comp_list, stor_list = info.node_info().show_all_running_sever_nodes()
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
            }
        )
        write_log.w2File().tolog('开始调用 add_shards')
        print('开始调用 add_shards')
        write_log.w2File().tolog(json_data)
        res = requests.post(self.url, json_data)
        res_dict = json.loads(res.text)
        job_id = res_dict['job_id']
        write_log.w2File().tolog(res_dict)
        print(res_dict)
        # 检查job status
        job_status = self.get_status(job_id)
        if job_status == 'done':
            write_log.w2File().tolog('add_shards 成功')
            print('add_shards 成功')
            job_status = get.status().job_status(job_id)
            result = [job_status['status'], job_status['attachment']]
        elif job_status == 'failed':
            write_log.w2File().tolog('add_shards 失败')
            print('ERROR: add_shards 失败')
            result = 0
        return result
