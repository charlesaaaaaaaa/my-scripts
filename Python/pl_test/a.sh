test_home=/home/charles/daily_smoke/pl_test
conf_home=/home/charles/daily_smoke/config_variables
conn_str='psql postgres://abc:abc@192.168.0.132:59701/postgres -a '
ubuntu_conn_str='psql postgres://abc:abc@192.168.0.138:58881/postgres -a -f'
err_file=$test_home/err.txt

print_format(){
level=$1
txt=$2
txt_num=`echo $txt | wc -c`
txt_num=`echo $txt_num+3 | bc`

if [[ $level -eq 1 ]]
then
        split_str=`printf '%0.s#' $(seq 1 $txt_num); echo`
        txt=`printf "# $txt #"`
elif [[ $level -eq 2 ]]
then
        split_str=`printf '%0.s=' $(seq 1 $txt_num); echo`
        txt=`printf "= $txt ="`
elif [[ $level -eq 3 ]]
then
        split_str=`printf '%0.s+' $(seq 1 $txt_num); echo`
        txt=`printf "+ $txt +"`
fi
echo $split_str
echo $txt
echo $split_str
}

rewrite='bash $test_home/reout.sh'

# --------------------------------------------------------------------------------

print_format 1 plpython
plpython_home=$test_home/postgresql-11.21/src/pl/plpython
cd $plpython_home && rm -rf ./out ./diff ./err.txt
mkdir -p out diff
plpython_cases='plpython_schema plpython_call plpython_drop plpython_global plpython_newline plpython_populate plpython_unicode plpython_void'
for case in $plpython_cases
do
	cd $plpython_home
	$conn_str -c 'create extension plpython3u;' || echo 
	$conn_str -f ./sql/$case.sql > $plpython_home/out/$case.out
    $rewrite $plpython_home/out/$case.out
    diff $plpython_home/out/$case.out $plpython_home/expected/$case.out
    if [[ $? -ne 0 ]]
    then
    	echo $case >> $err_file
    fi
done

# --------------------------------------------------------------------------------

print_format 1 pllua


if [[ -n $err_file ]]
then
	print_format 1 测试失败
    print_format 2 以下是失败的cases
    cat $err_file
    exit 1
else
	print_format 1 测试成功
fi
