import subprocess
from selenium.webdriver.common.action_chains import ActionChains
from bin.other_opt import *
from xpanel_case.load import *
from xpanel_case.get_cluster_info import *
from threading import Thread


class alarm_test():
    def __init__(self):
        self.dbInfo = get().signal_db_master()
        self.driver = loading().load()
        self.sys_ele = getElements().system_manage()
        self.alarm_ele = getElements().alarm()
        self.xpanelInfo = getconf().getXpanelInfo()

    def start_alarm(self):
        dbInfo = self.dbInfo
        driver = self.driver
        sys_ele = self.sys_ele
        alarm_ele = self.alarm_ele
        xpanelInfo = self.xpanelInfo
        print('== 现在测试用例为 告警能力 ==')
        sleep(2)
        driver.click_Xpath(sys_ele['system_manage'])
        driver.click_Xpath(sys_ele['user_manage'])
        sleep(1)
        user_count = int(driver.gettxt_Xpanth(sys_ele['user_num_info']).split(' ')[1])
        if user_count != 1:
            for i in range(user_count - 1):
                try:
                    driver.click_Xpath(sys_ele['user_delete_button_1'])
                except:
                    driver.click_Xpath(sys_ele['user_delete_button_2'])
                finally:
                    driver.click_Xpath(sys_ele['user_delete_commit_button'])
        driver.click_Xpath(sys_ele['add_new_user'])
        driver.clearAndSend_Xpath(sys_ele['user_input'], 'test')
        driver.clearAndSend_Xpath(sys_ele['pwd_input'], 'Qwer1234.')
        driver.clearAndSend_Xpath(sys_ele['pwd_input_again'], 'Qwer1234.')
        driver.clearAndSend_Xpath(sys_ele['phone_num_input'], '12345123451')
        driver.clearAndSend_Xpath(sys_ele['email_addr_input'], xpanelInfo['email'])
        driver.click_Xpath(sys_ele['add_new_user_commit_button'])
        # 开始告警的这部分了
        driver.click_Xpath(alarm_ele['alarm_server_man'])
        driver.click_Xpath(alarm_ele['add_new_button'])
        # 这里是开始选择告警类型为存储节点异常的行，一般在第2行，但有的时候会变
        num = 1
        head = alarm_ele['alarm_type_range']
        tail = 'tr[%s]/td[2]/div' % num
        tmpEle = head + tail
        txt = driver.gettxt_Xpanth(tmpEle)
        print(txt, end=',')
        while txt != '存储节点异常':
            num += 1
            tail = 'tr[%s]/td[2]/div' % num
            tmpEle = head + tail
            txt = driver.gettxt_Xpanth(tmpEle)
            print(txt, end=',')
        print()
        # 这里开始点击要推送的用户 test
        try:
            head = alarm_ele['alarm_unkown_user']
            tail = 'tr[%s]/td[5]/div/div/div[1]/span/span/i' % num
            tmpEle = head + tail
            driver.click_Xpath(tmpEle)
        except:
            pass
        head = alarm_ele['alarm_push_user_range']
        tail = 'tr[%s]/td[5]/div/div/div[2]/input' % num
        tmpEle = head + tail
        sleep(1)
        driver.click_Xpath(tmpEle)
        user_select_num = 1
        head = alarm_ele['alarm_push_user_select_range']
        tail = 'li[%s]/span' % user_select_num
        tmpEle = head + tail
        txt = driver.gettxt_Xpanth(tmpEle)
        while txt != 'test':
            user_select_num += 1
            tail = 'li[%s]/span' % user_select_num
            tmpEle = head + tail
            txt = driver.gettxt_Xpanth(tmpEle)
        driver.click_Xpath(tmpEle)
        # 这是是取消掉已选择的告警方式
        head = alarm_ele['alarm_push_way_range']
        try:
            # 这里是取消默认的只有系统告警方式
            tail = 'tr[%s]/td[6]/div/div/div[1]/span/span/i' % num
            clear_tail = 'tr[%s]/td[6]/div/div/div[1]/input' % num
            tmpEle = head + tail
            driver.clear_Xpath(head + clear_tail)
            driver.click_Xpath(tmpEle)
        except:
            # 如果失败了说明已选择的告警方式不止默认的系统告警，所以我们要多取消几个
            for i in range(1, 4):
                tail = 'tr[%s]/td[6]/div/div/div[1]/span/span[%s]/i' % num
                tmpEle = head + tail
                try:
                   # for ii in range(2):
                    driver.clear_Xpath(tmpEle)
                    driver.click_Xpath(tmpEle)
                except:
                    if i == 1:
                        print('当前没有被选中的告警方式，跳过')
                        break
                    if i == 3:
                        print('未取消默认系统告警')
        # 这里是点击已经告警方式的下拉框，此时该元素已经是空的了
        head = alarm_ele['alarm_push_non_select_range']
        tail = 'tr[%s]/td[6]/div/div/div[2]/span/span/i' % num
        tmpEle = head + tail
        sleep(1)
        driver.click_Xpath(tmpEle)
        sleep(2)
        # 点击系统告警和邮件告警
        head = alarm_ele['alarm_awy_select_range']
        for i in range(1, 4):
            tail = 'li[%s]/span' % i
            tmpEle = head + tail
            txt = driver.gettxt_Xpanth(tmpEle)
            print(txt, end=',')
            if txt == '系统提醒' or txt == '邮件提醒':
                driver.click_Xpath(tmpEle)
        print()
        # 现在开始弄 推送管理 的东西了
        driver.click_Xpath(alarm_ele['push_manage'])
        driver.click_Xpath(alarm_ele['ali_email_button'])
        driver.clearAndSend_Xpath(alarm_ele['ali_access_key_id_input'], xpanelInfo['ali_access_key'])
        driver.clearAndSend_Xpath(alarm_ele['ali_secret_key_input'], xpanelInfo['ali_access_id'])
        driver.clearAndSend_Xpath(alarm_ele['ali_email_access_input'], xpanelInfo['ali_email'])
        driver.click_Xpath(alarm_ele['push_manage_email_save_button'])
        # 现在所有告警的配置都已经配置完毕

        # 开始不间断kill其中一个主存储节点
        db_host = dbInfo[0].replace(' ', '')
        db_port = dbInfo[1].replace(' ', '')
        kill_com = "ps -ef | grep %s | awk \'{print \$2}\' | xargs kill -9 > /dev/null 2>&1" % db_port
        ssh_com = 'ssh %s@%s \"%s\"' % ('kunlun', db_host, kill_com)
        command = 'for i in `seq 1 30000`; do %s ; done' % (ssh_com)
        print(command)
        def run(command):
            subprocess.run(command, shell=True)
        p = Thread(target=run, args=[command])
        p.start()
        sleep(60)
        # 开始筛选 存储节点异常 的类型
        driver.click_Xpath(alarm_ele['close_alarm_set_button'])
        driver.click_Xpath(alarm_ele['select_alarm_type'])
        for div in range(3, 6):
            for li in range(1, 18):
                ele1 = alarm_ele['select_alarm_type_range1'] + '[%s]' % div
                ele2 = alarm_ele['select_alarm_type_range2'] + 'li[%s]/span' % li
                tmpEle = ele1 + ele2
                try:
                    txt = driver.gettxt_Xpanth(tmpEle)
                    print(txt, end=',')
                    if txt == '存储节点异常':
                        print(tmpEle)
                        break
                except:
                    break
            if txt == '存储节点异常':
                break
            print(div)
        sleep(2)
        print(tmpEle)
        driver.moveToXpanth(tmpEle)
        sleep(3)
        driver.click_Xpath(tmpEle)
        compare_str = '%s_%s' % (db_host, db_port)
        the_first_alarm_info = driver.gettxt_Xpanth(alarm_ele['the_first_alarm_info'])
        times = 1
        while the_first_alarm_info != compare_str:
            times += 1
            the_first_alarm_info = driver.gettxt_Xpanth(alarm_ele['the_first_alarm_info'])
            if times == 5:
                print('未找到对应的异常告警，失败')
                return ['告警能力', 0]
        # 现在去获取最新一个邮件及验证其邮件正确性
        subprocess.run('python3 ./bin/getEmail.py > tmp.txt', shell=True)
        with open('tmp.txt', 'r') as f:
            msg = f.read()
        print(msg)
        #head = msg.split('--------------------')[0]
        #txt = msg.split('--------------------')[1]
        #title = head.split(':')[-1].split('part')[0]