import requests
import pymysql
import json
import yaml
import argparse
from time import sleep

def readFile():
    global user_name, cluster_id, shard_id, iplist, mgrPort, mgrHost, postad
    f = open(files,encoding='utf-8')
    of = yaml.safe_load(f.read())
    user_name = of["username"]
    cluster_id = str(of["cluster_id"])
    shard_id = str(of["shard_id"])
    iplist = of["iplist"]
    metaPort = of["MetaPrimaryNode"]["port"]
    metaHost = of["MetaPrimaryNode"]["host"]
    db = pymysql.connect(host = metaHost, port = int(metaPort), user = "pgx", password = "pgx_pwd", database = "kunlun_metadata_db")
    cur = db.cursor()
    cur.execute("select hostaddr from cluster_mgr_nodes where  member_state = 'source'")
    MgrHost = cur.fetchone()
    cur.execute("select port from cluster_mgr_nodes where  member_state = 'source'")
    MgrPort = cur.fetchone()
    db.commit()
    cur.close()
    db.close()
    print(MgrPort)
    print(MgrHost)
    mgrPort = str(MgrPort)
    mgrHost = str(MgrHost)
    mgrPort = mgrPort.replace('(','')
    mgrPort = mgrPort.replace(",)","")
    mgrHost = mgrHost.replace("('","")
    mgrHost = mgrHost.replace("',)","")
    print(mgrPort)
    print(mgrHost)
    postad = "http://%s:%s/HttpService/Emit" % (mgrHost, mgrPort)


header = {
        "cookie": "cookie",
        "Accept": "*/*",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Connection": "keep-alive",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}

def delshard(user_name, cluster_id, shard_id):
    create_storage = json.dumps({
    "version":"1.0",
    "job_id":"",
    "job_type":"delete_shard",
    "timestamp":"1435749309",
    "user_name":user_name,
    "paras":{
        "cluster_id":cluster_id,
        "shard_id":shard_id
    }
})
    #print(create_storage + '\n')
    #res = requests.post(postad, data=create_storage, headers=header)
    res = requests.post(postad, data=create_storage)
    print("delete shard, shard_id = %s cluster_id = %s" % (shard_id, cluster_id))
    print(res.status_code, res.reason)
    print(res.text)

def delmachine(user_name, ip):
    del_machine = json.dumps({
    "version":"1.0",
    "job_id":"",
    "job_type":"delete_machine",
    "timestamp":"1435749309",
    "user_name":user_name,
    "paras":{
        "hostaddr":ip,
        "machine_type":"storage"
    }
})
    res = requests.post(postad, data=create_storage)
    print("delete storage machine host = %s" % (ip))
    print(res.status_code, res.reason)
    print(res.text)

def del_shards():
    delshard(user_name, cluster_id, shard_id)
    for i in iplist:
        delmachine(user_name, i)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'install')
    parser.add_argument('--config', default='addShards.ymal', help = 'the configure yaml file')
    args = parser.parse_args()
    files = args.config
    readFile()
    del_shards()
