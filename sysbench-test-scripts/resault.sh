#
echo `date` > resault
for list in point_select delete insert read_only read_write write_only update_index update_non_index
do	
	echo "== ${list} == "	
	for a in `seq 1 $i` 
	do
		$la=`expr $a \* 100`
		rea=`cat ${list}/${la}_${list} | grep read: | awk '{print $2}'`
		wri=`cat ${list}/${la}_${list} | grep write: | awk '{print $2}'`
		txn=`cat ${list}/${la}_${list} | grep transactions: |  awk '{print $2}'`
		avg=`cat ${list}/${la}_${list} | grep avg: |  awk '{print $2}'`
		thp=`cat ${list}/${la}_${list} | grep 95th |  awk '{print $3}'`
		toe=`cat ${list}/${la}_${list} | grep 'events (avg/stddev):' | awk '{print $3}'`
		echo $la $rea $wri $txn $avg $thp $toe >> resault
	done
	echo
done

sed -i 's/ / || /g' resault
sed -i 's/^/|| kunlun || /' resault
sed -i 's/$/ ||/' resault
sed -i '/^/i\|| db || threads || read || wirte || txn || total || avg response time(ms) || .95 response time(ms) || total events ||' resault
