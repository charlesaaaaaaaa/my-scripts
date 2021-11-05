/home/ubuntu/kunlun/kunlun-storage/dba_tools

if [ $1 = start ] ; then
	su ubuntu -c "/home/ubuntu/kunlun/kunlun-storage/dba_tools/startmysql.sh 6001"

elif [ $1 = stop ] ; then 
	su ubuntu -c "/home/ubuntu/kunlun/kunlun-storage/dba_tools/stopmysql.sh 6001"

elif [ $1 = 
