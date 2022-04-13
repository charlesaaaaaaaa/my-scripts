import json
import argparse
from time import sleep
import psycopg2
import subprocess
import os
import signal

def connTemp(puser, phost, pport, stmt):
    conn = psycopg2.connect(database = 'postgres', user = puser, host = phost, port = pport)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(stmt)
    #res = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()

def makeTemp(host, path):
    stmt = 'ssh ' + defuser + '@' + host + " 'mkdir -p " + path + "'"
    subprocess.run(stmt, shell = True)
    print('ssh mkdir : ' + stmt)


def sshTemp(host, stmt, time):
    stmt = 'ssh ' + defuser + '@' + host + " 'cd " + defbase + ' && source env.sh && ' + stmt + "'"
    p = subprocess.Popen(stmt, shell = True)
    os.kill(p.pid, signal.SIGCONT)
    print('ssh common : ' + stmt)
    sleep(time)

def readJsonFile():
    Of = open(File,encoding='utf-8')
    Ofload = json.loads(Of.read())
    gtm = Ofload['gtm']
    gtms = Ofload['gtm_slave']
    cn = Ofload['coordinator']
    dn = Ofload['datanode']
    dns = Ofload['datanode_slave']
    
    global gtmhost, gtmport, gtmdata, gtmuser, gtmname
    global gtmshost, gtmsport, gtmsdata, gtmsuser, gtmsname
    global cnhost, cnport, cndata, cnuser, cnname, cnpooler
    global dnhost, dnport, dndata, dnuser, dnname, dnpooler
    global dnsname, dnshost, dnsport, dnsdata, dnsuser, dnspooler, dnsmname, dnsmuser, dnsmport, dnsmhost

    gtmhost = []
    gtmport = []
    gtmdata = []
    gtmuser = []
    gtmname = []
    
    gtmshost = []
    gtmsport = []
    gtmsdata = []
    gtmsuser = []
    gtmsname = []

    cnhost = []
    cnport = []
    cndata = []
    cnuser = []
    cnname = []
    cnpooler = []

    dnhost = []
    dnport = []
    dndata = []
    dnuser = []
    dnname = []
    dnpooler = []

    dnsname = []
    dnshost = []
    dnsport = []
    dnsdata = []
    dnsuser = []
    dnspooler = []
    dnsmname = []
    dnsmuser = []
    dnsmport = []
    dnsmhost = []
    

    for i in gtm:
        Gtmhost = i["host"]
        Gtmport = i["port"]
        Gtmdata = i["datadir"]
        Gtmuser = i["user"]
        Gtmname = i["name"]
        gtmhost.append(Gtmhost)
        gtmport.append(Gtmport)
        gtmdata.append(Gtmdata)
        gtmuser.append(Gtmuser)
        gtmname.append(Gtmname)
        

    for i in gtms:
        Gtmshost = i["host"]
        Gtmsport = i["port"]
        Gtmsdata = i["datadir"]
        Gtmsuser = i["user"]
        Gtmsname = i["name"]
        gtmshost.append(Gtmshost)
        gtmsport.append(Gtmsport)
        gtmsdata.append(Gtmsdata)
        gtmsuser.append(Gtmsuser)
        gtmsname.append(Gtmsname)

    for i in cn:
        Cnhost = i["host"]
        Cnport = i["port"]
        Cndata = i["datadir"]
        Cnuser = i["user"]
        Cnname = i["name"]
        Cnpooler = i["pooler_port"]
        cnhost.append(Cnhost)
        cnport.append(Cnport)
        cnuser.append(Cnuser)
        cndata.append(Cndata)
        cnname.append(Cnname)
        cnpooler.append(Cnpooler)

    for i in dn:
        Dnhost = i["host"]
        Dnport = i["port"]
        Dndata = i["datadir"]
        Dnuser = i["user"]
        Dnname = i["name"]
        Dnpooler = i["pooler_port"]
        dnhost.append(Dnhost)
        dnport.append(Dnport)
        dndata.append(Dndata)
        dnuser.append(Dnuser)
        dnname.append(Dnname)
        dnpooler.append(Dnpooler)

    for i in dns:
        Dnshost = i["host"]
        Dnsport = i["port"]
        Dnsdata = i["datadir"]
        Dnsuser = i["user"]
        Dnspooler = i["pooler_port"]
        Dnsname = i["name"]
        Dnsmport = i["Master_port"]
        Dnsmuser = i["Master_user"]
        Dnsmname = i["Master_name"]
        Dnsmhost = i["Master_host"]
        dnshost.append(Dnshost)
        dnsport.append(Dnsport)
        dnsdata.append(Dnsdata)
        dnsuser.append(Dnsuser)
        dnspooler.append(Dnspooler)
        dnsname.append(Dnsname)
        dnsmport.append(Dnsmport)
        dnsmuser.append(Dnsmuser)
        dnsmname.append(Dnsmname)
        dnsmhost.append(Dnsmhost)


