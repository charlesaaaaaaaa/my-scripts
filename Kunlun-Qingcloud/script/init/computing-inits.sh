cd /home/ubuntu/kunlun/kunlun-computing/scripts/ 

mkdir -p /home/ubuntu/tmp

a=`cat /etc/confd/confd.toml | grep nodes | awk '{print $3}' | sed 's/..//' | sed 's/..$//'`

curl $a >> /home/ubuntu/tmp/a.txt

self_gid=`cat /home/ubuntu/tmp/a.txt | grep /self/host/gid | awk '{print $2}'`

self_ip=`cat /home/ubuntu/tmp/a.txt | grep /self/host/ip | awk '{print $2}'`

cat /home/ubuntu/tmp/a.txt | grep /self/hosts | grep comp | grep gid | awk '{print $2}' > /home/ubuntu/tmp/comp_gid.txt

cat /home/ubuntu/tmp/comp_gid.txt | sort -n >> /home/ubuntu/tmp/comp_gids.txt
sleep 1

#--------将计算节点对应的ip和port写入到comp-node.json--------
comp_num=`cat /home/ubuntu/tmp/comp_gids.txt | wc -l` #获取当前计算节点的个数

for i in `seq 1 $comp_num`
do	
	echo $i
	cat /home/ubuntu/tmp/a.txt | grep gid | grep self | grep hosts | grep "${i}"$ | grep comp | awk '{print $1}' | sed 's/...$//' >> /home/ubuntu/tmp/comp_frontname.txt
done
#生成计算节点配置文件
((b=$comp_num - 1))
echo '[' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "id":1,'  >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "name":"comp1",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "ip":"127.0.0.1",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "port":5401,' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "user":"abc",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "password":"abc",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo '	  "datadir":"/data/pg_data_dir1"'>> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json

for i in `seq 1 $b`
do
	((d=$i+1))
	echo '	},' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo '	{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "	  \"id\":${d}," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "          \"name\":\"comp${d}\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "          \"ip\":\"127.0.0.1\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "          \"port\":5401," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "          \"user\":\"abc\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "	  \"password\":\"abc\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
	echo "          \"datadir\":\"/data/pg_data_dir1\"" >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
done
echo '	}' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
echo ']' >> /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json


for i in `seq 1 $comp_num`
do
	a=`sed -n "${i}p" /home/ubuntu/tmp/comp_frontname.txt`
	c=`cat /home/ubuntu/tmp/a.txt | grep ${a} | grep /ip |awk '{print $2}'`
	sed -i "0,/127.0.0.1/s/127.0.0.1/${c}/" /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json
done

sed -i 's@/data@/home/ubuntu/kunlun/data@' /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json

python2 /home/ubuntu/kunlun/kunlun-computing/scripts/install_pg.py --config=/home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json --install_ids=${self_gid}

sleep 1 
#----------------------------------------------------

