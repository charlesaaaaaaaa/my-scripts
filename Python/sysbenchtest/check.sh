for a in $2
do
	for i in $1
                #for i in 500 1000 1500
        do

    		b=`cat result | grep -A 5 "=== $a" | grep "|| $i ||" | awk '{print $10}' | sed 's/...$//'`
                if [[ "$b" -eq 0 ]]; then
			echo $a: $i >> check.yaml
                fi
        done
done

if [[ -e "check.yaml" ]]
then
	for i in $1
	do
		cat check.yaml | grep $i | sort | uniq >> ../${i}check.yaml
	done
fi
