#ed -i 's///' par.sh
mkdir -p result
touch results

#for i in 2 4 5 6 7 8 9 10
for i in `seq 6 10`
do
	threads=`echo "$i*100" | bc -l`
	sed -i '/thread/d' par.sh
	echo "thread=$threads" >> par.sh
	./run.sh 1 > ./result/${threads}
	echo $threads
	sleep 10
	check=`cat ./result/${threads} | grep 'total number of events:'`
	n=2
	while [[ "$check" -eq "" ]]
	do
		bash del.sh 192.168.0.125 8888
		./run.sh 1 > ./result/${threads}
		echo "\n========>> run $threads threads $n times <<========"
		check=`cat ./result/${threads} | grep 'total number of events:'`
		cat ./result/${threads} | grep 'tps:' | sed -n '$p'
		cat ./result/${threads} | grep failed
		echo "========>> run $threads threads $n times <<========\n"
		n=`echo "$n+1" | bc -l`
		sleep 10
	done
done

> results

echo '|| threads || tps(avg) || read || write || txn || avg response time(ms) || .95 response time(ms) || total events ||' > results

for i in `seq 100 100 1000`
do
	wcl=`cat result/$i | grep tps | wc -l`
        tps=`cat result/$i | awk '{print $7}' | awk '{sum+=$1}END{printf "%.2f",sum}'`
        tpa=`echo "scale=2;${tps}/${wcl}" | bc -l`
        rea=`cat result/$i | grep read: | awk '{print $2}'`
        wri=`cat result/$i | grep write: | awk '{print $2}'`
        txn=`cat result/$i | grep transactions: |  awk '{print $2}'`
        avg=`cat result/$i | grep avg: |  awk '{print $2}'`
        thp=`cat result/$i | grep 95th |  awk '{print $3}'`
        toe=`cat result/$i | grep 'events (avg/stddev):' | awk '{print $3}'`
        echo '||' $i  '||' $tpa '||' $rea '||' $wri '||' $txn '||' $avg '||' $thp '||' $toe '||' >> results
done 
