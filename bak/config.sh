bash remote_run.sh --user=charles 192.168.0.128 'line=`cat /home/kunlun/TPC/data/pgdatadir1/postgresql.conf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^statement_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf && sed -i "${line}i statement_timeout = 300" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf'

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat /home/kunlun/TPC/data/pgdatadir1/postgresql.conf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^mysql_read_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf && sed -i "${line}i mysql_read_timeout = 500" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf'

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat /home/kunlun/TPC/data/pgdatadir1/postgresql.conf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^mysql_write_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf && sed -i "${line}i mysql_write_timeout = 100" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf'

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat /home/kunlun/TPC/data/pgdatadir1/postgresql.conf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^lock_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf && sed -i "${line}i lock_timeout = 100" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf'

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat /home/kunlun/TPC/data/pgdatadir1/postgresql.conf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^log_min_duration_statement\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf && sed -i "${line}i log_min_duration_statement = 100" /home/kunlun/TPC/data/pgdatadir1/postgresql.conf'

bash remote_run.sh --user=charles 192.168.0.128 /home/kunlun/TPC/data/pgdatadir1/bin/pg_ctl reload -D /home/kunlun/TPC/data/pgdatadir1

bash remote_run.sh --user=charles 192.168.0.127 'line=`cat /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf && sed -i "${line}i lock_wait_timeout = 200" /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf '

bash remote_run.sh --user=charles 192.168.0.127 'line=`cat /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^innodb_lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf && sed -i "${line}i innodb_lock_wait_timeout = 300" /home/kunlun/TPC/data/meta_data1/52110/my_52110.cnf '

bash remote_run.sh --user=charles 192.168.0.127 'line=`cat  /home/kunlun/TPC/data/data1/52140/my_52140.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/data1/52140/my_52140.cnf && sed -i "${line}i lock_wait_timeout = 200" /home/kunlun/TPC/data/data1/52140/my_52140.cnf '

bash remote_run.sh --user=charles 192.168.0.127 'line=`cat  /home/kunlun/TPC/data/data1/52140/my_52140.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^innodb_lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/data1/52140/my_52140.cnf && sed -i "${line}i innodb_lock_wait_timeout = 300" /home/kunlun/TPC/data/data1/52140/my_52140.cnf '

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat  /home/kunlun/TPC/data/data4/52170/my_52170.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/data4/52170/my_52170.cnf && sed -i "${line}i lock_wait_timeout = 200" /home/kunlun/TPC/data/data4/52170/my_52170.cnf '

bash remote_run.sh --user=charles 192.168.0.128 'line=`cat  /home/kunlun/TPC/data/data4/52170/my_52170.cnf | awk -F= '\'{print \$1}\'' | grep -n -w '\'^innodb_lock_wait_timeout\'' | awk -F: '\'{print \$1}\''` && sed -i "${line}d" /home/kunlun/TPC/data/data4/52170/my_52170.cnf && sed -i "${line}i innodb_lock_wait_timeout = 300" /home/kunlun/TPC/data/data4/52170/my_52170.cnf '

python2 generate_scripts.py --action=clean --config=install_tpc-78.json 

time bash clean/commands.sh 

python2 generate_scripts.py --action=install --config=install_tpc-78.json --defuser=charles 

time bash install/commands.sh
