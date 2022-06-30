for a in write_only insert point_select point_select_k read_only read_only_k read_write read_write_k update_index update_non_index
do
	for i in $1
                #for i in 500 1000 1500
        do

    		b=`cat result | grep -A 5 "=== $a" | grep "|| $i ||" | awk '{print $10}' | sed 's/...$//'`
                if [[ "$b" -eq '' ]]; then
			echo $a: $i >> check.yaml
                fi
        done
done

cat check.yaml | sort | uniq > check.yaml

for i in $1
do
	cat check.yaml | sort | uniq > ${i}check.yaml
done
