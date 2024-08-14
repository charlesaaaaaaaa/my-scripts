import pyhdfs
from pyhdfs import HdfsClient
import argparse
import logging
import sys, time


def run(hdfs_host, hdfs_port, cluster_name, hdfs_user='kunlun'):
    # clsuter_name = 'select name from db_clusters  where status = "inuse"  limit 0,1;'
    client = pyhdfs.HdfsClient(hosts="%s:%s" % (hdfs_host, hdfs_port), user_name=hdfs_user)
    path = '/kunlun/backup/xtrabackup/'
    allpath = path + cluster_name
    logging.basicConfig(level=logging.INFO, filename="./hdfs_query.log", filemode='a',
                        format='%(asctime)s - %(levelname)s: %(message)s')
    hadoop_file1 = client.listdir(path)
    hadoop_file2 = client.listdir(allpath)
    for i in hadoop_file1:
        if str(i) == cluster_name:
            print(str(i))
            logging.info("get 3rd total quantity of backup file from hdfs :" + str(i))
            for j in hadoop_file2:
                print(str(j))
                logging.info("get 3rd total quantity of backup file from hdfs :" + str(j))
            break

    try:
        sys.stdout.close()
        sys.stderr.close()
    except:
        pass
