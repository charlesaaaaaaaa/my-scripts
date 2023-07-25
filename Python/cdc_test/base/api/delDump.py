import json
from base.getconf import readcnf
from base.api.get import leader
import requests

class deleteDump():
    def __init__(self, conf):
        self.conf = conf

    def post(self, metadb, cluster_name, dump_tables):
        conf = self.conf
        url = 'http://%s/kunlun_cdc' % leader(conf).info()
        jsonData = json.dumps({
                "version":"1.0",
                "job_id":"",
                "job_type":"del_dump_table",
                "timestamp":"1435749309",
                "user_name":"kunlun_test",
                "paras":{
                    "meta_db":metadb,
                    "cluster_name":cluster_name,
                    "dump_tables":dump_tables
                }
        })
        res = requests.post(url, data=jsonData)
        txt = '删除任务成功：%s' % res.status_code
        return txt

from base.api.get import listDumpJob
cdcInfo = readcnf('../../conf/config.conf').getCdcInfo()
cc =json.loads(listDumpJob(cdcInfo).info())
metadb = cc['attachment'][0]['metadb']
cluster_name = cc['attachment'][0]['cluster_name']
dump_tables = cc['attachment'][0]['dump_tables']
a = deleteDump(cdcInfo).post(metadb, cluster_name, dump_tables)
print(a)