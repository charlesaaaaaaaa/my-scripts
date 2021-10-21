count=`cat ./table/* | wc -l`
echo =====================================
echo "you have | ${count} | rows TPCH-data"
echo =====================================
exit 0
