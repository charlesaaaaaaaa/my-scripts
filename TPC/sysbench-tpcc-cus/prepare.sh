sudo rm -rf /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
host=${1:-'192.168.0.132'} #defult host
echo host=${host} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
port=${2:-'5401'} #defult port
echo port=${port} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
db=${3:-'t5'} #defult dbname
echo db=${db} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
user=${4:-'abc'} #defult user
echo user=${user} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
pwds=${5:-'abc'} #defult pwd
echo pwds=${pwds} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
table=${6:-'2'} #defult table num
echo table=${table} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
wh=${7:-'2'} #defult warehouse num
echo wh=${wh} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
thread=${8:-'1'} #defult threads
echo thread=${thread} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
time=${9:-'15'} #defult times
echo time=${time} >> /home/charles/MyTools/Packages/sysbench-tpcc-cus/par.sh
/home/charles/MyTools/Packages/sysbench-tpcc-cus/tpcc.lua --pgsql-host=$host --pgsql-port=$port --pgsql-user=$user --pgsql-password=$pwds --pgsql-db=$db --use_fk=0 --threads=16 --tables=$table --scale=$wh --trx_level=RC --db-ps-mode=auto --db-driver=pgsql cleanup
/home/charles/MyTools/Packages/sysbench-tpcc-cus/tpcc.lua --pgsql-host=$host --pgsql-port=$port --pgsql-user=$user --pgsql-password=$pwds --pgsql-db=$db --use_fk=0 --threads=16 --tables=$table --scale=$wh --trx_level=RC --db-ps-mode=auto --db-driver=pgsql prepare
