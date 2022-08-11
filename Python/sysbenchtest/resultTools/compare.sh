rm -rf allcompare.res && touch allcompare.res
echo '[[PageOutline]]' >> allcompare.res
for loadwork in point_select point_select_k insert write_only read_only read_only_k read_write read_write_k update_index update_non_index
do
	echo "== ${loadwork}" >> allcompare.res
	for thread in 300 600 900
	do
		cat $1/allresult.txt | grep -w -A 5 $loadwork | grep -w tps >> allcompare.res
		#cat $1/allresult.txt | grep -w -A 5 $loadwork | grep -w tps
		for db in $*
		do
			ctext=`cat $db/allresult.txt | grep -w -A 5 $loadwork | grep -w $thread`
			#cat $db/allresult.txt | grep -w -A 5 $loadwork | grep -w $thread
			echo $ctext >> allcompare.res
		done
		echo ---- >> allcompare.res
	done
done
cat allcompare.res
