if [ $# -lt 7 ] ; then
       echo	
       echo get me 7 parameters,runing like	
	echo ./run.sh host port dbname user table_num table_size test_runtime       
	echo ./run.sh 192.168.0.134 38701 postgres abc 10 100000 120
	echo
	exit 1
fi



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


for i in point_select delete insert read_only read_write write_only update_index update_non_index
do
	# create test resault dir
	if [ ! -d $i ] ; then
		mkdir $i 
	fi
done

for i in `seq 4 10` # run sysbench test 100 to 1000 threads
do
	li=` expr ${i} \* 100 `
	echo
	echo run threads ${li}
	echo
	./test.sh $1 $2 $3 $4 $li $5 $6 $7 
	# like : ./run.sh 192.168.0.134 38701 postgres abc  10        100000     120
	#        ./run.sh host          port  dbname   user table_num table_size test_time
done

sysbench oltp_delete        \
      --tables=$5                   \
      --table-size=$6           \
      --db-driver=pgsql             \
      --pgsql-host=$1        \
      --pgsql-port=$2             \
      --pgsql-user=$4         \
      --pgsql-password=abc \
      --pgsql-db=$3           \
      cleanup


bash ./resault.sh
