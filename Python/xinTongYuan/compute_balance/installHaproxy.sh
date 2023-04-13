rm -rf haproxy*
killall haproxy > /dev/null 2>&1
wget http://zettatech.tpddns.cn:14000/thirdparty/cloud/haproxy.tgz
tar -zxf haproxy.tgz
rm -rf haproxy.tgz
for i in `seq 1 4`; do sed -i '$d' haproxy/conf/haproxy.cnf; done
num=0
for i in $*
do
	if [[ num -eq 0 ]]
	then
		echo "        bind $i" >> haproxy/conf/haproxy.cnf
		num=`echo "$num+1" | bc -l`
	else
		echo "        server server$num $i" >> haproxy/conf/haproxy.cnf
		num=`echo "$num+1" | bc -l`
	fi
done
cd haproxy
bash restart.sh
