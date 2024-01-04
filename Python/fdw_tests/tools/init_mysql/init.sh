host=${1:-192.168.0.136}
port=${2:-12388}
user=${3:-root}
pwds=${4:-root}
echo now init mysql://$user:$pwds/$host:$port ...
source ./env.sh $host $port $user $pwds
for i in mysql_fdw_regress1 mysql_fdw_regress2 mysql_fdw_regress
do 
	mysql -u$user -p$pwds -P$port -h$host -e "drop database if exists $i" > /dev/null 2>&1 
	mysql -u$user -p$pwds -P$port -h$host -e "create database if not exists $i" > /dev/null 2>&1
done
bash mysql_init.sh
