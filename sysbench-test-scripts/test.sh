echo ================ parameters ================
host=${1:-'192.168.0.134'} #default host
echo host = ${host}

port=${2:-'38701'} #default port
echo port = ${port}

db=${3:-'postgres'} #default dbname
echo dbname = ${db}

user=${4:-'abc'} #default user
echo user = ${user}

threads=${5:-'100'} #default pwd
echo thread =  ${threads}

table=${6:-'10'} #default table num
echo table num = ${table}

tb_size=${7:-'100000'} #default warehouse num
echo table_size = ${tb_size}

tim=${8:-'120'} #default threads
echo times = ${tim}
echo ================ parameters ================
echo 

#sysbench oltp_point_select        \
#      --tables=${table}                   \
#      --table-size=${tb_size}           \
#      --db-driver=pgsql             \
#      --pgsql-host=${host}        \
#      --pgsql-port=${port}             \
#      --pgsql-user=${user}         \
#      --pgsql-password=abc \
#      --pgsql-db=${db}           \
#      prepare

for i in point_select insert write_only read_only read_write update_index update_non_index
do
	echo testing ${i} ... please wait ${tim}s
	echo oltp_${i}
	sysbench oltp_${i} --tables=${table} --table-size=${tb_size} --db-driver=pgsql --pgsql-host=${host} --report-interval=10 --pgsql-port=${port} --pgsql-user=${user} --pgsql-password=abc --pgsql-db=${db} --threads=${threads} --time=${tim} --rand-type=uniform run > ./${i}/${threads}_${i} 2>&1
	echo test done, waiting 5s
done

#sysbench oltp_delete        \
#      --tables=${table}                   \
#      --table-size=${tb_size}           \
#      --db-driver=pgsql             \
#      --pgsql-host=${host}        \
#      --pgsql-port=${port}             \
#      --pgsql-user=${user}         \
#      --pgsql-password=abc \
#      --pgsql-db=${db}           \
#      cleanup

