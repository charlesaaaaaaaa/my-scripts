rm -rf check.yaml
threadNum=1
for i in $1
do
	threadNum=`echo "$threadNum+1" | bc -l`
done

for a in $2
do
	for i in $1
        do

    		b=`cat result | grep -w -A $threadNum "=== $a" | grep "|| $i ||" | awk '{print $10}' | sed 's/...$//'`
                if [[ "$b" -eq "" ]]; then
			echo $a: $i >> check.yaml
                fi
        done
done

if [[ -e "check.yaml" ]]
then
	for i in $1
	do
		rerunTest=`cat check.yaml | grep $i | sort | uniq`
		if [[ -n $rerunTest ]]
		then
			cat check.yaml | grep $i | sort | uniq >> ../${i}check.yaml
		fi
	done
fi
