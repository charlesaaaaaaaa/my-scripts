#获取相关信息
cd /home/kunlun/
nets=`cat /etc/confd/confd.toml  | grep nodes | awk -F= '{print $2}' | sed 's/^...//' | sed 's/..$//'`
curl $nets > /home/kunlun/scale.txt
diff /home/kunlun/configure.txt /home/kunlun/scale.txt > /home/kunlun/difftmp.txt
sed -i 's/^..//' /home/kunlun/difftmp.txt
selfRole=`cat /home/kunlun/scale.txt | grep /self/host/role | awk '{print $2}'`
metaIp=`cat /home/kunlun/scale.txt | grep /self/hosts/meta_data_node/ | grep /ip | awk '{print $2}'`
selfIp=`cat scale.txt | grep self/host/ip | awk '{print $2}'`
action=$1
#scaleIp1=`diff configure.txt scaleOut.txt | grep self/hosts/data_node/ | grep /ip | head -1 | awk '{print $3}'`

startCluster(){
	for i in `cat scale.txt | grep /self | grep meta_data | grep /ip | awk '{print $2}'`
	do
		bash start_cluster.sh $i
	done
}

if [[ "$selfRole" = "meta_data_node" ]]
then
	if [[ "$action" = "addshards" ]]
	then
	#当运行是addshards的时候，产生对应的配置文件
	#/home/kunlun/cluster_mgr_sc/addShards.yaml
	#/home/kunlun/base
		cat << EOF > /home/kunlun/cluster_mgr_sc/addShards.yaml
user_name: "kunlun"
mysql_port_range: "8000-10000"
datadir: "/home/kunlun/base/storage_datadir"
logdir: "/home/kunlun/base/storage_logdir"
wal_log_dir: "/home/kunlun/base/storage_waldir"
EOF
		total_memory=`cat difftmp.txt | grep /self/hosts/data_node | grep /memory | awk '{print $2}' | sort | uniq`
		total_cpu_cores=`cat difftmp.txt | grep /self/hosts/data_node | grep /cpu | grep -v cpu_model | awk '{print $2}' | sort | uniq`
		nodes=`cat difftmp.txt | grep /self/hosts/data_node | grep /sid | wc -l`
                shards=`cat difftmp.txt | grep /self/hosts/data_node | grep /gid | awk '{print $2}' | sort  | uniq | wc -l`
		cat << EOF >> /home/kunlun/cluster_mgr_sc/addShards.yaml
total_mem: "$total_memory"
total_cpu_cores: "$total_cpu_cores"
shards: $shards
nodes: $nodes
MetaPrimaryNode:
	host: "$metaIp"
	port: "6001"
dataHost:
EOF
		for i in `cat difftmp.txt | grep /self/hosts/data_node | grep /ip | awk '{print $2}'`
		do
			cat << EOF >> /home/kunlun/cluster_mgr_sc/addShards.yaml
        - $i
EOF
		done
		
		#重启所有 clustermgr，不然新增的nodeMGR无法生效
		cd /home/kunlun/
		startCluster
		
		sleep 15

		cd /home/kunlun/cluster_mgr_sc
		# 文件产生完后运行脚本发送api
		python3 addShards.py --config addShards.yaml
		cd /home/kunlun/

		mv /home/kunlun/scale.txt /home/kunlun/configure.txt
	
	elif [[ "$action" = "addcomps" ]]
	then
		total_cpu_cores=`cat difftmp.txt | grep /self/hosts/computing_node | grep -w cpu | awk '{print $2}'`
		total_memory=`cat difftmp.txt | grep /self/hosts/computing_node | grep -w memory | awk '{print $2}'`
		nodes=`cat difftmp.txt | grep /self/hosts/computing_node | grep /sid | wc -l`
		cat << EOF > /home/kunlun/cluster_mgr_sc/addComps.yaml
MetaPrimaryNode:
        host: $metaIp
        port: "6001"
user_name: "kunlun"
pgsql_port_range: "5431-8000"
comp_datadir: "/home/kunlun/base/server_datadir"
EOF
		cat << EOF >> /home/kunlun/cluster_mgr_sc/addComps.yaml
total_mem: $total_memory
total_cpu_cores: $total_cpu_cores
comps: $nodes
dataHost:
EOF
		for i in `cat difftmp.txt  | grep /self/hosts/computing_node/ | grep /ip | awk '{print $2}'`
		do
			cat << EOF >> /home/kunlun/cluster_mgr_sc/addComps.yaml
        - $i
EOF
		done
		
		#重启所有 clustermgr，不然新增的nodeMGR无法生效
                cd /home/kunlun/
                startCluster

		sleep 15

		#产生配置文件后发送api
		cd /home/kunlun/cluster_mgr_sc
		python3 addComps.py --config addComps.yaml
		cd /home/kunlun/
		mv /home/kunlun/scale.txt /home/kunlun/configure.txt

	elif [[ "$action" = "addcluster" ]]
	then
		total_mem=`cat /home/kunlun/difftmp.txt | grep memory | awk '{print $2}' | sort | uniq | head -1`
		total_cpu_cores=`cat /home/kunlun/difftmp.txt | grep -w cpu | awk '{print $2}' | sort | uniq | head -1`
		comps=`cat difftmp.txt | grep /self | grep computing | grep /sid | wc -l`
		nodes=`cat difftmp.txt | grep /self | grep data_node | grep /sid | wc -l`
		shards=`cat difftmp.txt | grep /self | grep data_node | grep /gid | awk '{print $2}' | sort | uniq | wc -l`
		cat << EOF > /home/kunlun/cluster_mgr_sc/addcluster.yaml
pgsql_port_range: "5431-8000"
mysql_port_range: "8000-10000"
MetaPrimaryNode:
        host: "$metaIp"
	port: "6001"
ha_mode: "rbr"
dbcfg: "1"
user_name: "kunlun"
datadir: "/home/kunlun/base/storage_datadir"
logdir: "/home/kunlun/base/storage_logdir"
wal_log_dir: "/home/kunlun/base/storage_waldir"
comp_datadir: "/home/kunlun/base/server_datadir"
nick_name: "Kunlun-Test"
max_storage_size: "20"
max_connections: "6"
innodb_size: "1"
fullsync_level: "1"
total_mem: "$total_mem"
total_cpu_cores: "$total_cpu_cores"
shards: $shards
nodes: $nodes
comps: $comps
computer:
EOF
		for i in `cat /home/kunlun/difftmp.txt | grep /self/hosts/computing | grep /ip | awk '{print $2}'`
		do
			cat << EOF >> /home/kunlun/cluster_mgr_sc/addcluster.yaml
	- $i
EOF
		done

		echo 'storage:' >> /home/kunlun/cluster_mgr_sc/addcluster.yaml
		for i in `cat /home/kunlun/difftmp.txt | grep /self/hosts/data_node | grep /ip | awk '{print $2}'`
		do
			cat << EOF >> /home/kunlun/cluster_mgr_sc/addcluster.yaml
        - $i
EOF
		done

		#重启所有 clustermgr，不然新增的nodeMGR无法生效
                cd /home/kunlun/
                startCluster

		sleep 15

                #产生配置文件后发送api
                cd /home/kunlun/cluster_mgr_sc
                python3 install_cluster.py --config /home/kunlun/cluster_mgr_sc/addcluster.yaml
                cd /home/kunlun/
                mv /home/kunlun/scale.txt /home/kunlun/configure.txt
	fi
fi

