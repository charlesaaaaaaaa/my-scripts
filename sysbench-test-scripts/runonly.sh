if [ $# -lt 7 ] ; then
       echo	
       echo get me 7 parameters,runing like	
	echo ./run.sh host port dbname user table_num table_size test_runtime       
	echo 'nohup /bin/bash `pwd`/runonly.sh 192.168.0.125 26252 postgres yugabyte 10 10000000 120 > log.log 2>&1 &'
	echo
	exit 1
fi



#for i in 9
for i in `seq 1 10` # run sysbench test 100 to 1000 threads
do
	li=` expr ${i} \* 100 `
	echo
	echo run threads ${li}
	echo
	./test.sh $1 $2 $3 $4 $li $5 $6 $7 
	# like : ./loop_test.sh 192.168.0.134 38701 postgres abc  10        100000     120
	#        ./loop_test.sh host          port  dbname   user table_num table_size test_time
done

bash ./resault.sh 
cp resault result_before

for n in `seq 1 5`
do
        for a in point_select write_only insert update_index update_non_index
        do
                for i in 100 200 300 400 500 600 700 800 900 1000
                do

                        b=`cat resault | grep -A 11 "=== $a" | grep "|| $i ||" | awk '{print $16}' | sed 's/...$//'`
                        if [[ "$b" -eq '' ]]; then
                                echo
                                date
                                echo "rerun ${a}:${i}"
                                sysbench oltp_${a} --tables=$5 --table-size=$6 --db-ps-mode=disable --db-driver=pgsql --pgsql-host=$1 --report-interval=10 --pgsql-port=$2 --pgsql-user=$4 --pgsql-password=abc --pgsql-db=$3 --threads=${i} --time=$7 --rand-type=uniform run > ./${a}/${i}_${a} 2>&1
                        sleep 5
                        else
                                echo > /dev/null
                        fi
                done
        done
        bash ./resault.sh
done

bash ./resault.sh

#sysbench oltp_delete --tables=10 --table-size=100000 --db-driver=pgsql --pgsql-host=192.168.0.134 --pgsql-port=38701 --pgsql-user=abc --pgsql-db=postgres --pgsql-password=abc cleanup
