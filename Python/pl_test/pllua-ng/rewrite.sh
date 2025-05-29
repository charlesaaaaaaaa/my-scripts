src_file=$1
rows=`cat ${src_file} -n | grep 'psql:' | awk '{print $1}'`
# =`sed -n '20p' a.txt | awk '{$1=""; print $0}'`
for i in $rows
do
	ins=`sed -n "${i}p" $src_file | awk '{$1=""; print $0}' | sed 's/:/: /'`
	sed -i "${i}d" $src_file
	sed -i "${i}i $ins" $src_file
done
