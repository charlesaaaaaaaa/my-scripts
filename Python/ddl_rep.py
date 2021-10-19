import filecmp
import os
import random
from time import sleep
import io
import paramiko
import psycopg2

cns_num = 3  # your computing node numbers
cn_host = ["192.168.0.113", "192.168.0.113", "192.168.0.113"]  # host of the computing node
cn_port = ["8881", "8882", "8883"]  # port of the computing node
linux_host = "192.168.0.113"  # host of your linux
linux_user = "charles"  # user of your linuxd
linux_pwd = "welcome1"  # password of you linux
linux_port = 22  # port of your linux
tpcc_path = "/home/charles/MyTools/Packages/sysbench-tpcc"  # your sysbench-tpcc path
tpcc_prepare_time = 150  # the time what you need when prepareing data for 1 houseware & 1 tables & 100 threads

# create and run tpcc file----------------------------------------------------------------------------------------------------------------------------------
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(linux_host, linux_port, linux_user, linux_pwd)
cp_co="cp %s/tpcc_common.lua %s/tpcc_common.lua_bak" % (tpcc_path, tpcc_path)
cp_lu="cp %s/tpcc.lua %s/tpcc.lua_bak" % (tpcc_path, tpcc_path)
cp_pr="cp %s/prepare.sh %s/prepare.sh_bak" % (tpcc_path, tpcc_path)
change_pk_path = "sed -i \'s#require(\"tpcc_common\")#package.path =\"%s/tpcc_common.lua\"..\";..\\?.lua\"\\nrequire(\"tpcc_common\")#\' %s/tpcc.lua" % (
tpcc_path, tpcc_path)
modify_lu= "sed -i 's/sleep(30)/--sleep(30)/' %s/tpcc_common.lua" % (tpcc_path)
mod_pr="sed -i 's@./tpcc.lua@%s/tpcc.lua@' %s/prepare.sh"% (tpcc_path, tpcc_path)
print(modify_lu)
print(mod_pr)
print(change_pk_path)
ssh.exec_command(cp_co)
ssh.exec_command(cp_lu)
ssh.exec_command(cp_pr)
ssh.exec_command(change_pk_path)
ssh.exec_command(modify_lu)
ssh.exec_command(mod_pr)

print("========create resault dir...========")
ssh.exec_command("cd %s" % (tpcc_path))
stdin, stdout, stderr = ssh.exec_command("pwd")
print(stdout.read())
ssh.exec_command("mkdir %s/resault" % (tpcc_path))
for i in range(1, cns_num + 1):
    cn_nu=int(i-1)
    ssh.exec_command(
        "echo %s/prepare.sh %s %s t%s abc abc 1 1 100  >> resault/cn%s.sh" % (tpcc_path,cn_host[cn_nu], cn_port[cn_nu], i, i))
ssh.close()

# create databases -----------------------------------------------------------------------------------------------------------------------------------------

print("\n========now creating databases...========\n")
sleep(1)

for i in range(1, cns_num + 1):
    try:        
        cn_po = int(i - 1)
        conn = psycopg2.connect(database="postgres", user="abc", password="abc", host=cn_host[0], port=cn_port[cn_po])
        cur = conn.cursor()
        conn.autocommit = True
        DATABASE_NAME = "t%i" % (i)
        DB_NAME = """
            CREATE DATABASE {};
            """.format(DATABASE_NAME)
        cur.execute(DB_NAME)
        #print("create database t%i successful!" % (i))
        sleep(1)

        cur.close()
        conn.close()

    except:
        print("create database failure! database t%i exists or %s:%s wrong." % (i, cn_host[cn_po], cn_port[cn_po]))

    else:
        print("create database t%i success!" % (i))

# run tpcc ------------------------------------------------------------------------------------------------------------------------------------------------
print("\n========preparing tpcc data......========\n")
print("  skip  ")

