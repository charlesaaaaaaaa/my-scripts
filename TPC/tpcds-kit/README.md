# tpcds-kit

The official TPC-DS tools can be found at [tpc.org](http://www.tpc.org/tpc_documents_current_versions/current_specifications.asp).

This version is based on v2.10.0 and has been modified to:

* Allow compilation under macOS (commit [2ec45c5](https://github.com/gregrahn/tpcds-kit/commit/2ec45c5ed97cc860819ee630770231eac738097c))
* Address obvious query template bugs like
  * query22a: [#31](https://github.com/gregrahn/tpcds-kit/issues/31)
  * query77a: [#43](https://github.com/gregrahn/tpcds-kit/issues/43)
* Rename `s_web_returns` column `wret_web_site_id` to `wret_web_page_id` to match specification. See [#22](https://github.com/gregrahn/tpcds-kit/issues/22) & [#42](https://github.com/gregrahn/tpcds-kit/issues/42).

To see all modifications, diff the files in the master branch to the version branch. Eg: `master` vs `v2.10.0`.

## Setup

### Linux

Make sure the required development tools are installed:

Ubuntu:
```
sudo apt-get install gcc make flex bison byacc git
```

CentOS/RHEL:
```
sudo yum install gcc make flex bison byacc git
```

Then run the following commands to clone the repo and build the tools:

```
git clone https://github.com/gregrahn/tpcds-kit.git
cd tpcds-kit
tpcds_path=`pwd` #把 tpcds-kit(当前) 目录路径 赋值给变量 tpcds_path
cd tools
make OS=LINUX
```

#create database db_name 

#creata tpc-ds table
```
	cd ${tpcds_path}  #使用该变量
	chmod 755 *sh
	psql -h host -p port -d db_name -f create_table.sql
	like : psql -h 192.168.0.113 -p 8881 -d test -f create_table.sql
```
#create data dir & generated data
```
        ${tpcds_path}/tools/dsdgen -DIR /TPC_DS-path/datas -SCALE 1 #-SCALE 1 means grnerated 1 GB TPC-DS data
        or
        ${tpcds_path}/tools/dsdgen -DIR /TPC_DS-path/datas -SCALE 1 -parallel 4 -child 1 #-parallel 4 : use 4 threads
```
#copy data 
```
	cd ${tpcds_path}
	./copy.sh
	psql -h host -p port -d db_name -f copy.sql
	like : psql -h 192.168.0.113 -p 8881 -d test -f copy.sql
```
#create posgresql statement 
```	
	cd ${tpcds_path}
	./create_query.sh
```
#run tpc-ds
```	
	cd ${tpcds_path}
	./run.sh host port db_name 
	like 
	./run.sh 192.168.0.113 5423 test
```

