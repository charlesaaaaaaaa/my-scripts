import subprocess
from res.getconf import *
from res.connection import *

class getFile():
    def __init__(self, hosts):
        self.hosts = hosts
        self.user = readcnf().getKunlunInfo()['sys_user']

    def replaceTxtRow(self, paths, txt, replace_value):
        user = self.user
        ssh_c = "ssh %s@%s " % (user, self.hosts)
        cat_c = 'cat %s | grep -nw "%s" ' % (paths, txt)
        awk_c = '| awk -F: "{print \$1"}'
        find_line = ssh_c + "'" + cat_c + awk_c + "'"
        lines = subprocess.Popen(find_line, shell=True, stdout=subprocess.PIPE)
        linetxt = lines.stdout.read()
        try:
            lineNum = int(linetxt.decode('utf-8').split('\n')[-2])
            try:
                if int(replace_value):
                    sed_c = "sed -i '%ss/.*/%s = %s/' %s" % (lineNum, txt, replace_value, paths)
            except:
                replace_value = replace_value.replace('"', '')
                sed_c = "sed -i \\\"%ss/.*/%s = '%s'/\\\" %s" % (lineNum, txt, replace_value, paths)
        except Exception as err:
            try:
                lineNum = int(linetxt.decode('utf-8'))
                sed_c = "sed -i '%ss/.*/%s = %s/' %s" % (lineNum, txt, replace_value, paths)
            except:
                sed_c = "echo '%s = %s' >> %s" % (txt, replace_value, paths)
        replace_c = ssh_c + '"' + sed_c + '"'
        print(replace_c)
        subprocess.run(replace_c, shell=True)

class restart_component():
    def __init__(self, hosts):
        self.hosts = hosts
        self.user = readcnf().getKunlunInfo()['sys_user']

    def restart_pg(self, baseDir, port):
        host = self.hosts
        user = self.user
        print('### restarting server - %s:%s' % (host, port))
        scriptDir = baseDir + '/scripts/'
        stopPg_c = 'cd %s; python2 %sstop_pg.py --port=%s' % (scriptDir, scriptDir, port)
        stopPg = "ssh %s@%s '%s'" % (user, host, stopPg_c)
        subprocess.run(stopPg, shell=True)

        startPg_c = 'cd %s; python3 %sstart_pg.py --port=%s' % (scriptDir, scriptDir, port)
        startPg = "ssh %s@%s '%s'" % (user, host, startPg_c)
        subprocess.run(startPg, shell=True)
        print('### restart server - %s:%s done' % (host, port))

    def restart_db(self, baseDir, port):
        host = self.hosts
        user = self.user
        print('### restarting storage - %s:%s' % (host, port))

        dba_toolsDir = baseDir + 'dba_tools/'
        stopDb_c = 'cd %s; bash %sstopmysql.sh %s' % (dba_toolsDir, dba_toolsDir, port)
        stopDb = "ssh %s@%s '%s'" % (user, host, stopDb_c)
        subprocess.run(stopDb, shell=True)

        startDb_c = 'cd %s; bash %sstartmysql.sh %s' % (dba_toolsDir, dba_toolsDir, port)
        startDb = "ssh %s@%s '%s'" % (user, host, startDb_c)
        subprocess.run(startDb, shell=True)
        print('### restart storage - %s:%s done' % (host, port))
