klustron_output=$1
expected_output=$2
diff $klustron_output $expected_output > tmp.out
for i in `cat tmp.out | grep '\-\-\-' | grep '|'`
do
	echo $i
done
