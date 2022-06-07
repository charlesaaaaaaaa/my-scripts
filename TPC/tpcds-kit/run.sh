host=${1:-'192.168.0.113'} #default host

port=${2:-'8881'} #default port

db=${3:-'test'} #default 

total_cost=0
for i in {1..99}
do
        echo "begin run Q${i}, query/q$i.sql , `date`"
        begin_time=`date +%s.%N`
        psql -h ${host} -p ${port} -d ${db}  -f query/q${i}.sql > ./log/log_q${i}.out
        rc=$?
        end_time=`date +%s.%N`
        cost=`echo "$end_time-$begin_time"|bc`
        total_cost=`echo "$total_cost+$cost"|bc`
        if [ $rc -ne 0 ] ; then
              printf "run Q%s fail, cost: %.2f, totalCost: %.2f, `date`\n" $i $cost $total_cost
         else
              printf "run Q%s succ, cost: %.2f, totalCost: %.2f, `date`\n" $i $cost $total_cost
         fi
done
