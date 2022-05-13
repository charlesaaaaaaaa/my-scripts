#
rm -rf result
touch result

for list in point_select insert read_only read_write write_only update_index update_non_index
do
        echo "== ${list} == " >> result
        for a in `seq 1 10`
        do
                la=`expr $a \* 100`
                wcl=`cat ${list}/${la}_${list} | grep tps | wc -l`
                tps=`cat ${list}/${la}_${list} | awk '{print $7}' | awk '{sum+=$1}END{printf "%.2f", sum}'`
                tpa=`echo "scale=2;${tps}/${wcl}" | bc -l`
                rea=`cat ${list}/${la}_${list} | grep read: | awk '{print $2}'`
                wri=`cat ${list}/${la}_${list} | grep write: | awk '{print $2}'`
                txn=`cat ${list}/${la}_${list} | grep transactions: |  awk '{print $2}'`
                avg=`cat ${list}/${la}_${list} | grep avg: |  awk '{print $2}'`
                thp=`cat ${list}/${la}_${list} | grep 95th |  awk '{print $3}'`
                toe=`cat ${list}/${la}_${list} | grep 'events (avg/stddev):' | awk '{print $3}'`
                echo $la $tpa $rea $wri $txn $avg $thp $toe >> result
        done
        echo >> result
done

sed -i 's/ / || /g' result
sed -i 's/^/|| kunlun || /' result
sed -i 's/$/ ||/' result
#sed -i '1 i\|| db || threads || tps(avg) || read || wirte || txn || total || avg response time(ms) || .95 response time(ms) || total events ||' result
sed -i "1 i * `date`" result
sed -i "1 i [[PageOutline]]" result

for i in `seq 0 6`
do
        ei=`expr ${i} \* 13 + 4`
        ai=`expr ${i} \* 13 + 4 `
        sed -i "$ai i\|| db || threads || tps(avg) || read || wirte || txn || avg response time(ms) || .95 response time(ms) || total events ||" result
        #sed -i "$ei s/||//g" result
        sed -i "$ei s/kunlun//g" result
done
sed -i 's/|| kunlun ||  ||/----/' result
sed -i 's/|| kunlun || == || /=== /' result
sed -i 's/ || == ||  ||//' result

cat result

