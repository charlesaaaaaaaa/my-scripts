rm copy.sql copy.txt

echo customer >> copy.txt
echo lineitem >> copy.txt
echo nation   >> copy.txt
echo orders   >> copy.txt
echo partsupp >> copy.txt
echo part     >> copy.txt
echo region   >> copy.txt
echo supplier >> copy.txt

#for copy in $(ls | grep tbl) #开始copy数据
#do
#	echo ${copy} >> copy.txt
#done

#sed -i 's/.tbl//' copy.txt



for a in `seq 1 9`
do
	ab=`sed -n ${a}p copy.txt`
	echo "delete from ${ab} ;" >> copy.sql
	for i in ${ab}
	do
		for ia in $(ls ./table | grep ${ab})
		do
			echo "\\copy ${ab} from './table/${ia}' with(delimiter '|', null '');" >> copy.sql
		done
	done
done

sed -i "/part from '\.\/table\/partsupp*/d" copy.sql
sed -i '$d' copy.sql
#echo "delete from ${ab} ;" >> copy.sql
psql -h $1 -p $2 -d $3 -U $4 -f ./copy.sql

#rm copy.sql copy.txt
