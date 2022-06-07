formats(){
echo ==========================
echo finding error with $1 ...
echo ==========================
}

# cpu
rm ./check/cpuerr.sh
touch ./check/cpuerr.sh
formats CPU
for cpu in `ls check/cpu`
do
	echo ">> check $cpu"
	for i in `cat check/cpu/$cpu | grep -v '%idle' | awk '{print $13}'`
	do
		val=`echo $i | sed 's/...$//'`
		dup=`cat ./check/cpuerr.sh | grep $i`
		if [ "$dup" ]
		then
			echo > /dev/null

		elif [ "$val" -le "70" ]
		then
			echo >> ./check/cpuerr.sh
			echo '             CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle' >> ./check/cpuerr.sh
			err=`cat check/cpu/$cpu | grep $i`
		       	echo "$cpu: $err">> ./check/cpuerr.sh
		fi
	done
done

#scale 1 GiB = 1048576 Kib
