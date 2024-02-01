for i in dml select limit_offset_pushdown connection_validation aggregate_pushdown pushdown server_options join_pushdown 
do 
	printf "\n--------\n========########\ntesting $i.sql ...\n########========\n--------\n"
    cd tools/init_mysql/
    bash init.sh 192.168.0.136 12388 root root
    cd ../..
    echo 以下输出有错误并不一定是错误，因为官方预期文件里就有一堆错误。主要是看diff那些select语句的结果有没有和预期文件不一样的
    python3 ./fdw_test.py --config conf/config.conf --dbtype mysql --sqlfile sql/mysql/$i.sql > out/mysql/$i.out 2>&1
    cat out/mysql/$i.out
done
echo 开始检查。。。
for i in dml limit_offset_pushdown connection_validation aggregate_pushdown pushdown join_pushdown 
do
	python3 diff.py --expected expected/mysql/$i.out --output out/mysql/$i.out
done
err_count=`cat err.diff | wc -l`
if [ $err_count -gt 0 ]
then 
	echo ！！！本次测试失败！！！
	echo 更详细的错误输出在 126 的 ' /home/charles/daily_smoke/fdw_tests/err.diff ' 下
	exit 1
fi
