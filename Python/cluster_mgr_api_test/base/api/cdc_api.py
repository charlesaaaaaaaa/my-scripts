from base.other.info import *
from base.other import getconf, info, sys_opt
import json
import requests
import time


def send_cdc_api(json_data, job_id=None, ip_port=None):
    # 当txt=None时，则返回一个job_id, 否则返回整个json值
    # 当ip_port为None时，则使用配置文件里面的host和port，否则给一个以 host:port 为格式的字符串去访问这个cdc
    # 当json_data = 'get_leader'时，直接返回当前cdc主
    ts = int(time.time())
    cdc_cnf = getconf.get_conf_info().cdc_info()
    host_list = cdc_cnf['cdc_host'].replace(' ', '').split(',')
    port_list = cdc_cnf['cdc_port'].replace(' ', '').split(',')
    if ip_port == None:
        for i in range(len(host_list)):
            host, port = host_list[i], port_list[i]
            url = 'http://%s:%s/kunlun_cdc' % (host, port)
            js_data = json.dumps(
                {
                    "version": "1.0",
                    "job_id": "",
                    "job_type": "get_leader",
                    "timestamp": "%s" % ts,
                    "user_name": "kunlun_test"
                }, indent=4
            )
            ip_port = json.loads(requests.post(url=url, data=js_data).text)['attachment']['ipPort']
            if ip_port:
                break
        if json_data == 'get_leader':
            return ip_port
    url = 'http://%s/kunlun_cdc' % (ip_port)
    res = json.loads(requests.post(url=url, data=json_data).text)
    if job_id == None:
        job_id = res['job_id']
        return job_id
    else:
        return res

class Get:
    def __init__(self):
        self.ts = int(time.time())

    def get_leader(self):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "get_leader",
                "timestamp": "%s" % self.ts,
                "user_name": "kunlun_test"
            }, indent=4
        )

    def list_support_plugins(self):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "list_support_plugins",
                "timestamp": "%s" % self.ts,
                "user_name": "kunlun_test"
            }, indent=4
        )

    def list_dump_jobs(self):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "list_dump_jobs",
                "timestamp": "%s" % self.ts,
                "user_name": "kunlun_test"
            }, indent=4
        )

    def get_job_state(self):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "get_job_state",
                "timestamp": "%s" % self.ts,
                "user_name": "kunlun_test",
                "paras": {
                    "meta_db": "172.0.0.1:28001,172.0.0.2:28001,172.0.0.3:28001",
                    "cluster_name": "cluster_xxx_xxx",
                    "dump_tables": "postgres_$$public.t1,postgres$$_public.t2"
                }
            }, indent=4
        )

    def get_state(self, job_id):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "%s" % job_id,
                "job_type": "get_state",
                "timestamp": "%s" % self.ts,
                "user_name": "kunlun_test"
            }, indent=4
        )
        txt = 'get_state job_id[%s]' % job_id
        print(json_data)
        res = send_cdc_api(json_data=json_data, job_id=job_id)
        while res['status'] == "ongoing":
            time.sleep(5)
            res = send_cdc_api(json_data=json_data, job_id=job_id)
        print("结果： %s" % res)
        if res['status'] == "done":
            print("job_id[%s] 成功" % job_id)
            return 1
        else:
            print("job_id[%s] 失败" % job_id)
            return 0


    def list_cdc_conf(self):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "list_cdc_conf",
                "timestamp": "1435749309",
                "user_name": "kunlun_test"
            }, indent=4
        )


class NeedAllDump:
    def __init__(self, meta_db, meta_user, meta_passwd, cluster_name, dump_tables):
        # "meta_db": "172.0.0.1:28001,172.0.0.2:28001,172.0.0.3:28001",
        # "dump_tables": postgres_$$_public.t1,postgres_$$_public.t2
        self.ts = int(time.time())
        self.meta_db = meta_db
        self.meta_user = meta_user
        self.meta_passwd = meta_passwd
        self.cluster_name = cluster_name
        self.dump_tables = dump_tables

    def post(self, plugin_info):
        json_data = json.dumps(
            {
                "version": "1.0",
                "job_id": "",
                "job_type": "add_dump_table",
                "timestamp": "1435749309",
                "user_name": "kunl un_test",
                "paras": {
                    "meta_db": "%s" % self.meta_db,
                    "meta_user": "%s" % self.meta_user,
                    "meta_passwd": "%s" % self.meta_passwd,
                    "dump_db_type": "kunlunbase",
                    "cluster_name": "%s" % self.cluster_name,
                    "dump_tables": "%s" % self.dump_tables,
                    "need_alldump": "1",
                    "output_plugins": [
                        {
                            "plugin_name": "event_file",
                            "plugin_param": "../log/event.log",
                            "udf_name": "test1"
                        },
                        plugin_info
                    ]
                }
            }, indent=4
        )
        job_id = send_cdc_api(json_data=json_data)
        res = Get().get_state(job_id)
        return res

    def to_mysql(self, host, port, user, passwd):
        pp = "{\"hostaddr\":\"%s\",\"port\":\"%s\",\"user\":\"%s\",\"password\":\"%s\",\"log_path\":\"../log\"}" \
             "" % (host, port, user, passwd)
        json_data = json.dumps(
            {
                "plugin_name": "event_sql",
                "plugin_param": "%s" % pp,
                "udf_name": "test2"
            }
        )
        res = self.post(plugin_info=json_data)
        return res

    def to_mariadb(self, host, port, user, passwd):
        pp = "{\"hostaddr\":\"%s\",\"port\":\"%s\",\"user\":\"%s\",\"password\":\"%s\",\"log_path\":\"../log\"," \
             "\"is_kunlun\":\"0\"}" % (host, port, user, passwd)
        json_data = json.dumps(
            {
                "plugin_name": "event_sql",
                "plugin_param": "%s" % pp,
                "udf_name": "test2"
            }
        )
        res = self.post(plugin_info=json_data)
        return res

    def to_es(self, ip_port, es_index, es_version='v8'):
        # ip_port = 172.0.0.2:24002
        # es_version = v7 | v8
        pp = "{\"es_url\":\"%s\",\"es_index\":\"%s\",\"es_version\":\"%s\",\"log_name\":\"../log/es.log\"," \
             "\"log_path\":\"../log\"}" % (ip_port, es_index, es_version)
        json_data = json.dumps(
            {
                "plugin_name": "event_es",
                "plugin_param": "%s" % pp,
                "udf_name": "test2"
            }
        )
        res = self.post(plugin_info=json_data)
        return res


class AddDump:
    pass
