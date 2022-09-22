#ldd /home/kunlun/base/program_binaries/kunlun-server-$VERSION/bin/postgres | grep 'not found' | awk -F= '{print $1}' | sort | uniq
for i in `ldd /home/kunlun/base/program_binaries/kunlun-server-$VERSION/bin/postgres | grep 'not found' | awk -F= '{print $1}' | sort | uniq`
do
	cp /home/kunlun/base/program_binaries/kunlun-server-$VERSION/lib/deps/$i /home/kunlun/base/program_binaries/kunlun-server-$VERSION/lib/
done
