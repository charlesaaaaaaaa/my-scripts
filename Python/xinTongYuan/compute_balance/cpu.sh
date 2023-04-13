num=0
for i in $*
do
	if [[ num -eq 0 ]]
	then
		user=$i
		num=`echo "$num+1" | bc -l`
	else
		ssh $user@$i 'iostat -c | grep -A 1 avg-cpu' | awk '{print $6}' | tail -1 >> tmpcpu.txt
	fi
done
big=`cat tmpcpu.txt | sort -n | tail -1`
small=`cat tmpcpu.txt | sort -n | head -1`
div=`echo "scale=2;$small/$big*100" | bc -l`
res=`echo "100-$div" | bc -l`
echo $res | awk -F. '{print $1}'
rm tmpcpu.txt
