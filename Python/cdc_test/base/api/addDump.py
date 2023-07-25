import json
from base.other.otherOpt import *
import requests
from base.srcTable.klustron import *
from base.api.get import *
from base.getconf import readcnf

class post():
    def __init__(self):
        self.conf = readcnf().getConfigDbInfo()

    def src_klustron_now(self):
        pass

    def src_klustron(self, dump_tables, shard_param):
        mysqlInfo = readcnf().getMysqlInfo()
        mysqlDict = '{\"hostaddr\": \"%s\", \"port\": \"%s\", \"user\": \"%s\", \"password\": \"%s\", \"log_path\"' \
                       ': \"../log\", \"is_kunlun\": \"0\"}' % (mysqlInfo['host'], mysqlInfo['port'], mysqlInfo['user'], mysqlInfo['password'])
        master = leader().info()
        metadataList = info().getMetadataList()
        clusterName = info().clusterName()
        clusterInfo = info().clusterInfo()
        cdcInfo = readcnf().getCdcInfo()
        cdcLog = cdcInfo['log']
        timeStamp = '%.0f' % time.time()
        shard_params = []
        for i in shard_param:
            shard_params.append(shard_param[i])
        json.dumps(shard_params)
        url = 'http://%s/kunlun_cdc' % master
        jsonData = json.dumps({
            "version":"1.0",
            "job_id":"",
            "job_type": "add_dump_table",
            "timestamp": timeStamp,
            "user_name": "kunlun_test",
            "paras":{
                "meta_db": metadataList,
                "meta_user": clusterInfo['metadata']['user'],
                "meta_passwd": clusterInfo['metadata']['password'],
                "cluster_name": clusterName,
                "dump_tables": dump_tables,
                "shard_params":
                    shard_params,
                "output_plugins":[
                    {
                        "plugin_name":"event_file",
                        "plugin_param": cdcLog,
                        "udf_name":"test1"
                    },
                    {
                        "plugin_name":"event_sql",
                        "plugin_param": mysqlDict,
                        "udf_name":"test2"
                    }
                ]
            }
        })
        writeLog(str(url))
        writeLog(str(jsonData))
        res = requests.post(url, data=jsonData)
        if res.status_code != 200:
            err_content = 'failure: 发起add_dump失败，status_code = %s\n' % res.status_code
            writeLog(err_content)
        else:
            log = '发起add_dump成功\n\t%s' % res.text
            writeLog(log)
        writeLog(res.text)

    def src_mysql(self, ConfigDbInfo, binlog_dict, tableList, cdcInfo, comp_mysql_protocol_port):
        master = leader().info()
        klustron = ConfigDbInfo['klustron']
        mysql = ConfigDbInfo['mysql']
        meta_db = '%s:%s' % (mysql['host'], mysql['port'])
        cluster_name = 'cdcTest_%s' % tableList.split('.')[0]
        plugin_param = '{\"hostaddr\": \"%s\", \"port\": \"%s\", \"user\": \"%s\", \"password\": \"%s\", \"log_path\"' \
                       ': \"../log\"}' % (klustron['host'], comp_mysql_protocol_port, klustron['user'], klustron['password'])
        url = 'http://%s/kunlun_cdc' % master
        jsonData = json.dumps({
        "version": "1.0",
        "job_id": "",
        "job_type": "add_dump_table",
        "timestamp": "1435749309",
        "user_name": "kunlun_test",
        "paras":{
                "meta_db": meta_db,
                "meta_user": mysql['user'],
                "meta_passwd": mysql['password'],
                "cluster_name": cluster_name,
                "dump_tables": tableList,
                "is_kunlun": "0",
                "shard_params": [
                        {
                        "binlog_file": binlog_dict['Log'],
                        "binlog_pos": binlog_dict['Pos'],
                        "gtid_set": binlog_dict['Gtid']
                        }
                ],
        "output_plugins":[
                {
                "plugin_name": "event_file",
                "plugin_param": cdcInfo['log'],
                "udf_name": "test1"
                },
                {
                "plugin_name": "event_sql",
                "plugin_param": plugin_param,
                "udf_name": "test2"}
                ]
            }
        })
        writeLog(str(url))
        writeLog(str(jsonData))
        res = requests.post(url, data=jsonData)
        if res.status_code != 200 :
            err_content = 'failure: 发起add_dump失败，status_code = %s\n' % res.status_code
            writeLog(err_content)
        else:
            log = '发起add_dump成功\n\t%s' % res.text
            writeLog(log)
        return res.text

# print(readcnf().getMysqlInfo())