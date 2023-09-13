from res.cluster_info import getStorage
from res.connection import *
from res.getconf import *
from res.system_opt import *

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
                print('change storage == %s: %s' % (infos[0], infos[1]))
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

        for host in Path:
            OF = getFile(host)
            for info in Path[host]:
                for key in variables:
                    OF.replaceTxtRow(info[1], key, variables[key])

    def restart(self):
        print('\n## restart stoarge node ...')
        Path = self.Paths
        for host in Path:
            for info in Path[host]:
                print('resert storage %s: %s' % (host, info[2]))
                restart_component(host).restart_db(info[0], info[2])