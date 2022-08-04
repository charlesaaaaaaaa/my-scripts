mkdir -p fail 
mkdir -p pass

for i in `cat ../fail | sort | uniq`
do
	echo $i
	../mtr  --force  --parallel=4 --suite-timeout=3000  --max-test-fail=10000 --mysqld="--ddc_mode=0" --mysqld="--print_extra_info_verbosity=0"  --testcase-timeout=300 --mysqld="--enable-fullsync=0" ${i} >> $i 2>&1 
	line=`cat $i | wc -l`
	if [[ ${line} -lt 50 ]]
	then
		mv $i pass
	else
		mkdir -p fail/$i 
		mv $i fail/$i
		mv ../var fail/$i
		tar -zcf fail/$i.tgz fail/$i
		rm -rf fail/$i
	fi
done
