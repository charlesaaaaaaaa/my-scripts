if [ $# -lt 7 ] ; then
       echo	
       echo get me 7 parameters,runing like	
	echo ./run.sh host port dbname user table_num table_size test_runtime       
	echo 'nohup /bin/bash `pwd`/prepare.sh 192.168.0.132 8881 postgres abc 10 10000000 120 > prepare.log 2>&1 &'
	echo
	exit 1
fi

date

sysbench oltp_point_select        \
      --tables=$5                   \
      --table-size=$6           \
      --db-driver=pgsql             \
      --pgsql-host=$1        \
      --pgsql-port=$2             \
      --pgsql-user=$4         \
      --pgsql-password=abc \
      --pgsql-db=$3           \
      prepare

date

#for i in point_select point_select_k insert write_only read_only read_only_k read_write read_write_k update_index update_non_index
#do
	# create test result dir
#	if [ ! -d $i ] ; then
#		mkdir $i 
#	fi
#done

#sysbench oltp_delete --tables=10 --table-size=10000000 --db-driver=pgsql --pgsql-host=192.168.0.132 --pgsql-port=8881 --pgsql-user=abc --pgsql-db=postgres --pgsql-password=abc cleanup
