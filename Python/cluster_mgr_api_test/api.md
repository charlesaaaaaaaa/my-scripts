# base目录 
## get
* base.api.get.mgr_infos().cluster_info()
    * 获取cluster集群信息的
* base.api.get.status().cluster()
  * 在api上获取cluster集群信息的
* base.api.get.status().job_status()
  * 在api上获取某个任务的完成状态的
## post
* base.api.post.cluster_setting().random_nodes()
  * 在 节点ip列表 里面随机选择 node_num 个数的节点
* base.api.post.cluster_setting().get_status()
  * 自动检查job status 并返回状态
* base.api.post.cluster_setting().create_cluster()
  * 创建群集
* base.api.post.cluster_setting().add_shards()
  * 增加一个shard
* base.api.post.cluster_setting().delete_cluster_all()
  * 清理掉所有集群
* base.api.post.cluster_setting().add_comps(cluster_id, comps_num, comps_iplist)
  * 增加计算节点
* base.api.post.cluster_setting().del_comps(cluster_id, comp_id)
  * 删除计算节点
* base.api.post.cluster_setting().del_shard(cluster_id, shard_id)
  * 删除shard
* base.api.post.cluster_setting().add_nodes(cluster_id, shard_id, nodes_num, stor_iplists)
  * 增加存储节点
* base.api.post.cluster_setting().del_nodes(cluster_id, shard_id, stor_node_host, stor_node_port)
  * 删除存储节点
* base.api.post.cluster_setting().repartition_tables(src_cluster_id, dst_cluster_id, repartition_tables)
  * 表重分布
* base.api.post.cluster_setting().logical_backup(cluster_id, backup_type, backup_info)
  * 表逻辑备份
* base.api.post.cluster_setting().logical_restore(src_cluster_id, dst_cluster_id, restore_type, restore_info)
  * 表逻辑恢复（回档）
* base.api.post.cluster_setting().create_rcr(meta_info, src_cluster_id, dst_cluster_id)
  * 建立rcr数据同步, 用户发起对两个cluster建立rcr数据同步
# other 目录
## connect
* base.other.connect.Pg(host, port, user, pwd, db).ddl_sql(sql)
  * pg 执行一条sql并commit，不会返回值
* base.other.connect.Pg(同上).sql_with_result(sql)
  * pg 执行一条构sql并commit且关闭游标连接，返回一个列表
* base.other.connect.Pg(同上).colse()
  * pg 关闭游标连接
* base.other.connect.My(host, port, user, pwd, db).ddl_sql
  * mysql 执行一条sql并commit，不会返回值
* base.other.connect.Pg(同上).sql_with_result(sql)
  * mysql 执行一条构sql并commit且关闭游标连接，返回一个列表
* base.other.connect.Pg(同上).colse()
  * mysql 关闭游标连接
## getconf
* base.other.getconf.get_conf_info().cluster_mgr()
  * 获取config.conf 配置文件里面的[cluster_mgr]
* base.other.getconf.get_conf_info().klustron_metadata()
  * 获取config.conf 配置文件里面的[klustron_metadata]
## info
* base.other.info.master().metadata()
  * 获取 **metadata主节点** 的信息
  * 返回一个元组，如：('192.168.0.170', 18882, user, port)
* base.other.info.master().cluster_mgr()
  * 获取 **cluster_mgr主节点** 信息
  * 返回一个元组，如：('192.168.0.170', 18885)
* base.other.info.node_info().get_sql(sql)
  * 没看明白昰干啥的
* base.other.info.node_info().get_res(sql)
  * 在 **元数据节点[kunlun_metadata_db]里面查询sql** 并返回一个元组
* base.other.info.node_info().show_all_running_sever_nodes()
  * 获取正在运行的 **server nodes**
  * 会返回两个列表, 第0个元素是可安装的计算节点ip， 第1个元素则是可安装的存储节点ip
* base.other.info.node_info().show_all_running_computer()
  * 获取所有在运行的 **计算节点信息** ，返回一个列表，列表里面有多个元组
  * 每个元组里面第0个元素是ip，第1个元素是port, 2是用户， 3是密码
* base.other.info.node_info().show_all_running_storage()
  * 获取所有在运行的 **存储节点信息** ，返回内容同上
* base.other.info.node_info().show_all_storage_with_id(shard_id)
  * 获取指定shard_id下的所有 **存储节点信息** ，返回一个元组，元组里面有多个二级元组
  * 元组内容如下：((node_id1, ip1, port1, user1, pwd1),(node_id2, ip2, port2, user2, pwd2)...)
* base.other.info.node_info().show_all_running_cluster_id()
  * 获取所有在运行的 **clusterid** , 返回一个元组，元组里面有多个二级元组
  * 每个元组里面第0个元素是cluster_id
* base.other.info.node_info().show_all_running_shard_id()
  * 获取所有在运行的 **shard_id** , 返回一个元组，元组里面有多个二级元组
  * 每个元组里面第0个元素是shard_id
* base.other.info.node_info().show_all_meta_ip_port_by_clustermgr_format()
  * 获取所有metadata的host和port, 以cluster_mgr配置文件的格式 返回一个str
  * 返回结果如：'192.168.0.0:3006,192.168.0.0:3007,192.168.0.1:3006'
* base.other.info.node_info().compare_shard_master_and_standby(dbname)
  * 对比指定数据库的存储节点 **主备内容是否一致**
  * 返回1是成功，返回0是失败
## sys_opt
| 选项名           | 内容                          |
|---------------|-----------------------------|
| node_type     | ['computer'] or ['storage'] |   
| variable_name | 变量名                         |
| value         | 变量值                         |
* base.other.sys_opt.setting_variable(node_type, variable_name, value).print_log(txt)
  * 把内容打印在屏幕上的同时写入日志文件里
* base.other.sys_opt.setting_variable(node_type, variable_name, value).get_res(node_info)
  * 获取存储节点指定变量值
  * node_info = (host, port, user, pwd)
* base.other.sys_opt.setting_variable(node_type, variable_name, value).set_sql(node_info) 
  * 设置存储节点指定变量值
  * node_info = (host, port, user, pwd)
## write_log
* base.other.write_log.w2File().tolog(txt)
  * 写到日志文件里面去
* base.other.write_log.w2File().print_log(txt)
  * 写到日志文件里面去的同时打印出来
* base.other.write_log.w2File().toOther(file_name, txt)
  * 写到指定文件里