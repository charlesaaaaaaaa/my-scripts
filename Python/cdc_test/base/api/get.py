import requests
import time
import json
from base.getconf import readcnf
from base.other.otherOpt import *

class leader():
    def __init__(self):
        self.conf = readcnf().getCdcInfo()

    def info(self):
        conf = self.conf
        timestamp = '%.0f' % time.time()
        jsonData = json.dumps({
        "version":"1.0",
        "job_id":"",
        "job_type":"get_leader",
        "timestamp":timestamp,
        "user_name":"kunlun_test"
        })
        for i in range(int(conf['nodenum'])):
            tmpHost = conf['host'].split(',')[i].replace(' ', '')
            tmpPort = conf['port'].split(',')[i].replace(' ', '')
            url = 'http://%s:%s/kunlun_cdc' % (tmpHost, tmpPort)
            try:
                res = requests.post(url, data=jsonData)
                if res.status_code == 200:
                    txt = res.text
                    break
            except Exception as err:
                err = '连接%s失败，尝试连接下一个节点：%s' % (url, err)
                writeLog(err)
        master = txt.split('"')[9]
        if res.status_code != 200 or master == 'error_info':
            err = '当前无法找到主'
            writeLog(err)
        else:
            log = '调用get_leader成功，当前cdc主节点为%s\n\t%s' % (master, txt)
            writeLog(log)
            return master

class listDumpJob():
    def __init__(self):
        pass

    def info(self):
        conf = leader().info()
        timestamp = '%.0f' % time.time()
        jsonData = json.dumps({
        "version":"1.0",
        "job_id":"",
        "job_type":"list_dump_jobs",
        "timestamp":timestamp,
        "user_name":"kunlun_test"
        })
        url = 'http://%s/kunlun_cdc' % conf
        res = requests.post(url, data=jsonData)
        txt = json.loads(res.text)
        master = {"master": conf}
        txt = json.dumps(dict(txt, **master))
        return txt

class jobState():
    def __init__(self):
        pass

    def info(self):
        cnf = json.loads(listDumpJob().info())
        timeStamp = '%.0f' % time.time()
        dumpTable = cnf['attachment'][0]['dump_tables']
        metadb = cnf['attachment'][0]['metadb']
        cluster_name = cnf['attachment'][0]['cluster_name']
        try:
            is_kunlun = cnf['attachment'][0]['is_kunlun']
        except:
            is_kunlun = '1'
        jsonData = json.dumps({
                    "version":"1.0",
                    "job_id":"",
                    "job_type":"get_job_state",
                    "timestamp":timeStamp,
                    "user_name":"kunlun_test",
                    "paras":{
                        "meta_db":metadb,
                        "is_kunlun": is_kunlun,
                        "cluster_name":cluster_name,
                        "dump_tables":dumpTable
                    }
        })
        url = 'http://%s/kunlun_cdc' % cnf['master']
        res = requests.post(url, data=jsonData)
        txt = json.loads(res.text)
        return txt
#
mysqlInfo = readcnf().getMysqlInfo()
mysqlDict = '{\"hostaddr\": \"%s\", \"port\": \"%s\", \"user\": \"%s\", \"password\": \"%s\", \"log_path\"' \
            ': \"../log\", \"is_kunlun\": \"0\"}' % (mysqlInfo['host'], mysqlInfo['port'], mysqlInfo['user'], mysqlInfo['password'])
print(json.dumps({"abc": mysqlDict}))
print(mysqlDict)