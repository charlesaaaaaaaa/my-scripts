rm -rf result
touch result

#for list in insert write_only read_write read_write_k update_index update_non_index
for list in $2
do
        echo "== ${list} == " >> result
        #for a in `seq 1 10`
	for la in $1
        do
                #la=`expr $a \* 500`
		#la=`expr $a \* 100`
                wcl=`cat ${list}/${la}_${list} | grep tps | wc -l`
                tpa=`cat ${list}/${la}_${list} | grep transactions | awk '{print $3}' | sed 's/^.//'`
                qps=`cat ${list}/${la}_${list} | grep queries: | awk '{print $3}' | sed 's/^.//'`
		txn=`cat ${list}/${la}_${list} | grep transactions: |  awk '{print $2}'`
		avg=`cat ${list}/${la}_${list} | grep avg: |  awk '{print $2}'`
                thp=`cat ${list}/${la}_${list} | grep 95th |  awk '{print $3}'`
                echo $la $tpa $qps $avg $thp >> result
        done
        echo >> result
done

sed -i 's/ / || /g' result && sed -i 's/^/|| kunlun || /' result
sed -i 's/$/ ||/' result
sed -i "1 i * `date`" result && sed -i "1 i [[PageOutline]]" result

#for i in insert write_only read_write read_write_k update_index update_non_index
for i in $2
do
	ai=`cat -n result | grep -w $i | awk '{print $1}'`
	sed -i "${ai}a || db || threads || tps || pqs || avg response time(ms) || .95 response time(ms) ||" result
done

sed -i 's/|| kunlun ||  ||/----/' result && sed -i 's/|| kunlun || == || /=== /' result
sed -i 's/ || == ||  ||//' result && cat result

