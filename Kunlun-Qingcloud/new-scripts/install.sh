rm -rf conf && mkdir conf
nets=`cat /etc/confd/confd.toml  | grep nodes | awk -F= '{print $2}' | sed 's/^...//' | sed 's/..$//'`
curl $nets > configure.txt
compIp=`cat configure.txt | grep /self/hosts/computing_node/ | grep /ip | awk '{print $2}'`
dataIp=`cat configure.txt | grep /self/hosts/data_node/ | grep /ip | awk '{print $2}'`
dataGid=`cat configure.txt | grep /self/hosts/data_node/ | grep /gid | awk '{print $2}'`
dataRepIp=`cat configure.txt | grep /self/hosts/data_node-replica/ | grep /ip | awk '{print $2}'`
dataRepGid=`cat configure.txt | grep /self/hosts/data_node-replica/ | grep /gid | awk '{print $2}'`
metaIp=`cat configure.txt | grep /self/hosts/meta_data_node/ | grep /ip | awk '{print $2}'`
metaRepIp=`cat configure.txt | grep /self/hosts/meta_data_node-replica/ | grep /ip | awk '{print $2}'`
selfRole=`cat configure.txt | grep /self/host/role | awk '{print $2}'`
selfIp=`cat configure.txt | grep /self/host/ip | awk '{print $2}'`
#for i in $compIp; do echo comp: $i; done
#for i in $dataIp; do echo data: $i; done
#echo $dataGid
#for i in $dataRepIp; do echo dataRep: $i; done
#echo $dataRepGid
#for i in $metaIp; do echo meta: $i; done
#for i in $metaRepIp; do echo metaRep: $i; done
#echo i am $selfRole and my ip is $selfIp

# 产生对应的配置文件

# data节点配置文件
for i in $dataGid
do
	masterId=`cat configure.txt | grep "$i"$ | grep /self/hosts/data_node/ | grep gid | awk -F/ '{print $5}'`
	master_dataip=`cat configure.txt | grep "$masterId" | grep /self/hosts/data_node/ | grep /ip | awk '{print $2}'`
	repDataGId=`echo $dataRepGid | grep "$i"$ | grep /self/hosts/data_node-replica/ | grep gid | awk -F/ '{print $5}'`
	echo -en \"group_seeds\": \"$master_dataip:6001 >> conf/data${i}seed.txt
	echo -e mas: $master_dataip >> conf/data${i}.txt
	#echo -n "$master_dataip" >> conf/dataIp${i}.txt
	
	for m in `cat configure.txt | grep "$i"$ | grep /self/hosts/data_node-replica/ | grep gid | awk -F/ '{print $5}'`
	do
		rep_dataip=`cat configure.txt | grep "$m" | grep /self/hosts/data_node-replica/ | grep /ip | awk '{print $2}'`
		echo -n ,$rep_dataip:6001 >> conf/data${i}seed.txt
		echo -e rep: $rep_dataip >> conf/data${i}.txt
		echo -n " $rep_dataip" >> conf/dataIp${i}.txt
	done
	
	echo -n \" >> conf/data${i}seed.txt
done

# meta 节点配置文件
rm -rf conf/meta.txt
echo $metaIp >> conf/meta.txt
echo -en $metaIp >> conf/metaSeed.txt
echo -en $metaIp:6001 >> conf/metaClusterSeed.txt
for i in `cat configure.txt | grep /self/hosts/meta_data_node-replica/ | grep /ip | awk '{print $2}'`
do
	echo $i >> conf/meta.txt
	echo -n " $i" >> conf/metaIp.txt
	echo -n " $i" >> conf/metaSeed.txt
	echo -n ",$i:6001" >> conf/metaClusterSeed.txt
done 

# comp 节点配置文件
rm -rf conf/data.txt
for i in `cat configure.txt | grep /self/hosts/computing_node/ | grep /ip | awk '{print $2}'`
do
	echo $i >> conf/comp.txt
	echo -n $i >> conf/compIp.txt
done

# cluster_mgr 配置文件
echo -en $metaIp:56001:0 >> conf/clusterSeed.txt
for i in `cat configure.txt | grep /self/hosts/meta_data_node-replica/ | grep /ip | awk '{print $2}'`
do
	echo -n ",$i:56001:0" >> conf/clusterSeed.txt
done

