from xpanel_case.load import *
from bin.other_opt import *

class get():
    def __init__(self):
        self.driver = loading().load()
        self.ele = getElements().cluster_manage()

    def signal_pg(self):
        driver = self.driver
        ele = self.ele
        head_host = ele['cluster_list_pg_host']
        head_port = ele['cluster_list_pg_port']
        try:
            tail_host = 'tr/td[1]/div'
            tmpEle = head_host + tail_host
            host = driver.gettxt_Xpanth(tmpEle)
            tail_port = 'tr/td[2]/div'
            tmpEle = head_port + tail_port
            port = driver.gettxt_Xpanth(tmpEle)
        except:
            tail_host = 'tr[1]/td[1]/div'
            tmpEle = head_host + tail_host
            host = driver.gettxt_Xpanth(tmpEle)
            tail_port = 'tr[1]/td[2]/div'
            tmpEle = head_port + tail_port
            port = driver.gettxt_Xpanth(tmpEle)
        res = [host, port]
        return res

    def signal_db_master(self):
        driver = self.driver
        ele = self.ele
        num = 1
        driver.click_Xpath(ele['cluster_list_info'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_shard_list'])
        head = ele['cluster_dbinfo_masterornot_range']
        tail = 'tr[%s]/td[4]/div/span' % num
        tmpEle = head + tail
        txt = driver.gettxt_Xpanth(tmpEle)
        while txt != '主':
            num += 1
            tail = 'tr[%s]/td[4]/div/span' % num
            tmpEle = head + tail
            txt = driver.gettxt_Xpanth(tmpEle)
        head = ele['cluster_list_db_host']
        tail = 'tr[%s]/td[2]/div/span' % num
        tmpEle = head + tail
        host = driver.gettxt_Xpanth(tmpEle).replace(' ', '')
        head = ele['cluster_list_db_port']
        tail = 'tr[%s]/td[3]/div' % num
        tmpEle = head + tail
        port = driver.gettxt_Xpanth(tmpEle)
        res = [host, port]
        print('选中一个主存储节点：%s' % res)
        return res