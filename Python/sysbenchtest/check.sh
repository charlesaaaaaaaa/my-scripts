rm -rf check.yaml
for a in $2
do
	for i in $1
        do

    		b=`cat result | grep -w -A 5 "=== $a" | grep "|| $i ||" | awk '{print $10}' | sed 's/...$//'`
                if [[ "$b" -eq "" ]]; then
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
