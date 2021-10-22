iconv -f GBK -t UTF-8 ./tools/customer.dat -o ./tools/tcustomer.dat  #把编码转换成UTF-8
sed -i 's/'"'"/' ''/g' ./tools/customer.dat                          #把包含有 ‘ 的给去掉，不然计算节点会不认识报错

