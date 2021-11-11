source /etc/profile

cd python2 /home/ubuntu/kunlun/kunlun-computing/scripts

comp_path=`ps -ef |  grep 'postgres -D' | grep home | awk '{print $10}'`

if [ $1 = start ] ; then

	su ubuntu -c "python2 /home/ubuntu/kunlun/kunlun-computing/scripts/start_pg.py port = 5401"

elif [ $1 = stop ] ; then
	su ubuntu -c "/home/ubuntu/kunlun/kunlun-computing/bin/pg_ctl stop -D ${comp_path}"

elif [ $1 = restart ] ; then 
	su ubuntu -c "/home/ubuntu/kunlun/kunlun-computing/bin/pg_ctl restart -D ${comp_path}"

elif [ $1 = destory ] ; then
        su ubuntu -c "/home/ubuntu/kunlun/kunlun-computing/bin/pg_ctl kill 5401"
else ;
	echo please add parameter 'start' 'restart' 'stop' 'destory' 'upgrade' !
fi