def install():
    allhost = []
    allhost.extend(gtmhost)
    allhost.extend(gtmshost)
    allhost.extend(dnhost)
    allhost.extend(cnhost)
    allhost.extend(dnshost)
    ahost = list(set(allhost))
    #print(ahost)

    pakname = package.replace('./','')
    pakname = pakname.replace('.tgz','')

    # create env file
    print('======== deploy packages ========')
    f = open('./env.sh', 'w')
    stmt1 = 'export PATH=' + defbase + '/' + pakname + '/bin:$PATH'
    stmt2 = 'export LD_LIBRARY_PATH=' + defbase + '/' + pakname + '/lib:$LD_LIBRARY_PATH'
    f.write(stmt1 + '\n' + stmt2 + '\n')
    f.close()

    # scp package & env file to each instance ======================
    for i in ahost:
        stmt = 'scp' + ' ' + package + ' ' + defuser + '@' + i + ':' + defbase
        stmt3 = 'scp' + ' ./env.sh ' + defuser + '@' + i + ':' + defbase
        stmt5 = 'scp' + ' ./install.sh ' + defuser + '@' + i + ':' + defbase
        subprocess.run(stmt, shell = True)
        print(stmt)
        subprocess.run(stmt3, shell = True)
        print(stmt3)
        subprocess.run(stmt5, shell = True)
        print(stmt5)
        stmt7 = 'tar -zxf ' + defbase + '/' + package
        sshTemp(i, stmt7, 1)
    print()
    
    # -------------------------- gtm -------------------------------------
    # init gtm master node ==================================
    print('\n ======== creating gtm master node ======== \n')
    makeTemp(gtmhost[0], gtmdata[0])
    initgtm = 'initgtm -Z gtm -D ' + gtmdata[0]
    sshTemp(gtmhost[0], initgtm, 1) 

    # change gtm configuration ===================================
    gtmconf = '/bin/bash ' + defbase + '/install.sh gtm ' + gtmhost[0] + ' ' + str(gtmport[0]) + ' ' + gtmname[0] + ' ' + gtmdata[0] + ' ' + gtmuser[0]
    sshTemp(gtmhost[0], gtmconf, 1)

    # start gtm =============================
    startgtm = 'gtm_ctl -Z gtm -D ' + gtmdata[0] + ' start'
    sshTemp(gtmhost[0], startgtm, 1)

    # -------------------------- gtm slave -----------------------------
    n = 0
    print('\n ======== creating gtm slave node ========')
    for i in gtmshost:
        makeTemp(i, gtmsdata[n])
        print('\n creating gtm slave node ' + gtmsname[n])
        # init gtm slave node ====================
        initgtms = 'initgtm -Z gtm -D ' + gtmsdata[n]
        sshTemp(i, initgtms, 1)
        
        # change gtm slave configuration =====================
        gtmsconf = '/bin/bash ' + defbase + '/install.sh gtm_slave ' + gtmhost[0] + ' '  + str(gtmsport[n]) + ' ' + gtmsname[n] + ' ' + gtmsdata[n] + ' ' + str(gtmport[0])
        sshTemp(i, gtmsconf, 1)

        #start gtm slave ==================
        startgtms = 'gtm_ctl -Z gtm_standby -D ' + gtmsdata[n] + ' start'
        sshTemp(i, startgtms, 1)

        n = n + 1
    
    # ------------------------- cn node --------------------------------
    n = 0
    print('\n ======== creating cn node ========')
    #initdb --locale=zh_CN.UTF-8 -U kunlun -E utf8 -D /home/kunlun/TPC/postgres-xz/data/cn01 --nodename=cn01 --nodetype=coordinator --master_gtm_nodename gtm --master_gtm_ip 192.168.0.134 --master_gtm_port 23001
    for i in cnhost:
        makeTemp(i, cndata[n])
        print('\n ==========creating cn node ' + cnname[n])
        # init cn node ===============
        if type == 'pgxz':
            initcn = 'initdb --locale=en_US.UTF-8 -U ' + cnuser[n] + ' -E utf8 -D ' + cndata[n] + ' --nodename=' + cnname[n] + ' --nodetype=coordinator --master_gtm_nodename ' + gtmname[0] + ' --master_gtm_ip ' + gtmhost[0] + ' --master_gtm_port ' + str(gtmport[0])
            sshTemp(i, initcn, 3)

        else if type = 'pgxc':
            initcn = 'initdb -D ' + cndata[n] + ' --nodename ' + cnname[n]
            sshTemp(i, initcn, 3)
        
        # change cn node configuration =============
        cnconf = '/bin/bash ' + defbase + '/install.sh cn ' + str(cnport[n]) + ' ' + str(cnpooler[n]) + ' ' + cndata[n] + ' ' + gtmhost[0] + ' ' + gtmport[0]
        sshTemp(i, cnconf, 1)

        # start cn node =================
        if type == 'pgxz':
            startcn = 'pg_ctl -Z coordinator -D ' + cndata[n] + ' start'
            reloadcn = 'pg_ctl -D ' + cndata[n] + ' reload'
            sshTemp(i, startcn, 6)
            sshTemp(i, reloadcn, 1)
        
        else if type == 'pgxc':
            startcn == 'postgres --coordinator -D ' + cndata[n]
            sshTemp(i, startcn, 6)

        n = n + 1

    # ------------------------- dn node --------------------------------
    n = 0
    print('\n ======== creating dn master node ========')
    for i in dnhost:
        makeTemp(i, dndata[n])
        print('\n ================creating dn node ' + dnname[n])
        # init dn node ===============
        initdn = 'initdb --locale=en_US.UTF-8 -U ' + dnuser[n] + ' -E utf8 -D ' + dndata[n] + ' --nodename=' + dnname[n] + ' --nodetype=datanode --master_gtm_nodename ' + gtmname[0] + ' --master_gtm_ip ' + gtmhost[0] + ' --master_gtm_port ' + str(gtmport[0])
        sshTemp(i, initdn, 3)

        # change dn configuration ====================
        dnconf = '/bin/bash ' + defbase + '/install.sh dn ' + str(dnport[n]) + ' ' + str(dnpooler[n]) + ' ' + dndata[n] + ' ' + gtmhost[0] + ' ' + gtmport[0]
        sshTemp(i, dnconf, 1)

        # start dn node =================
        startdn = 'pg_ctl -Z datanode -D ' + dndata[n] + ' start'
        reloaddn = 'pg_ctl -D ' + dndata[n] + ' reload'
        sshTemp(i, startdn, 6)
        sshTemp(i, reloaddn, 1)

        n = n + 1

    # ----------------------- dn slave node --------------------------
