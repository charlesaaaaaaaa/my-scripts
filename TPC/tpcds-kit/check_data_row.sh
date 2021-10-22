

find ./tools/ -name '*dat' >> a.txt ; 
for i in `seq 1 26` 
do 
	b=`sed -n "${i}p" a.txt` 
       	cat ${b} | wc -l >> b.txt
done 

cat b.txt; 

d=`sed -n '1p' b.txt`

for n in b.txt
do
	echo ${n}
done
rm a.txt b.txt
