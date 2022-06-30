ps -fe | grep sysbench | grep $1 | grep $2 | awk '{print $2}' > pid.log
