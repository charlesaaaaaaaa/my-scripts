dir=${1:-.}
first_row=0
for casedir in `ls $dir | grep oltp`
do
	case_res=()
	now_tag=0
	files=`ls -v $dir/$casedir`
	for threadOutput in $files
	do
		res=`cat $dir/$casedir/$threadOutput | grep transactions | awk -F'(' '{print \$2}' | awk '{print \$1}'`
		case_res[$now_tag]=$res
		now_tag=$((now_tag+1))
	done
	if [[ $first_row -eq 0 ]]
	then
		files=`echo $files | sed 's/ / || /g'`
		echo "|| case || $files ||"
		first_row=1
	fi
	case_result=`echo "${case_res[*]}"| sed 's/ / || /g'`
	case_result=`echo "|| $casedir || $case_result ||"`
	echo $case_result
done
