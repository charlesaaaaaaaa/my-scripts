mkdir -p mysql2Kunlun
Home=`readlink -f mysql2Kunlun`
ps -ef | grep $Home | sed '$d' | awk '{print $2}' | xargs kill -9
rm -rf mysql2Kunlun && mkdir -p mysql2Kunlun
cd $Home
echo $Home
#Home=`pwd`
echo -e "========\n安装mysql\n========"
echo download mysql ...
wget -q https://downloads.mysql.com/archives/get/p/23/file/mysql-8.0.31-linux-glibc2.17-x86_64-minimal.tar.xz
tar -xf mysql-8.0.31-linux-glibc2.17-x86_64-minimal.tar.xz
cd mysql-8.0.31-linux-glibc2.17-x86_64-minimal
mysqlHome=`pwd`
echo mysql_home == $mysqlHome
cat << EOF > my.cnf 
[mysql]
port=12388
socket=$Home/mysql/mysql.sock

[client]
port=12388
socket=$Home/mysql/mysql.sock

[mysqldump]
quick
max_allowed_packet = 16M

[mysqld]
user = mysql
basedir = $Home/mysql/mysql-8.0.31
datadir = $Home/mysql/data
port=12388
server-id = 1
socket=$Home/mysql/mysql.sock

character-set-server = utf8mb4
collation-server = utf8mb4_general_ci
init_connect='SET NAMES utf8mb4'
lower_case_table_names = 1
EOF

mkdir -p $Home/mysql/mysql-8.0.31 $Home/mysql/data
cd $mysqlHome/bin
./mysqld --defaults-file=$mysqlHome/my.cnf --initialize --user=charles > tmp.log 2>&1
./mysqld_safe --defaults-file=$mysqlHome/my.cnf --user=kunlun &
myPwd=`tail -1 tmp.log | awk '{print $NF}'`
echo mysql_init_password == $myPwd
cat << EOF > alter.sql
ALTER user 'root'@'localhost' IDENTIFIED BY 'root';
use mysql
update user set host = '%' where User = 'root';
FLUSH PRIVILEGES;
create database mydumper;
ALTER USER 'root'@'%' IDENTIFIED BY 'root' PASSWORD EXPIRE NEVER;
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
ALTER USER 'root'@'%' IDENTIFIED BY 'root';
ALTER USER 'root'@'%' IDENTIFIED BY 'root' PASSWORD EXPIRE NEVER;
ALTER USER 'root'@'%' IDENTIFIED WITH mysql_native_password BY 'root';
FLUSH PRIVILEGES;
ALTER USER 'root'@'%' IDENTIFIED BY 'root';
GRANT Super, BACKUP_ADMIN ON *.* TO 'root'@'%' WITH GRANT OPTION;
FLUSH PRIVILEGES;
EOF
sleep 15
$mysqlHome/bin/mysql --defaults-file=$mysqlHome/my.cnf -uroot -p$myPwd mysql < $mysqlHome/bin/alter.sql --connect-expired-password
echo "$mysqlHome/bin/mysql --defaults-file=$mysqlHome/my.cnf -uroot -p'$myPwd' mysql < $mysqlHome/bin/alter.sql --connect-expired-password"
echo -e "========\nmysql 安装完成\n========"
cd $Home
echo 'downloading mydumper & ddl2kunlun-linux ...'
wget -q http://zettatech.tpddns.cn:14000/util/1.1/mydumper
wget -q http://zettatech.tpddns.cn:14000/util/1.2/ddl2kunlun-linux
chmod 755 mydumper ddl2kunlun-linux
echo -e "========\n灌数据中。。。\n========"
sysbench oltp_point_select --tables=1 --table-size=50000 --db-ps-mode=disable --db-driver=mysql --mysql-host=$1 --report-interval=1 --mysql-port=12388 --mysql-user=root --mysql-password=root --mysql-db=mydumper --rand-type=uniform prepare
ldd mydumper  | grep 'not found' | awk -F= '{print $1}' > tmp.txt
ldd ddl2kunlun-linux | grep 'not found' | awk -F= '{print $1}' >> tmp.txt
for i in `cat tmp.txt`
do
sudo find / -name $i > tmp.log 2> /dev/null
cp `head -1 tmp.log` .
done
export LD_LIBRARY_PATH=`pwd`:$LD_LIBRARY_PATH
./mydumper -h $1 -u root -p root -P 12388 -B mydumper -o $Home/myDumperData
PGPASSWORD=abc psql -h $2 -p $3 -U abc -d postgres -c 'drop schema if exists mydumper CASCADE; create schema mydumper'
./ddl2kunlun-linux -host="$1" -port="12388" -user="root" -password="root" -sourceType="mysql" -database="mydumper" -table="sbtest1" > a.sql
PGPASSWORD=abc psql -h $2 -p $3 -U abc -d postgres < a.sql
cd $Home/myDumperData
for i in `ls . | grep -v schema | grep sql`
do
    table=`echo $i | awk -F. '{print $2}'`
    db=`echo $i | awk -F. '{print $1}'`
    sed -i "s/\`$table\`/${db}.$table/" $i
    sed -i 's/0000-00-00/1970-01-01/' $i
    sed -i "s/\"/'/g" $i
done
for i in `ls . | grep -v schema | grep sql`
do
    echo begin $i
    PGPASSWORD=abc psql -h $2 -p $3 -U abc -d postgres -f $i
done
echo -e "========\n灌数据完成。。。\n========"
mysql -h$1 -P12388 -uroot -proot mydumper -e 'select count(*) from sbtest1' > a.txt
PGPASSWORD=abc psql -h $2 -p $3 -U abc -d postgres -c 'set search_path to mydumper; select count(*) from sbtest1' > b.txt
pgSize=`cat b.txt | grep -A 2 count | tail -1 | awk '{print $1}'`
mlSize=`tail -1 a.txt`
if [[ "$pgSize" -eq "$mlSize" ]]
then
	echo -e "KunlunBase count	$pgSize"
	echo -e "mysql count	 	$mlSize"
	echo 数据量相同，成功
else
	echo -e "KunlunBase count	$pgSize"
        echo -e "mysql count		$mlSize"
	echo 数据量不相同，失败
	exit 1
fi