if [[ "$selfRole" == "meta_data_node"  ]]
then
	# 生成mysql_meta.json文件
	metaseeds=`cat conf/metaSeed.txt`
	echo metaseeds = $metaseeds
	metaIpR=`cat conf/metaIp.txt`
	echo metaIpR = $metaIpR
	/bin/bash change_conf.sh meta "$metaseeds" "$metaIpR"
	
	# 修改cluster_mgr配置文件
	clusterSeeds=`cat conf/clusterSeed.txt`
	echo `cat conf/clusterSeed.txt`
	clusterMetaSeeds=`cat conf/metaClusterSeed.txt`
	/bin/bash change_conf.sh cluster $selfIp "$clusterMetaSeeds" "$clusterSeeds"
	
	# 修改node_mgr配置文件
	/bin/bash change_conf.sh node $selfIp "$clusterMetaSeeds"

	#安装
	cd /home/kunlun/base/program_binaries/kunlun-storage-1.0.1/dba_tools
	python2 install-mysql.py --config=/home/kunlun/conf/mysql_meta.json --target_node_index=0 --cluster_id=meta --shard_id=meta --server_id=1 --ha_mode=mgr
	cd /home/kunlun/base/kunlun-cluster-manager-1.0.1/bin
	bash start_cluster_mgr.sh </dev/null >& start.log & 
	cd /home/kunlun/base/kunlun-node-manager-1.0.1/bin
	bash start_node_mgr.sh </dev/null >& start.log &
	sleep 15
	cd $HOME
	python2 bootstrap.py --config=./conf/reg_meta.json --bootstrap_sql=/home/kunlun/base/program_binaries/kunlun-server-1.0.1/scripts/meta_inuse.sql --ha_mode=mgr
	bash imysql.sh 6001 < dba_tools_db.sql
	
elif [[ "$selfRole" == "meta_data_node-replice" ]]
then
	metaseeds=`cat conf/metaSeed.txt`
        echo metaseeds = $metaseeds
        metaIpR=`cat conf/metaIp.txt`
        echo metaIpR = $metaIpR
        /bin/bash change_conf.sh meta "$metaseeds" "$metaIpR"

        # =======================================================================
        n=2
        for i in `cat configure.txt | grep /self/hosts/meta_data_node-replica/ | grep /ip | awk '{print $2}'`
        do
                echo $i
                if [[ "$i" != "$selfIp" ]]
                then
                        n=`echo "$n+1" | bc -l `
                elif [[ "$i" == "$selfIp" ]]
                then
                        serid=$n
                        echo yes!! $serid
                fi
        done
	clusterSeeds=`cat conf/clusterSeed.txt`
        echo `cat conf/clusterSeed.txt`
        clusterMetaSeeds=`cat conf/metaClusterSeed.txt`
        /bin/bash change_conf.sh cluster $selfIp "$clusterMetaSeeds" "$clusterSeeds"
	/bin/bash change_conf.sh node $selfIp "$clusterMetaSeeds"
        # =======================================================================
        tni=`echo "{$serid}-1" | bc -l`
	#/home/kunlun/base/program_binaries/kunlun-server-1.0.1/scripts/meta_inuse.sql

	cd /home/kunlun/base/program_binaries/kunlun-storage-1.0.1/dba_tools
	python2 install-mysql.py --config=/home/kunlun/conf/mysql_meta.json --target_node_index=$tni --cluster_id=meta --shard_id=meta --server_id=$serid --ha_mode=mgr
	cd /home/kunlun/base/kunlun-cluster-manager-1.0.1/bin
        bash start_cluster_mgr.sh </dev/null >& start.log &
        cd /home/kunlun/base/kunlun-node-manager-1.0.1/bin
        bash start_node_mgr.sh </dev/null >& start.log &


elif [[ "$selfRole" == "computer_node" ]]
then
	/bin/bash change_conf.sh node $selfIp "$clusterMetaSeeds"
	cd /home/kunlun/base/kunlun-node-manager-1.0.1/bin
        bash start_node_mgr.sh </dev/null >& start.log &

elif [[ "$selfRole" == "data_node" ]]
then
	/bin/bash change_conf.sh node $selfIp "$clusterMetaSeeds"
        cd /home/kunlun/base/kunlun-node-manager-1.0.1/bin
        bash start_node_mgr.sh </dev/null >& start.log &

elif [[ "$selfRole" == "data_node-replice" ]]
then
        /bin/bash change_conf.sh node $selfIp "$clusterMetaSeeds"
        cd /home/kunlun/base/kunlun-node-manager-1.0.1/bin
        bash start_node_mgr.sh </dev/null >& start.log &
fi
