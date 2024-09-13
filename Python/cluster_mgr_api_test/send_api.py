from base.api import get, post
from base.other import info
import argparse
import random


def delete_all_clusters():
    res = post.cluster_setting(0).delete_cluster_all()
    if res == 0:
        exit(1)


def delete_clsuter():
    res = post.cluster_setting(0).delete_clsuter(cluster_id=cluster_id)
    if res == 0:
        exit(1)

def Create_cluster(shard, shard_nodes, comps, cpu_cores, cpu_limit_node):
    nick_name = random.randint(0, 10000)
    nick_name = 'tmpdb_%s' % nick_name
    res = post.cluster_setting(0).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=shard, nodes=shard_nodes,
                                           comps=comps, cpu_cores=cpu_cores, cpu_limit_node=cpu_limit_node)
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


if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='send cluster_api')
    ps.add_argument('--action', help='[create_cluster]|[delete_cluster]|[delete_all_cluster]|[delete_all_storage_replace]'
                                     '|[set_all_shard_noswitch]|[create_rcr]|[delete_rcr]|[manualsw_rcr]')
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
    if action == 'delete_all_cluster':
        delete_all_clusters()
    elif action == "delete_cluster":
        delete_clsuter()
    elif action == 'create_cluster':
        Create_cluster(shard, shard_nodes, comps, cpu_cores=cpu_cores, cpu_limit_node=cpu_limit_node)
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

