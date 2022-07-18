pids=`ps -fe | grep sysbench | grep $1 | grep $2 | awk '{print $2}' | wc -l`

if [ "$pids" -ne 0 ]
then
	ps -fe | grep sysbench | grep $1 | grep $2 | awk '{print $2}' > pid.log
else
	rm -rf pid.log
fi
