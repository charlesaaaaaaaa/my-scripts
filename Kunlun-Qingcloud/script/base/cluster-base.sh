cd /home/ubuntu/kunlun/cluster_mgr_rel/

if [ $1 = start ] ; then
	
	su ubuntu -c "bash -x bin/cluster_mgr_safe --debug --pidfile=run.pid resources/clustermgr.cnf >& run.log </dev/null &"

elif [ $1 = stop ] ; then 

	su ubuntu -c "bash -x bin/cluster_mgr_safe --debug --pidfile=run.pid --stop"
else
	
	echo "please add parameter start or stop"

fi
