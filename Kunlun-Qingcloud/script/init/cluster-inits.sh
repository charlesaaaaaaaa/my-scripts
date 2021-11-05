a=`cat /etc/confd/confd.toml | grep nodes | awk '{print $3}' | sed 's/..//' | sed 's/..$//'`

curl $a >> /home/ubuntu/a.txt

meta_ip=`cat /home/ubuntu/a.txt | grep /self/hosts/meta_data_node/ | grep /ip | awk '{print $2}'`

sed -i 's/4321/6001/' /home/ubuntu/kunlun/cluster_mgr_rel/resources/cluster_mgr.cnf

sed -i "s/127.0.0.1/${meta_ip}/" /home/ubuntu/kunlun/cluster_mgr_rel/resources/cluster_mgr.cnf

sed -i 's/user = abc/user = pgx/' /home/ubuntu/kunlun/cluster_mgr_rel/resources/cluster_mgr.cnf

sed -i 's/pwd = abc/pwd = pgx_pwd/' /home/ubuntu/kunlun/cluster_mgr_rel/resources/cluster_mgr.cnf

/home/ubuntu/kunlun/cluster_mgr_rel/bin/cluster_mgr /home/ubuntu/kunlun/cluster_mgr_rel/resources/cluster_mgr.cnf &
