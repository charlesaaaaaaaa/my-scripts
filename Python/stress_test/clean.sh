hosts='192.168.0.19 192.168.0.20 192.168.0.21'
ports='56661 56663'
user='kunlun'
logdir='/nvme2/compare/base/storage_logdir'
left_files=10
clean_file_name='a.sh'
printf "======== infos ========\nhosts=$hosts\nports=$ports\nuser=$user\nlogdir=$logdir\nleft_files=$left_files\nclean_file_name=$clean_file_name\n======== infos ========\n"
cat << EOF > $clean_file_name
num=\`ls | grep -v $clean_file_name | wc -l\`
if [ \$num -gt $left_files ]
then
        delete_num=\`echo "\$num-$left_files" | bc\`
        file_names=\`ls | head -\$delete_num | grep -v $clean_file_name\`
        rm \$file_names
fi
EOF

printf "\n======== copy tmp file ========\n"
for host in $hosts
do
	for port in $ports
	do
		echo scp $clean_file_name to $host:$port
		scp ./$clean_file_name $user@$host:$logdir/$port/binlog
	done
done
printf "======== copy tmp file ========\n"
rm $clean_file_name

while true
do
	printf "\n======== clean binlog files ======\n"
	for host in $hosts
	do
        	for port in $ports
        	do
			echo "clean $user@$host:$port ......"
			ssh $user@$host "cd $logdir/$port/binlog && bash $clean_file_name"
		done
	done
	printf "======== clean binlog files ======\n"
	sleep 3600
done
