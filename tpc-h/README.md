```
1.  cd TPC-H_Tools_v3.0.0/dbgen/

mv makefile.suite makefile
vi makefile
	change makefile on line 103 to 111, like：
103 CC      = gcc
104 # Current values for DATABASE are: INFORMIX, DB2, TDAT (Teradata)
105 #                                  SQLSERVER, SYBASE, ORACLE, VECTORWISE
106 # Current values for MACHINE are:  ATT, DOS, HP, IBM, ICL, MVS, 
107 #                                  SGI, SUN, U2200, VMS, LINUX, WIN32 
108 # Current values for WORKLOAD are:  TPCH
109 DATABASE=ORACLE 
110 MACHINE = LINUX
111 WORKLOAD = TPCH

2.  make
```


```
3.  ./dbgen -vf -s 1
	-s 1 : Generate 1GB of data
    
4.  bash ./modify_splits.sh	

5.  psql -h host -p port -d db_name -f ./dss.ddl
	like
	psql -h localhost -p 8881 -d tpch -f ./dss.ddl

6.  bash ./copy.sh host port db_name user_name
	like 
	bash ./copy.sh localhost  8881 tpch abc

7.  bash ./create_statements.sh

8.  bash ./run.sh host port db_name user_name
	like
	bash ./run.sh localhost 8881 tpch abc
```
