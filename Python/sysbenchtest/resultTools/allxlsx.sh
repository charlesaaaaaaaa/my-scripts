CP=`pwd`
for i in `ls | grep -v allxlsx.sh`
do
	cat $CP/$i/* | grep -v '$i.res' > $CP/$i/$i.res
done	

for i in `ls | grep -v allxlsx.sh`
do
	echo $i
	cat $i/$i.res
	echo
done

