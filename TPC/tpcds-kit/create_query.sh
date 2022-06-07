csplit query/query_0.sql /Query/ -n 3 -s {*} -f q -b "%02d.sql" ;#分割文本到各个小文本

for i in `seq 1 9` ; do mv q0$i.sql query/q$i.sql ;done

rm q00.sql

for n in `seq 1 99` ; do sed -i '1d' query/q$n.sql ;done

chmod 755 *sh

echo create sql query success!
