from res.cluster_info import getStorage
from res.connection import *
from res.getconf import *
from res.system_opt import *
import threading
from time import sleep

class configure_storage():
    def __init__(self):
        self.Infos = getStorage().Infos()
        self.Paths = getStorage().Paths()
        self.variables = readcnf().storage_settings()

    def change_variables(self):
        Infos = self.Infos
        variables = self.variables

        print('\n## setting storage node ...')
        for host in Infos:
            for infos in Infos[host]:
                print('setting storage %s: %s' % (infos[0], infos[1]))
                conn = connMy(infos[0], infos[1], infos[2], infos[3], 'mysql')
                for key in variables:
                    sql = 'SET PERSIST %s = %s' % (key, variables[key])
                    conn.myNotReturn(sql)

    def show_variables(self):
        Infos = self.Infos
        variables = self.variables

        print('|--------|\n|storage |\n|--------|')
        for host in Infos:
            for infos in Infos[host]:
                print('\n-- %s: %s --' % (infos[0], infos[1]))
                conn = connMy(infos[0], infos[1], infos[2], infos[3], 'mysql')
                for key in variables:
                    sql = 'show variables like "%s"' % key
                    res = conn.myReturn(sql)[0][1]
                    print(' * %s = %s' % (key, res))

    def write_config_file(self):
        Path = self.Paths
        variables = self.variables

        print("\n## write storage config file ...")
        for host in Path:
            OF = getFile(host)
            for info in Path[host]:
                print("### %s: %s" % (host, info[1]))
                for key in variables:
                    OF.replaceTxtRow(info[1], key, variables[key])

    def restart(self):
        print('\n## restart stoarge node ...')
        Path = self.Paths

        def thread_worker(host, info1, info2):
            restart_component(host).restart_db(info1, info2)

        l = []
        for host in Path:
            for info in Path[host]:
                restart_component(host).restart_db(info[0], info[2])
                p = threading.Thread(target=thread_worker, args=[host, info[0], info[2]])
                l.append(p)
                p.start()
        for i in l:
            i.join()
        print('## sleep 30s')
        sleep(30)
