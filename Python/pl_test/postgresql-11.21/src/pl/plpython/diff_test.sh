src=$1
psql postgres://abc:abc@192.168.0.132:59701/postgres -f sql/$src.sql -a > a.txt 2>&1
bash rewrite.sh a.txt
diff a.txt expected/$src.out -y --left-column

