from res.cluster_info import getServer
from res.connection import *
from res.getconf import *
from time import sleep
from res.system_opt import *

class configure_server():
    def __init__(self):
        self.Infos = getServer().Infos()
        self.Path = getServer().Paths()
        self.variables = readcnf().server_settings()

    def show_variables(self):
        Infos = self.Infos
        variables = self.variables

        print('|--------|\n| server |\n|--------|')
        for host in Infos:
            for infos in Infos[host]:
                print('-- %s: %s --' % (infos[0], infos[1]))
                conn = connPg()
                for key in variables:
                    sql = "show %s" % key
                    res = conn.pgReturn_other(infos[0], infos[1], infos[2], infos[3], sql)[0][0]
                    print(' * %s = %s' % (key, res))

    def write_config_file(self):
        Path = self.Path
        variables = self.variables

        print('\n## setting server node ...')
        for host in Path:
            OF = getFile(host)
            for info in Path[host]:
                print('setting server %s:%s' % (host, info[1]))
                for key in variables:
                    OF.replaceTxtRow(info[1], key, variables[key])

    def restart(self):
        Path = self.Path
        print('\n## restart server node ...')
        for host in Path:
            for info in Path[host]:
                print('resert server %s: %s' % (host, info[2]))
                restart_component(host).restart_pg(info[0], info[2])
        print('sleep 30s ...\n')
        sleep(30)
