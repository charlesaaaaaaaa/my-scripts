psql postgres://abc:abc@192.168.0.132:59701/postgres -c 'create extension pllua;'
psql postgres://abc:abc@192.168.0.132:59701/postgres -a -f sql/$1.sql > out/$1.out 2>&1 
cp out/$1.out a.txt
bash reout.sh a.txt
diff a.txt expected/$1.out