# pg_basebackup -p 23003 -h 192.168.0.132 -U kunlun -D /home/kunlun/TPC/postgres-xz/data/dn01s1 -X f -P -v
    n = 0
    print('\n ======== creating dn slave node ========')
    for i in dnshost:
        makeTemp(i, dnsdata[n])
        print('\n ==============creating dns node ' + dnsname[n])
        # init dns node ===============
        initdns = 'pg_basebackup -p ' + dnsmport[n] + ' -h ' + dnsmhost[n] + ' -U ' + dnsuser[n] + ' -D ' + dnsdata[n] + ' -X f -P -v'
        sshTemp(i, initdns, 2)

        # change dns configuration ==================
        dnsconf = '/bin/bash ' + defbase + '/install.sh dn_slave ' + str(dnsport[n]) + ' ' + str(dnspooler[n]) + ' ' + dnsdata[n] + ' ' + dnsmhost[n]  + ' ' + dnsmport[n]  + ' ' + dnsmuser[n]  + ' ' + dnsmname[n]
        changedir = 'chmod 700 ' + dnsdata[n]
        sshTemp(i, dnsconf, 1)
        sshTemp(i, changedir, 1)

        # start dns node ==================
        startdns = 'pg_ctl -Z datanode -D ' + dnsdata[n] + ' start'
        reloaddns = 'pg_ctl -D ' + dnsdata[n] + ' reload'
        sshTemp(i, startdns, 3)
        sshTemp(i, reloaddns, 1)

        n = n + 1

