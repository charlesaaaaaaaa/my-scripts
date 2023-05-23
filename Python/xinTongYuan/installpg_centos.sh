version=15.3
rm -rf postgresql-$version.tar.gz pg
echo 下载中...
wget http://192.168.0.104:14000/thirdparty/cloud/postgresql-15.3.tar.gz > tmp.log 2>&1
mkdir -p pg pg/pgbase pg/pgdata
mv postgresql-$version.tar.gz pg
pgbase=`readlink -f pg/pgbase`
pgdata=`readlink -f pg/pgdata`
cd pg
tar -zxf postgresql-$version.tar.gz
cd postgresql-$version
echo 编译中... 
./configure --prefix=$pgbase >> tmp.log 2>&1
make -j8 >> tmp.log 2>&1
make install >> tmp.log 2>&1
echo init...
cd $pgbase/bin
./initdb -D $pgdata >> tmp.log 2>&1 
cat << EOF >> $pgdata/pg_hba.conf
host    all             all             0.0.0.0/0               trust
host    all             all             127.0.0.1/32            trust
EOF
sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/" $pgdata/postgresql.conf
sed -i "s/#port = 5432/port = 35432/" $pgdata/postgresql.conf
startCmd=`cat tmp.log | grep 'pg_ctl -D'`
echo 开启中...
export PATH=$pgbase/bin:$PATH && export LD_LIBRARY_PATH=$pgbase/lib:$LD_LIBRARY_PATH && $startCmd >> tmp.log
psql postgres://localhost:35432/postgres -c "alter user `whoami` with password '`whoami`'"
echo '使用方法：(localhost可以改成ip地址)'
echo "	psql postgres://`whoami`:`whoami`@localhost:35432/postgres"
