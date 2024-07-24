from base.api import get, post
import argparse
import random

def delete_all_clusters():
    res = post.cluster_setting(0).delete_cluster_all()
    if res == 0:
        exit(1)

def Create_cluster(shard, shard_nodes, comps):
    nick_name = random.randint(0, 10000)
    nick_name = 'tmpdb_%s' % nick_name
    res = post.cluster_setting(0).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=shard, nodes=shard_nodes,
                                           comps=comps)
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

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='send cluster_api')
    ps.add_argument('--action', help='[create_cluster]|[delete_all_cluster]|[delete_all_storage_replace]'
                                     '|[set_all_shard_noswitch]|[create_rcr]|[delete_rcr]')
    ps.add_argument('--shard', help='shard number', default=1)
    ps.add_argument('--shard_nodes', help='shard nodes', default=3)
    ps.add_argument('--other_paras')
    ps.add_argument('--comps', help='computing nodes', default=1)
    ps.add_argument('--rcr_pos', help='在元数据信息中[正在运行]的rcr序号, default=1', type=int, default=1)
    args = ps.parse_args()
    action = args.action
    shard = args.shard
    shard_nodes = args.shard_nodes
    other_paras = args.other_paras
    comps = args.comps
    rcr_pos = args.rcr_pos
    if action == 'delete_all_cluster':
        delete_all_clusters()
    elif action == 'create_cluster':
        Create_cluster(shard, shard_nodes, comps)
    elif action == 'delete_all_storage_replace':
        post.cluster_setting(0).delete_all_storage_replice()
    elif action == 'set_all_shard_noswitch':
        # 7 days
        post.cluster_setting(0).set_all_shard_noswitch(604800)
    elif action == 'create_rcr':
        create_rcr_with_thesame_metadata()
    elif action == 'delete_rcr':
        delete_rcr(rcr_postition=rcr_pos)