ssh.connect(linux_host, linux_port, linux_user, linux_pwd)
cp_lu = "cp %s/tpcc_common.lua %s/tpcc_common.lua_bak" % (tpcc_path, tpcc_path)
change_pk_path = "sed -i \'s#require(\"tpcc_common\")#package.path =\"%s/tpcc_common.lua\"..\";..\\?.lua\"\nrequire(\"tpcc_common\")#\' %s/tpcc.lua" % (
tpcc_path, tpcc_path)

ssh.exec_command(change_pk_path)
for i in range(1, cns_num + 1):
    cn_nu=int(i-1)
    try:
        ssh.exec_command("bash resault/cn%s.sh &" % (i))
        sleep(1)
    except:
        print("prepare tpcc data on %s:%s/t%s failure" % (cn_host[cn_nu], cn_port[cn_nu], i))
    else:
        print("prepare tpcc data on %s:%s/t%s " % (cn_host[cn_nu], cn_port[cn_nu], i))

print("please wait %i seconds" % (tpcc_prepare_time))
sleep(tpcc_prepare_time)
ssh.close()

ssh.connect(linux_host, linux_port, linux_user, linux_pwd)
back_lu = "mv %s/tpcc_common.lua_bak %s/tpcc_common.lua" % (tpcc_path, tpcc_path)
back_pr = "mv %s/prepare.sh_bak %s/prepare.sh" % (tpcc_path, tpcc_path)
back_co = "mv %s/tpcc_common.lua_bak %s/tpcc_common.lua" % (tpcc_path, tpcc_path)
ssh.exec_command(back_lu)
ssh.exec_command(back_pr)
ssh.exec_command(back_co)
ssh.exec_command("rm resault/*")
ssh.close()
# test tpcc data ------------------------------------------------------------------------------------------------------------------------------------------
print("\n========test database && tpcc data========\n")
for i in cn_port:
    for n in range(1, cns_num + 1):
        tb_name = random.choice(
            ['history1', 'customer1', 'district1', 'item1', 'new_orders1', 'order_line1', 'orders1', 'stock1','warehouse1'])

        db_name = "t%s" % (n)
        conn = psycopg2.connect(database=db_name, user="abc", password="abc", host=cn_host[0], port=i)
        cur = conn.cursor()
        print("connect host:%s port:%s database:%s successful" % (cn_host[0], i, db_name))

        ran_tb = tb_name
        test_conn = ('select * from %s limit 1' % (tb_name))
        cur.execute(test_conn)

        results = cur.fetchall()
        print(results)
        conn.commit()
        cur.close()
        conn.close()


pg_list=["pg_class","pg_proc","pg_namespace","pg_database","pg_index","pg_shard","pg_shard_node","pg_cluster_meta","pg_cluster_meta_nodes", "pg_ddl_log_progress"]
# check pg_class ------------------------------------------------------------------------------------------------------------------------------------------
for list in range(1,11):
    list_num=int(list-1)
    print('\n========test %s=======' % (pg_list[list_num]))
    for i in range(1, cns_num + 1):
        cn_nu = int(i - 1)
        conn = psycopg2.connect(database="postgres", user="abc", password="abc", host=cn_host[cn_nu], port=cn_port[cn_nu])
        cur = conn.cursor()
        pg_class = "select * from %s ;" % (pg_list[list_num])
        cur.execute(pg_class)
        results_log = cur.fetchall()
        

        with open('./%s%s' % (pg_list[list_num],i), 'w') as f:
            f.write(str(results_log))


    for f in range(1, cns_num):
        status = filecmp.cmp("%s%s" % (pg_list[list_num],f), "%s%s" % (pg_list[list_num],f + 1))
        if status:
            print("node %s is the same as node %s,success!\n" % (f, f + 1))
        else:
            print("node %s is different form node %s,failure!\n" % (f, f + 1))

for cn_un in range(1, cns_num + 1):
    
    for list_d in range(10):
        try:
            pa_nu=int(list_d)
            a=str(pg_list[pa_nu])
            files="%s%s" % (a, cn_un)
            os.remove(files)
        except:
            print("%s not exists!" % (files))
            
ssh.connect(linux_host, linux_port, linux_user, linux_pwd)
ssh.exec_command("rm resault/*")

ssh.close()