if [ $self_gid = 1 ] ; then

	meta_master=`cat /home/ubuntu/tmp/a.txt | grep /self/hosts/meta_data_node/ | grep /ip | awk '{print $2}'` #获取meta-data master 节点ip

	#-----------------获取meta——data的子节点---------------------------

	cat /home/ubuntu/tmp/a.txt | grep meta_data_node-re | grep /ip | grep self | awk '{print $2}' >/home/ubuntu/tmp/meta-replica.txt

	metare_num=`cat /home/ubuntu/tmp/meta-replica.txt | wc -l`

	#------------------------------------------------------------------

	#-----------------获取data-shard的数量及master节点的ip-------------
	
	cat /home/ubuntu/tmp/a.txt | grep /data_node/ | grep /ip | grep self | awk '{print $2}' > /home/ubuntu/tmp/datashard_num.txt

	datasha_num=`cat /home/ubuntu/tmp/datashard_num.txt | wc -l` 

	for i in `seq 1 $datasha_num`
	do
		mas=`cat /home/ubuntu/tmp/a.txt | grep self/hosts/data_node/ | grep gid | grep ${i}$ | awk '{print $1}' | sed 's/...$//'`
		cat /home/ubuntu/tmp/a.txt | grep "$mas" | grep /ip | awk '{print $2}' >> /home/ubuntu/tmp/datashards_num.txt
	done

	#------------------------------------------------------------------

	#----------------获取data-node子节点ip及对应的shard文本------------

	for i in `seq 1 ${datasha_num}`
	do
		cat /home/ubuntu/tmp/a.txt | grep /data_node-replica | grep self | grep gid | grep ${i}$ | awk '{print $1}' | sed 's/...$//' > /home/ubuntu/tmp/datasha_num${i}.txt
		data_node=`cat /home/ubuntu/tmp/datasha_num${i}.txt | wc -l`
		for s in `seq 1 ${data_node}`
		do
			a=`sed -n "${s}p" /home/ubuntu/tmp/datasha_num${i}.txt`
			echo $a
			cat /home/ubuntu/tmp/a.txt | grep /ip | grep ${a} | awk '{print $2}' >> /home/ubuntu/tmp/data_shard${i}.txt
		done
	done

	#------------------------------------------------------------------
	sleep 1

	#--------将metadata信息生成到meta-datas.json--------
	#生成配置文件
	echo '[' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo '	{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo '	  "ip":"127.0.0.1",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo '	  "port":6001,' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo '	  "user":"pgx",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo '	  "password":"pgx_pwd"' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json

	for i in `seq 1 ${metare_num}`
	do
		echo '	},' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
		echo '	{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
		echo '	  "ip":"127.0.0.1",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
		echo '	  "port":6001,' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
		echo '	  "user":"pgx",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
		echo '	  "password":"pgx_pwd"' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	done
	echo '	}' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	echo ']' >> /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json


	#替换
	sed -i "0,/127.0.0.1/s/127.0.0.1/${meta_master}/" /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	for i in `seq 1 ${metare_num}`
	do	
		a=`sed -n "${i}p" /home/ubuntu/tmp/meta-replica.txt`
		sed -i "0,/127.0.0.1/s/127.0.0.1/${a}/" /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json
	done
	#--------------------------------------------------
	sleep 1
	#--------将datanode信息生成到data-shard.json--------
	#生成配置文件
	echo '[' >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
	for i in `seq 1 ${datasha_num}`
	do
		n=`cat /home/ubuntu/tmp/data_shard${i}.txt | wc -l`
		echo '{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "	\"shard_name\":\"shard${i}\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "	\"shard_nodes\":" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "	[" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "		{" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "		  \"ip\":\"127.0.0.1\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "		  \"port\":6001," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "		  \"user\":\"pgx\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "		  \"password\":\"pgx_pwd\"" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		for times_num in `seq 1 ${n}`
		do
			echo '		},' >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
			echo '		{' >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
			echo '		  "ip":"127.0.0.1",' >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
			echo "		  \"port\":6001," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
			echo "		  \"user\":\"pgx\"," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
			echo "		  \"password\":\"pgx_pwd\"" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		done
		echo "		}" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "	]" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		echo "}," >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
	done
	sed -i '$d' /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
	echo '}'  >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
	echo "]" >> /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json

	#替换node信息
	for i in `seq 1 ${datasha_num}`
	do	
		datamaster_ip=`cat /home/ubuntu/tmp/datashards_num.txt | sed -n "${i}p"`
		sed -i "0,/127.0.0.1/s/127.0.0.1/${datamaster_ip}/" /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		datashard_txt=`cat /home/ubuntu/tmp/data_shard${i}.txt | wc -l`
		for a in `seq 1 ${datashard_txt}`
		do
			datanode_ip=`cat /home/ubuntu/tmp/data_shard${i}.txt | sed -n "${a}p"`
			sed -i "0,/127.0.0.1/s/127.0.0.1/${datanode_ip}/" /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json
		done
	done
	#---------------------------------------------------
	sleep 330
	python2 /home/ubuntu/kunlun/kunlun-computing/scripts/bootstrap.py --config=/home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json --bootstrap_sql=/home/ubuntu/kunlun/kunlun-computing/scripts/meta_inuse.sql
	sleep 10
	python2 /home/ubuntu/kunlun/kunlun-computing/scripts/create_cluster.py --shards_config /home/ubuntu/kunlun/kunlun-computing/scripts/data-shard.json --comps_config /home/ubuntu/kunlun/kunlun-computing/scripts/comp-node.json --meta_config /home/ubuntu/kunlun/kunlun-computing/scripts/meta-datas.json --cluster_name clust1 --cluster_owner abc --cluster_biz test
else 
	echo replica-node,pass
fi
