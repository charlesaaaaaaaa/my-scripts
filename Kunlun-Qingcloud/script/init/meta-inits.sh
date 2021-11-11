mkdir -p /home/ubuntu/tmp

cd /home/ubuntu/kunlun/kunlun-storage/dba_tools/

a=`cat /etc/confd/confd.toml | grep nodes | awk '{print $3}' | sed 's/..//' | sed 's/..$//'` #获取metadata所在的ip

curl $a >> /home/ubuntu/tmp/a.txt #将metadata info全部放到a.txt里面

self_gid=`cat /home/ubuntu/tmp/a.txt | grep /self/host/gid | awk '{print $2}'` #获取本地节点所在的gid

self_ip=`cat /home/ubuntu/tmp/a.txt | grep /self/host/ip | awk '{print $2}'` #获取本地节点所在的ip地址

master_info=`cat /home/ubuntu/tmp/a.txt | grep /self/hosts/meta_data_node/ | grep "$self_gid"$ | grep gid | awk '{print $1}' | sed 's/...$//'` #获取本节点对应的主节点的前缀info

master_ip=`cat /home/ubuntu/tmp/a.txt | grep "$master_info" | grep /ip | awk '{print $2}'` #获取对应主节点的ip地址

sudo cp /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json1

sudo sed -i 's/6002/6001/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's/6003/6001/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's@/data@/home/ubuntu/kunlun/data/data@'  /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's@"innodb_log_dir_path":"/home/ubuntu/kunlun/data/data/log"@"innodb_log_dir_path":"/home/ubuntu/kunlun/data/data/innolog"@'  /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

sudo sed -i 's/abc/ubuntu/' /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

cat /home/ubuntu/tmp/a.txt | grep gid | grep "$self_gid"$ | grep self/hosts/meta_data_node-re |awk '{print $1}' | sed 's/...$//' > /home/ubuntu/tmp/replica.txt

re_num=`cat /home/ubuntu/tmp/replica.txt | wc -l `

sudo sed -i "0,/127.0.0.1/s/127.0.0.1/${master_ip}/" /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

for i in `seq 1 $re_num`
do
        re_info=`sed -n "${i}p" /home/ubuntu/tmp/replica.txt`
	re_ip=`cat /home/ubuntu/tmp/a.txt | grep "$re_info" | grep /ip |  awk '{print $2}' `  		
	sudo sed -i "0,/127.0.0.1/s/127.0.0.1/${re_ip}/" /home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json

done

if [ $self_ip != $master_ip ] ; then
	
	echo this is salve_node instance! wait 150s
	
	sleep 160

	for i in `seq 1 $re_num`
        do	
		cur_info=`sed -n "${i}p" /home/ubuntu/tmp/replica.txt`
                cur_ip=`cat /home/ubuntu/tmp/a.txt | grep "$cur_info" | grep /ip |  awk '{print $2}'`
                if [ $cur_ip != $self_ip ] ; then
                        echo not node_$i

                elif [ $cur_ip = $self_ip ]; then
                        sudo python2 /home/ubuntu/kunlun/kunlun-storage/dba_tools/install-mysql.py --config=/home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json --target_node_index=${i}
                fi
        done

elif [ $self_ip = $master_ip ] ; then
	
	echo this is master_node instance
	
        sudo python2 /home/ubuntu/kunlun/kunlun-storage/dba_tools/install-mysql.py --config=/home/ubuntu/kunlun/kunlun-storage/dba_tools/mgr_config.json --target_node_index=0

fi
