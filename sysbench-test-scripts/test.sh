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

echo
echo testing oltp_point_select

sysbench oltp_point_select        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      prepare
echo
echo testing... please wait ${tim}s

sysbench oltp_point_select        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc  \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./point_select/${threads}_point_select 2>&1

echo
echo wait 5s
sleep 5
echo testing oltp_read_only 
echo
echo testing... please wait ${tim}s

sysbench oltp_read_only        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run> ./read_only/${threads}_read_only 2>&1
echo
echo wait 5s
sleep 5
echo testing oltp_read_write
echo
echo testing... please wait ${tim}s

sysbench oltp_read_write        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./read_write/${threads}_read_write 2>&1
echo wait 5s
sleep 5
echo testing oltp_write_only    
echo
echo testing... please wait ${tim}s

sysbench oltp_write_only        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --rand-type=uniform           \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./write_only/${threads}_write_only 2>&1
echo wait 5s
sleep 5
echo testing oltp_insert
echo

echo testing... please wait ${tim}s

sysbench oltp_insert        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --rand-type=uniform      \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./insert/${threads}_insert 2>&1
echo
echo wait 5s
sleep 5
echo testing oltp_update_index
echo
echo testing... please wait ${tim}s

sysbench oltp_update_index        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./update_index/${threads}_update_index 2>&1
echo
echo wait 5s
sleep 5
echo testing oltp_update_non_index
echo
echo testing... please wait ${tim}s

sysbench oltp_update_non_index        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./update_non_index/${threads}_update_non_index 2>&1
echo
sleep 10

echo
echo wait 5s
sleep 5
echo testing oltp_delete
echo
sysbench oltp_delete        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --report-interval=10 \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      --threads=${threads}                  \
      --time=${tim}                    \
      --rand-type=uniform \
      run > ./delete/${threads}_delete 2>&1
echo
sleep 10

sysbench oltp_delete        \
      --tables=${table}                   \
      --table-size=${tb_size}           \
      --db-driver=pgsql             \
      --pgsql-host=${host}        \
      --pgsql-port=${port}             \
      --pgsql-user=${user}         \
      --pgsql-password=abc \
      --pgsql-db=${db}           \
      cleanup

