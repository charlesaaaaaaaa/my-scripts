> del.sql
del(){
	history=`echo "history$3"`
	new_orders=`echo "new_orders$3"`
	orders=`echo "orders$3"`
	order_line=`echo "order_line$3"`
	echo "delete from $history where h_c_d_id > 10;" >> del.sql
	echo "delete from $new_orders where  no_o_id > 3000 ;" >> del.sql
	echo "delete from $orders where o_id > 3000000 ;">> del.sql
	echo "delete from $order_line where ol_o_id > 3000;" >> del.sql
}
for i in `seq 1 10`
do
	del $1 $2 $i
done	

psql postgres://abc:abc@$1:$2/postgres -f del.sql > /dev/null
exit 0
