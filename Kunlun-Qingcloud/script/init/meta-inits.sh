cd /home/ubuntu/kunlun/kunlun-storage/dba_tools/

a=`cat /etc/confd/confd.toml | grep nodes | awk '{print $3}' | sed 's/..//' | sed 's/..$//'` #获取metadata所在的ip

curl $a >> /home/ubuntu/a.txt #将metadata info全部放到a.txt里面

self_gid=`cat /home/ubuntu/a.txt | grep /self/host/gid | awk '{print $2}'` #获取本地节点所在的gid

self_ip=`cat /home/ubuntu/a.txt | grep /self/host/ip | awk '{print $2}'` #获取本地节点所在的ip地址

master_info=`cat /home/ubuntu/a.txt | grep /self/hosts/meta_data_node/ | grep gid | awk '{print $1}' | sed 's/...$//'` #获取本节点对应的主节点的前缀info

master_ip=`cat /home/ubuntu/a.txt | grep "$master_info" | grep /ip | awk '{print $2}'` #获取对应主节点的ip地址

sudo cp /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json1

sudo sed -i 's/6002/6001/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's/6003/6001/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's@/data@/home/ubuntu/kunlun/data/metadata@'  /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's@"innodb_log_dir_path":"/home/ubuntu/kunlun/data/metadata/log"@"innodb_log_dir_path":"/home/ubuntu/kunlun/data/metadata/innolog"@'  /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's/abc/ubuntu/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

if [ $self_ip != $master_ip ] ; then
	
	echo this is salve_node instance! wait 150s
	
	sleep 150

	sudo sed -i "0,/127.0.0.1/s/127.0.0.1/${master_ip}/" /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

        sudo sed -i "0,/127.0.0.1/s/127.0.0.1/${self_ip}/" /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

	sudo python2 /home/ubuntu/kunlun/kunlun-storage/dba_tools/install-mysql.py --config=/home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json --target_node_index=1

elif [ $self_ip = $master_ip ] ; then
	
	echo this is master_node instance
	
	sudo sed -i "0,/127.0.0.1/s/127.0.0.1/${master_ip}/" /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

        sudo python2 /home/ubuntu/kunlun/kunlun-storage/dba_tools/install-mysql.py --config=/home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json --target_node_index=0

fi
