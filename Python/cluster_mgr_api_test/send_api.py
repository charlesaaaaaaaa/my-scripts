from base.api import get, post
from base.other import info
import argparse
import random, json


def get_url():
    mgr_info = info.master().cluster_mgr()
    url = 'http://%s:%s/HttpService/Emit' % (mgr_info[0], mgr_info[1])
    print("当前请求的cluster_mgr地址为： " + url)


def get_status():
    res = get.status().job_status(job_id=job_id)
    print(res)


def delete_all_clusters():
    res = post.cluster_setting(0).delete_cluster_all()
    if res == 0:
        exit(1)


def delete_clsuter():
    res = post.cluster_setting(0).delete_clsuter(cluster_id=cluster_id)
    if res == 0:
        exit(1)


def Create_cluster(shard, shard_nodes, comps, cpu_cores, cpu_limit_node, other_paras, nick_name):
    if nick_name == 'random_nick_name':
        nick_name = random.randint(0, 10000)
        nick_name = 'tmpdb_%s' % nick_name
    if other_paras:
        other_paras = json.loads(other_paras)
    res = post.cluster_setting(0).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=shard, nodes=shard_nodes,
                                           comps=comps, cpu_cores=cpu_cores, cpu_limit_node=cpu_limit_node, other_paras_dict=other_paras)
    if res == 0:
        exit(1)


def delete_all_replace():
    res = post.cluster_setting(0).delete_all_storage_replice()
    if res == 0:
        exit(1)


def create_rcr_with_thesame_metadata():
    res = post.cluster_setting(0).create_rcr_with_thelatest_clusters()
    if res == 0:
        exit(1)


def delete_rcr(rcr_postition):
    res = post.cluster_setting(0).delete_rcr(rcr_postition)
    if res == 0:
        exit(1)


def manualsw_rcr(meta_info, cluster_id, dst_cluster_id):
    if meta_info == None:
        meta_info = info.node_info().show_all_meta_ip_port_by_clustermgr_format()
    if cluster_id == None:
        cluster_id = info.node_info().show_all_running_cluster_id()[-2][0]
    if dst_cluster_id == None:
        dst_cluster_id = info.node_info().show_all_running_cluster_id()[-1][0]
    res = post.cluster_setting(0).manualsw_rcr(meta_info=meta_info, src_cluster_id=cluster_id,
                                               dst_cluster_id=dst_cluster_id)
    if res == 0:
        exit(1)


def add_shard(cluster_id=None, shards=1, nodes=1):
    if cluster_id == None:
        cluster_id = info.node_info().show_all_running_cluster_id()[-1][0]
    res = post.cluster_setting(0).add_shards(cluster_id=cluster_id, shards=shards, nodes=nodes)
    if res == 0:
        exit(1)


def logical_restore(src_cluster_id, dst_cluster_id, restore_type, restore_info):
    res = post.cluster_setting(0).logical_restore(src_cluster_id=src_cluster_id, dst_cluster_id=dst_cluster_id,
                                                  restore_type=restore_type, restore_info=restore_info)
    if res == 0:
        exit(1)


if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='send cluster_api')
    ps.add_argument('--action', help='[create_cluster]|[delete_cluster]|[delete_all_cluster]|[delete_all_storage_replace]'
                                     '|[set_all_shard_noswitch]|[create_rcr]|[delete_rcr]|[manualsw_rcr]|[add_shard]'
                                     '|[logical_restore]|[get_job_status]')
    ps.add_argument('--shard', help='shard number', default=1)
    ps.add_argument('--shard_nodes', help='shard nodes', default=3)
    ps.add_argument('--other_paras')
    ps.add_argument('--cluster_id', default=None)
    ps.add_argument('--dst_cluster_id', default=None)
    ps.add_argument('--meta_info', default=None)
    ps.add_argument('--comps', help='computing nodes', default=1)
    ps.add_argument('--rcr_pos', help='在元数据信息中[正在运行]的rcr序号, default=1', type=int, default=1)
    ps.add_argument('--cpu_cores', help='default=8', type=int, default=8)
    ps.add_argument('--cpu_limit_node', help="[quota]|[share], defualt=quota", type=str, default='quota')
    ps.add_argument('--restore_type', help='db|schema|table', type=str)
    ps.add_argument('--restore_info', help='这个选项给一个列表数据，元素为字典。如[{"db_table":"postgres_$$_public.t1","restore_time":"2022-10-20 19:20:15"},'
                                           ' [{第二个同步信息}]', type=list)
    ps.add_argument('--job_id', help='使用job_status时要指定的job id', type=str)
    ps.add_argument('--printurl', help='打印出当前请求的url', action='store_true')
    ps.add_argument('--cluster_nick_name', help='集群的别名，默认为random_nick_name，随机别名', type=str, default='random_nick_name')
    args = ps.parse_args()
    action = args.action
    shard = args.shard
    shard_nodes = args.shard_nodes
    other_paras = args.other_paras
    comps = args.comps
    rcr_pos = args.rcr_pos
    dst_cluster_id = args.dst_cluster_id
    meta_info = args.meta_info
    cluster_id = args.cluster_id
    cpu_cores = args.cpu_cores
    cpu_limit_node = args.cpu_limit_node
    restore_type = args.restore_type
    restore_info = args.restore_info
    job_id = args.job_id
    nick_name = args.cluster_nick_name
    if args.printurl:
        get_url()
    if action == 'delete_all_cluster':
        delete_all_clusters()
    elif action == "delete_cluster":
        delete_clsuter()
    elif action == 'create_cluster':
        Create_cluster(shard, shard_nodes, comps, cpu_cores=cpu_cores, cpu_limit_node=cpu_limit_node, other_paras=other_paras, nick_name=nick_name)
    elif action == 'delete_all_storage_replace':
        post.cluster_setting(0).delete_all_storage_replice()
    elif action == 'set_all_shard_noswitch':
        # 7 days
        post.cluster_setting(0).set_all_shard_noswitch(604800)
    elif action == 'create_rcr':
        create_rcr_with_thesame_metadata()
    elif action == 'delete_rcr':
        delete_rcr(rcr_postition=rcr_pos)
    elif action == 'manualsw_rcr':
        manualsw_rcr(meta_info=meta_info, cluster_id=cluster_id, dst_cluster_id=dst_cluster_id)
    elif action == 'add_shard':
        add_shard(cluster_id=cluster_id, shards=shard, nodes=shard_nodes)
    elif action == 'logical_restore':
        logical_restore(src_cluster_id=cluster_id, dst_cluster_id=dst_cluster_id, restore_type=restore_type, restore_info=restore_info)
    elif action == 'get_job_status':
        get_status()
