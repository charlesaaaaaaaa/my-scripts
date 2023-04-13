num=0
for i in $*
do
	if [[ num -eq 0 ]]
	then
		user=$i
		num=`echo "$num+1" | bc -l`
	else
		ssh $user@$i 'free | grep Mem' | awk '{print $4}' >> tmpnum.txt
	fi
done
big=`cat tmpnum.txt | sort -n | tail -1`
small=`cat tmpnum.txt | sort -n | head -1`
div=`echo "scale=2;$small/$big*100" | bc -l`
res=`echo "100-$div" | bc -l`
echo $res | awk -F. '{print $1}'
rm tmpnum.txt
