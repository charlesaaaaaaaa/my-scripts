rm tb.txt tb_ntb.txt
for i in $(ls | grep tbl) #把每个生成数据文件每行的最后一个 ｜ 给删除掉
do
        sed -i 's/|$//' $i

done

rm -rf table
mkdir table

echo `ls -l | grep tbl | awk '{print $9}'` >> tbn.txt
cp tbn.txt tbn_ntb.txt
sed -i 's/.tbl//g' tbn_ntb.txt

for sp in `seq 1 9`
do
	awk "{print \$${sp}}" tbn.txt >> tb.txt
	awk "{print \$${sp}}" tbn_ntb.txt >> tb_ntb.txt
done

rm tbn.txt tbn_ntb.txt

sed -i '$d' tb.txt
sed -i '$d' tb_ntb.txt

for spl in `seq 1 8`
do
	
	tbns=`sed -n ${spl}p tb.txt`      #获取文件名
	tbnns=`sed -n ${spl}p tb_ntb.txt` #获取文件名前缀
	echo spliting ${tbns}, please wait......
	split -l 1600000 -d ${tbns} ${tbnns} #以每1600000行来分割文件，前缀为文件名的前缀
	mv ${tbnns}* ./table/
done	

rm tb.txt tb_ntb.txt
rm ./table/*tbl #删除原文件
