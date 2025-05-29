from xpanel_case import verify_results
from bin import other_opt
import pymysql
import time

def my_conn(node_info, db, sql):
    conn = pymysql.connect(host=node_info[0], port=int(node_info[1]), user=node_info[2], password=node_info[3], db=db)
    cur = conn.cursor()
    cur.execute(sql)
    res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return res


def kill_metadata_master():
    conf = other_opt.getconf().getXpanelInfo()
    meta_infos = verify_results.Meta_Info().metadata_infos()

    def get_meta_master_slave(meta_infos):
        master_list, slave_list = [], []
        for meta_info in meta_infos:
            if meta_info[4] == 'source':
                master_list.append(meta_info)
            elif meta_info[4] == 'replica':
                slave_list.append(meta_info)
        return master_list, slave_list

    def get_mate_info(node_info):
        sql = 'select hostaddr, port, user_name, passwd, member_state from meta_db_nodes;'
        new_meta_infos = my_conn(node_info=node_info, db='kunlun_metadata_db', sql=sql)
        master, slave = get_meta_master_slave(new_meta_infos)
        return master, slave

    print('kill 掉主metadata节点')
    master_list, slave_list = get_meta_master_slave(meta_infos)
    shell_kill_meta_master = "ssh %s@%s \"ps -ef | grep %s | grep -v grep | awk '{print \$2}' | " \
                             "xargs kill -9\"" % (conf['sys_user'], master_list[0][0], master_list[0][1])
    other_opt.run_shell(shell_kill_meta_master)

    print('开始检查metadata主是否更换')
    master_list, slave_list = get_meta_master_slave(meta_infos)
    old_master = master_list[0]
    while old_master == master_list[0]:
        time.sleep(3)
        # 这里要用备节点去查，主可能刚被kill还没起来
        master_list, slave_list = get_mate_info(slave_list[0])
    # 当选出主的时候，应该查看所有meta节点是否都是同一个主节点
    print('等待60s后检查所有元数据节点主是否一致')
    time.sleep(60)
    master_list, slave_list = get_mate_info(master_list[0])
    for slave_node in slave_list:
        try:
            tmp_master, tmp_slave = get_mate_info(slave_node)
            diff_times = 0
            while tmp_master[0] not in master_list and diff_times <= 20:
                diff_times += 1
                tmp_master, tmp_slave = get_mate_info(slave_node)
                print('当前metadata主节点数量大于1个，分别是%s和%s, 5秒后再次检查' % (str(master_list), str(tmp_master)))
                time.sleep(5)
            if diff_times > 20 and tmp_master[0] not in master_list:
                print('20次检查metadata主节点数大于1个，故本用例失败')
                return 0
        except Exception as err:
            print(err)
            return 0
    return 1


def kill_cluster_mgr_master():
    conf = other_opt.getconf().getXpanelInfo()

    # 这里把主节点和备节点分开放到不同的列表里面
    def get_cluster_master_slave():
        cluster_infos = verify_results.Meta_Info().clustermgr_infos()
        master_lsit, slave_list = [], []
        for node in cluster_infos:
            if node[2] == 'source':
                master_lsit.append(node)
            elif node[2] == 'replica':
                slave_list.append(node)
        return master_lsit, slave_list

    master_list, salve_list = get_cluster_master_slave()
    print('kill 掉主cluster_mgr节点, 当前主节点是 %s ' % master_list[0])
    shell_kill_meta_master = "ssh %s@%s \"ps -ef | grep %s | grep -v grep | awk '{print \$2}' | " \
                             "xargs kill -9\"" % (conf['sys_user'], master_list[0][0], master_list[0][1])
    other_opt.run_shell(shell_kill_meta_master)
    old_master = master_list[0]
    print('开始检查cluster_mgr节点是否切换成功')
    # 当老的主节点和现在的主节点一样说明没有切换完成
    while old_master == master_list[0]:
        time.sleep(3)
        master_list, salve_list = get_cluster_master_slave()
    show_times = 0
    while len(master_list) > 1 and show_times <= 20:
        show_times += 1
        master_list, salve_list = get_cluster_master_slave()
        print('第[%s]检查，当前cluster_mgr主节点数量大于1个，%s' % (show_times, master_list))
        time.sleep(5)
    if show_times > 20 and len(master_list) > 1:
        print('检查20次cluster_mgr主节点数量依旧大于1，故本用例失败')
        return 0
    return 1


def restart_xpanel_server():
    status_list = []
    conf = other_opt.getconf().getXpanelInfo()
    xpanel_name = 'xpanel_%s' % conf['port']
    shell_stop_xpanel = 'ssh %s@%s "sudo docker stop %s"' % (conf['sys_user'], conf['host'], xpanel_name)
    shell_start_xpanel = 'ssh %s@%s "sudo docker start %s"' % (conf['sys_user'], conf['host'], xpanel_name)
    shell_show_shatus = 'ssh %s@%s "sudo docker ps -a | grep %s"' % (conf['sys_user'], conf['host'], xpanel_name)

    # 查看xpanel的容器状态
    def show_status():
        status = ''
        res = other_opt.run_shell(shell_show_shatus)
        if "Exited (" in res:
            status = 'esited'
        elif "Up " in res:
            status = 'up'
        return status

    # 开始运行这两个停止和启动的命令
    for shell_comm in shell_stop_xpanel, shell_start_xpanel:
        other_opt.run_shell(shell_comm)
        time.sleep(1)
        # 然后各获取一次docker状态
        status = show_status()
        status_list.append(status)

    # 只要不是第一次的状态是退出且第二次的状态是运行的情况都是错误失败的
    if status_list[0] == 'esited' and status_list[1] == 'up':
        res = 1
    else:
        res = 0

    return res
