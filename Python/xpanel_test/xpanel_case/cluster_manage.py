import random
from bin.other_opt import *
from xpanel_case.load import *

class cluster_list():
    def __init__(self):
        self.driver = loading().load()
        self.elements = getElements().cluster_manage()

    @timer
    def add_new_cluster(self):
        resList = []
        result = 1
        caseName = "创建集群"
        print('== 现在测试用例为 %s ==' % caseName)
        driver = self.driver
        ele = self.elements
        conf = getconf().getXpanelInfo()
        cluster_name = conf['cluster_name']
        db_shard_num = conf['shard_num']
        db_shard_node_num = conf['shard_node_num']
        pg_select_node = conf['pg_node']
        driver.click_Xpath(ele['cluster_list'])
        driver.click_Xpath(ele['cluster_list_add_cluster_button'])
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_business_name'], cluster_name)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shard_num'], db_shard_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_shardnode_num'], db_shard_node_num)
        driver.clearAndSend_Xpath(ele['cluster_list_add_cluster_pg_totalnum'], pg_select_node)
        driver.click_Xpath(ele['cluster_list_add_cluster_dblist_button'])
        rangeHead = ele['cluster_list_add_cluster_dblist_button_range']
        #循环点三个db的节点选项
        for i in range(1, int(db_shard_node_num) + 1):
            rangeTail = 'div[1]/div[1]/ul/li[%s]/span' % i
            eles = rangeHead + rangeTail
            driver.click_Xpath(eles)
        driver.click_Xpath(ele['cluster_list_add_cluster_dblist_button_end'])
        driver.click_Xpath(ele['cluster_list_add_cluster_pglist_button'])
        rangeHead = ele['cluster_list_add_cluster_pglist_button_range']
        # 循环点三个pg的节点选项
        for i in range(1, int(pg_select_node) + 1):
            rangeTail = 'li[%s]/span' % i
            eles = rangeHead + rangeTail
            driver.click_Xpath(eles)
        driver.click_Xpath(ele['cluster_list_add_cluster_commit_button'])
        sleep(10)
        #检查集群是否完成
        global a
        a = 1
        def review_status(elements, rightTxt, errTxt):
            global a
            times = 1
            while True:
                if a == 0:
                    break
                try:
                    percent = driver.gettxt_Xpanth(elements)
                    assert percent == rightTxt
                    print(percent)
                    a = 1
                    return a
                    break
                except:
                    if times < 600:
                      times += 1
                      if percent == errTxt:
                          print(errTxt)
                          a = 0
                          return a
                      sleep(1)
                    else:
                        print('当前新建集群超过10分钟，失败')
                        a = 0
                        return a
        resList.append(review_status(ele['install_pg_info'], '新增computer成功', '新增computer失败'))
        #resList.append(review_status(ele['install_db_info'], '新增shard成功', '新增shard失败'))
        resList.append(review_status(ele['install_cluster_info'], '新增集群成功', '新增集群失败'))
        for i in resList:
            if i == 0:
                result = 0
        res = [caseName, result]
        return res

    @timer
    def config_variables(self):
        driver = self.driver
        ele = self.elements
        rangeTimes = 3
        errTimes = 0
        caseName = "参数配置"
        print('== 现在测试用例为 %s ==' % caseName)
        variableList = ['lock_wait_timeout', 'fullsync_timeout', 'innodb_lock_wait_timeout']
        for i in range(rangeTimes):
            keys = random.choice(variableList)
            value = random.randint(500, 3000)
            driver.click_Xpath(ele['cluster_list_info'])
            driver.click_Xpath(ele['cluster_list_setting_button'])
            driver.click_Xpath(ele['set_variable_button'])
            print('第 %d 次设置变量：%s = %s' % (i+1, keys, value))
            driver.clearAndSend_Xpath(ele['set_variable_input'], 'set global %s = %s' % (keys, value))
            driver.click_Xpath(ele['set_variable_save_button'])
            sleep(3)
            driver.click_Xpath(ele['get_variable_button'])
            print('获取%s值：' % keys)
            driver.clearAndSend_Xpath(ele['get_variable_input'], "show variables like '%s';" % keys)
            driver.click_Xpath(ele['get_variable_save_button'])
            info = driver.gettxt_Xpanth(ele['get_alert_info'])
            getValue = info.split('=')[1]
            if int(getValue) == value:
                print('\t%s' % info)
            else:
                print('失败，当前 % s设置的值 %s 与获取的值 %s 不同' % (keys, value, getValue))
                errTimes += 1
        if errTimes > 0:
            print('本次测试失败 %s 次, 共测试 %s 次' % (errTimes, rangeTimes))
            a = 0
        else:
            print("本次测试 %s 次，全都成功" % (rangeTimes))
            a = 1
        res = [caseName, a]
        return res

    @timer
    def monitor(self):
        driver = self.driver
        ele = self.elements
        caseName = '实时监控'
        print('== 现在测试用例为 %s ==' % caseName)
        driver.click_Xpath(ele['cluster_list_info'])
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_shard_list'])
        monHead = ele['cluster_dbinfo_masterornot_range']
        ipHead = ele['cluster_dbinfo_ip_range']
        hostHead = ele['cluster_dbinfo_host_range']
        for i in range(1, 4):
            monTail = 'tr[%s]/td[4]/div/span' % i
            mon = monHead + monTail
            monTxt = driver.gettxt_Xpanth(mon)
            ipTail = 'tr[%s]/td[2]/div/span' % i
            ip = ipHead + ipTail
            ipTxt = driver.gettxt_Xpanth(ip)
            hostTail = 'tr[%s]/td[3]/div' % i
            host = hostHead + hostTail
            hostTxt = driver.gettxt_Xpanth(host)
            print('当前选中节点 %s: %s 为 %s 节点' % (ipTxt, hostTxt, monTxt) )
            if monTxt == '备':
                break
        disable_button = ele['cluster_dbinfo_disable_button_range']
        disable_ele = disable_button + 'tr[%s]/td[9]/div/button[3]/span' % i
        disableTxt = driver.gettxt_Xpanth(disable_ele)
        if disableTxt == '禁用 ':
            print('当前按钮为禁用， 点击中')
            driver.click_Xpath(disable_ele)
        else:
            print("当前备节点 %s: %s 的禁用按钮不存在，失败" % (ipTxt, hostTxt))
            a = 0
            res = [caseName, a]
            return res
        txt = driver.gettxt_Xpanth(ele['warning_info'])
        wanCode = str(txt).split('=')[1]
        driver.clearAndSend_Xpath(ele['warning_input'], wanCode)
        driver.click_Xpath(ele['disable_node_commit_button'])

        def check_alter_info(elements, caseName, rightTxt, errTxt):
            times = 0
            while True:
                try:
                    txt = driver.gettxt_Xpanth(elements)
                    assert txt == rightTxt
                    print(txt)
                    break
                except:
                    times += 1
                    if times == 150:
                        print('时间超过150，失败')
                        a = 0
                        res = [caseName, a]
                        return res
                    try:
                        if txt == errTxt:
                            a = 0
                            res = [caseName, a]
                            return res
                    except:
                        pass
                    sleep(1)
        check_alter_info(ele['disable_info'], caseName, ' 禁用成功 ', ' 禁用失败 ')
        driver.click_Xpath(ele['disable_alert_close_button'])
        sleep(5)
        driver.reflush()
        driver.click_Xpath(ele['cluster_list_setting_button'])
        driver.click_Xpath(ele['cluster_shard_list'])
        restartHead = ele['restart_button_range']
        restart_ele = restartHead + 'tr[%s]/td[9]/div/button[1]/span' % i
        print('点击重启中。。。')
        driver.click_Xpath(restart_ele)
        txt = driver.gettxt_Xpanth(ele['warning_info_restart'])
        restart_code = txt.split('=')[1]
        driver.clearAndSend_Xpath(ele['warning_input_restart'], restart_code)
        driver.click_Xpath(ele['resatart_node_commit_button'])
        check_alter_info(ele['restart_info'], caseName, ' 重启成功 ', ' 重启失败 ')
        driver.click_Xpath(ele['restart_alter_close_button'])
        errTimes = 0
        while True:
            try:
                txt = driver.gettxt_Xpanth(ele['get_node_status'])
                assert txt == '运行中'
                print(txt)
                print('本次测试成功')
                break
            except:
                errTimes += 1
                if errTimes >= 60:
                    a = 0
                    res = [caseName, a]
                    return res
                sleep(1)
        a = 1
        res = [caseName, a]
        return res
