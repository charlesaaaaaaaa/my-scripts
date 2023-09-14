if [[ $# -eq 0 ]]
then
        cat << EOF
该脚本是用来读取多个目录下的result文件的内容，对比tps结果及pqs结果
确保目录下一级里要有result文件
其中测试的case和线程要在该脚本里面改
使用方法：
        bash show.sh comp1 comp2 ......
EOF
exit 0
fi

test='point_select write_only read_only read_write insert update_index'
threads='1 8 16 32 64 128'

echo '[[PageOutline]]'
for i in $test
do
        echo ===$i
        title_tps=`echo $* | sed 's/ /-tps || /g'`
        title_tps=`echo ${title_tps}-tps`
        title_pqs=`echo $* | sed 's/ /-pqs || /g'`
        title_pqs=`echo ${title_pqs}-pqs`
        echo "|| thread || $title_tps || $title_pqs ||"
        for t in $threads
        do
                rows=`echo "|| $t"`
                for tt in $*
                do
                        res=`cat $tt/result | grep -A 7 -w $i | grep -w " $t " | awk '{print $6}'`
                        rows=`echo "$rows || $res"`
                done
                for tq in $*
                do
                        res=`cat $tq/result | grep -A 7 -w $i | grep -w " $t " | awk '{print $8}'`
                        rows=`echo "$rows || $res"`
                done
                echo "$rows ||"
        done
done

