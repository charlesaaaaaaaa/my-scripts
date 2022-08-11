for i in point_select point_select_k insert write_only read_only read_only_k read_write read_write_k update_index update_non_index
do
	for a in 300 600 900
	do
		db=`cat allresult.txt | grep -wA 5 $i | grep $a | awk '{print $2}'`
		export tps$a=`cat allresult.txt | grep -wA 5 $i | grep $a | awk '{print $6}'`
	done
	echo $db, $tps300, $tps600, $tps900 > $1/$i/$db.txt
done
