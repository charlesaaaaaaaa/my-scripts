import requests
import json
import time
import base.other.getconf as conf
import base.other.write_log as W2F
from base.other import info

class mgr_infos():
    def __init__(self):
        self.mgr_info = info.master().cluster_mgr()

    def cluster_info(self):
        mgr_info = self.mgr_info
        url = 'http://%s:%s/HttpService/Emit' % (mgr_info[0], mgr_info[1])
        print(url)
        now_timestamp = int(time.time())
        json_data = json.dumps({
            "version": "1.0",
            "job_id": "",
            "job_type": "get_machine_summary",
            "timestamp": "%s" % now_timestamp,
            "paras": {
            }
        })
        res = requests.post(url, data=json_data)
        print(res.text)

class status():
    def __init__(self):
        self.mgr_info = info.master().cluster_mgr()
        self.url = 'http://%s:%s/HttpService/Emit' % (self.mgr_info[0], self.mgr_info[1])

    def cluster(self, clu_id, dst_shard_id, src_shard_id, table_list):
        jsdata = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "expand_cluster",
                "timestamp": "%d" % int(time.time()),
                "user_name": "kunlun_test",
                "paras": {
                    "cluster_id": clu_id,
                    "dst_shard_id": dst_shard_id,
                    "src_shard_id": src_shard_id,
                    "table_list": [
                        table_list
                    ]
                }
            }
        )

    def job_status(self, job_id):
        time_stamp = int(time.time())
        url = self.url
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": str(job_id),
                "job_type": "get_status",
                "timestamp": str(time_stamp),
                "user_name": "kunlun_test",
                "paras": {
                }
            }
        )
        res = requests.post(url, json_data)
        res_dict = json.loads(res.text)
        return res_dict