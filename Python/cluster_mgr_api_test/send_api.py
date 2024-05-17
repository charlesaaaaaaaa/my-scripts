from base.api import get, post
import argparse
import random

def delete_all_clusters():
    post.cluster_setting(0).delete_cluster_all()

def Create_cluster(shard, shard_nodes, comps, other_paras):
    nick_name = random.randint(0, 10000)
    nick_name = 'tmpdb_%s' % nick_name
    post.cluster_setting(0).create_cluster(user_name='kunlun_test', nick_name=nick_name, shard=shard, nodes=shard_nodes,
                                                    comps=comps, max_storage_size=1024, max_connections=2000,
                                                    cpu_limit_node='quota', innodb_size=1024, cpu_cores=8,
                                                    rocksdb_block_cache_size_M=1024, fullsync_level=1,
                                                    data_storage_MB=1024, log_storage_MB=1024,
                                                    other_paras_dict=other_paras)
def delete_all_replace():
    post.cluster_setting(0).delete_all_storage_replice()

if __name__ == '__main__':
    ps = argparse.ArgumentParser(description='send cluster_api')
    ps.add_argument('--action', help='[create_cluster]|[delete_all_cluster]')
    ps.add_argument('--shard', help='shard number', default=1)
    ps.add_argument('--shard_nodes', help='shard nodes', default=3)
    ps.add_argument('--other_paras')
    ps.add_argument('--comps', help='computing nodes', default=1)
    args = ps.parse_args()
    action = args.action
    shard = args.shard
    shard_nodes = args.shard_nodes
    other_paras = args.other_paras
    comps = args.comps
    if action == 'delete_all_cluster':
        delete_all_clusters()
    elif action == 'create_cluster':
        Create_cluster(shard, shard_nodes, comps, other_paras)
    elif action == 'delete_all_storage_replace':
        post.cluster_setting(0).delete_all_storage_replice()
    elif action == 'set_all_shard_noswitch':
        # 7 days
        post.cluster_setting(0).set_all_shard_noswitch(604800)