def ConfigRoute():

    # 配置路由
    print('\n======== Configration Route ========')
    cof = ['cn','dn']
    for i in cof:
        if i == 'cn':
            ns = 0
            for a in cnhost:
                print('\npsql -h '+ cnhost[ns] + ' -d postgres -p ' + str(cnport[ns]))
                for b in cof:
                    if b == 'cn':
                        n = 0
                        for c in cnhost:
                            if c == a:
                                stmt = 'alter node ' + cnname[n] + " with(host='" + c + "',port=" + str(cnport[n]) + ')'
                                print(cnuser[ns],cnhost[ns], cnport[ns],stmt)
                                connTemp(cnuser[ns], cnhost[ns], cnport[ns], stmt)
                                n = n + 1
                            else:
                                stmt = 'create node ' + cnname[n] + " with(type=coordinator,host='" + c + "',port=" + str(cnport[n]) + ',primary=false,preferred=false)'
                                print(cnuser[ns], cnhost[ns], cnport[ns],stmt)
                                connTemp(cnuser[ns], cnhost[ns], cnport[ns], stmt)
                                n = n + 1
                    else:
                        n = 0
                        for c in dnhost:
                            stmt = 'create node ' + dnname[n] + " with(type=datanode,host='" + c + "',port=" + str(dnport[n]) + ',primary=false,preferred=false)'
                            print(cnuser[ns], cnhost[ns], cnport[ns],stmt)
                            connTemp(cnuser[ns], cnhost[ns], cnport[ns], stmt)
                            n = n + 1
                ns = ns + 1
        if i == 'dn':
            nn = 0
            for a in dnhost:
                print('\npsql -h '+ dnhost[nn] + ' -d postgres -p ' + str(dnport[nn]))
                for b in cof:
                    if b == 'dn':
                        n = 0
                        for c in dnhost:
                            if c == a:
                                stmt = 'alter node ' + dnname[n] + " with(host='" + c + "',port=" + str(dnport[n]) + ')'
                                print(dnuser[nn], dnhost[nn], dnport[nn],stmt)
                                connTemp(dnuser[nn], dnhost[nn], dnport[nn], stmt)
                                n = n + 1
                            else:
                                stmt = 'create node ' + dnname[n] + " with(type=datanode,host='" + c + "',port=" + str(dnport[n]) + ',primary=false,preferred=false)'
                                print(dnuser[nn], dnhost[nn], dnport[nn], stmt)
                                connTemp(dnuser[nn], dnhost[nn], dnport[nn], stmt)
                                n = n + 1
                    else:
                        n = 0
                        for c in cnhost:
                            stmt = 'create node ' + cnname[n] + " with(type=coordinator,host='" + c + "',port=" + str(cnport[n]) + ',primary=false,preferred=false)'
                            print(cnuser[nn], cnhost[nn], cnport[nn], stmt)
                            connTemp(dnuser[nn], dnhost[nn], dnport[nn], stmt)
                            n = n + 1
                nn = nn + 1
    
    print('\ncreating sharding')
    alldn = ''
    for i in dnname:
        if i == dnname[0]:
            alldn = i
        else:
            alldn = alldn + ',' + i
    stmt1 = 'create default node group default_group with(' + alldn + ')'
    stmt2 = 'create sharding group to group default_group'
    stmt3 = 'clean sharding'
    print(stmt1 + '\n' + stmt2 + '\n' + stmt3 + '\n')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'the pgxz/pgxl/pgxc install script.')
    parser.add_argument('--type', default='pgxz', help = 'pgxc, pgxz, pgxl')
    parser.add_argument('--config', default='install.json', help = 'the config json file')
    parser.add_argument('--defbase', default='/home/kunlun/compare/postgres-xz/base', help = 'default basedir')
    parser.add_argument('--defuser', default='kunlun', help = 'default user')
    parser.add_argument('--package', default='package', help = 'the package of pgxz/xl/xc')
    args = parser.parse_args()
    File = args.config
    defbase = args.defbase
    defuser = args.defuser
    package = args.package
    print(args)
    readJsonFile()
    install()
    ConfigRoute()

    #print('gtm\n', gtmhost,'\n', gtmport, '\n', gtmdata, '\n',gtmuser, '\n', gtmname, '\n' , '\ngtm_slave \n',gtmshost, '\n', gtmsport, '\n', gtmsdata, '\n', gtmsuser, '\n', gtmsname, '\n', '\ncn\n', cnhost, '\n', cnport, '\n', cndata, '\n', cnuser, '\n', cnname, '\n', '\ndn\n', dnhost, '\n', dnport, '\n', dndata, '\n', dnuser, '\n', dnname, '\n', dnpooler, '\n', '\ndn_slave \n', dnshost, '\n', dnsport, '\n', dnsdata, '\n', dnsuser, '\n', dnspooler, '\n', dnsname, '\n', dnsmport, '\n', dnsmname, '\n', dnsmhost)
