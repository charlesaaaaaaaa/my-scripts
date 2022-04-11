import json
import argparse
from time import sleep
import psycopg2

File="./install.json"

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

    # create env file
    print('deploy packages')
    f = open('./env.sh', 'w')
    stmt1 = 'export PATH=' + defbase + '/bin:$PATH'
    stmt2 = 'export LD_LIBRARY_PATH=' + defbase + '/lib:$LD_LIBRARY_PATH'
    f.write(stmt1 + '\n' + stmt2 + '\n')
    
    # scp package & env file to each instance ======================
    for i in ahost:
        stmt = 'scp' + ' ' + package + ' ' + defuser + '@' + i + ':' + defbase
        stmt3 = 'scp' + ' ./env.sh ' + defuser + '@' + i + ':' + defbase
        stmt5 = 'scp' + ' ./install.sh ' + defuser + '@' + i + ':' + defbase
        print(stmt)
        print(stmt3)
    print()
    
    # -------------------------- gtm -------------------------------------
    # init gtm master node ==================================
    print('\n ======== creating gtm master node ======== \n')
    initgtm = 'initgtm -Z gtm -D ' + gtmdata[0]
    print(initgtm)

    # change gtm configuration ===================================
    gtmconf = '/bin/bash ' + defbase + '/install.sh gtm ' + gtmhost[0] + ' ' + str(gtmport[0]) + ' ' + gtmname[0] + ' ' + gtmdata[0] + ' ' + gtmuser[0]
    print(gtmconf)

    # start gtm =============================
    startgtm = 'gtm_ctl -Z gtm -D ' + gtmdata[0] + ' start'
    print(startgtm)

    # -------------------------- gtm slave -----------------------------
    n = 0
    print('\n ======== creating gtm slave node ========')
    for i in gtmshost:
        print('\n creating gtm slave node ' + gtmsname[n])
        # init gtm slave node ====================
        initgtms = 'initgtm -Z gtm -D ' + gtmsdata[n]
        print(initgtms)
        
        # change gtm slave configuration =====================
        gtmsconf = '/bin/bash ' + defbase + '/install.sh gtm_slave ' + gtmhost[0] + ' '  + str(gtmsport[n]) + ' ' + ' '  + gtmsname[n] + ' ' + gtmsdata[n] + ' ' + gtmsuser[0]
        print(gtmsconf)

        #start gtm slave ==================
        startgtms = 'gtm_ctl -Z gtm -D ' + gtmsdata[n] + ' start'
        print(startgtms)
        
        n = n + 1
    
    # ------------------------- cn node --------------------------------
    n = 0
    print('\n ======== creating cn node ========')
    #initdb --locale=zh_CN.UTF-8 -U kunlun -E utf8 -D /home/kunlun/TPC/postgres-xz/data/cn01 --nodename=cn01 --nodetype=coordinator --master_gtm_nodename gtm --master_gtm_ip 192.168.0.134 --master_gtm_port 23001
    for i in cnhost:
        print('\n creating cn node ' + cnname[n])
        # init cn node ===============
        initcn = 'initdb --locale=zh_CN.UTF-8 -U ' + cnuser[n] + ' -E utf8 -D ' + cndata[n] + '--nodename=' + cnname[n] + ' --nodetype=coordinator --master_gtm_nodename ' + gtmname[0] + ' --master_gtm_ip ' + gtmhost[0] + ' --master_gtm_port ' + str(gtmport[0])
        print(initcn)
        
        # change cn node configuration =============
        cnconf = '/bin/bash ' + defbase + '/install.sh cn ' + str(cnport[n]) + ' ' + str(cnpooler[n]) + ' ' + cndata[n]
        print(cnconf)

        # start cn node =================
        startcn = 'pg_ctl -Z coordinator -D ' + cndata[n] + ' start'
        reloadcn = 'pg_ctl -D ' + cndata[n] + ' reload'

        n = n + 1

    # ------------------------- dn node --------------------------------
    n = 0
    print('\n ======== creating dn master node ========')
    for i in dnhost:
        print('\n creating dn node ' + dnname[n])
        # init dn node ===============
        initdn = 'initdb --locale=zh_CN.UTF-8 -U ' + dnuser[n] + ' -E utf8 -D ' + dndata[n] + '--nodename=' + dnname[n] + ' --nodetype=datanode --master_gtm_nodename ' + gtmname[0] + ' --master_gtm_ip ' + gtmhost[0] + ' --master_gtm_port ' + str(gtmport[0])
        print(initdn)

        # change dn configuration ====================
        dnconf = '/bin/bash ' + defbase + '/install.sh dn ' + str(dnport[n]) + ' ' + str(dnpooler[n]) + ' ' + dndata[n]
        print(dnconf)

        # start dn node =================
        startdn = 'pg_ctl -Z datanode -D ' + dndata[n] + ' start'
        reloaddn = 'pg_ctl -D ' + dndata[n] + ' reload'

        n = n + 1

    # ----------------------- dn slave node --------------------------
# pg_basebackup -p 23003 -h 192.168.0.132 -U kunlun -D /home/kunlun/TPC/postgres-xz/data/dn01s1 -X f -P -v
    n = 0
    print('\n ======== creating dn slave node ========')
    for i in dnshost:
        print('\n creating dns node ' + dnsname[n])
        # init dns node ===============
        initdns = 'pg_basebackup -p ' + dnsmport[n] + ' -h ' + dnsmhost[n] + ' -U ' + dnsuser[n] + ' -D ' + dnsdata[n] + ' -X f -P -v'
        print(initdns)

        # change dns configuration ==================
        dnsconf = '/bin/bash ' + defbase + '/install.sh dn_slave ' + str(dnsport[n]) + ' ' + str(dnspooler[n]) + ' ' + dnsdata[n] + ' ' + dnsmhost[n]  + ' ' + dnsmport[n]  + ' ' + dnsmuser[n]  + ' ' + dnsmname[n]
        print(dnsconf)

        # start dns node ==================
        startdns = 'pg_ctl -Z datanode -D ' + dnsdata[n] + ' start'
        reloaddns = 'pg_ctl -D ' + dnsdata[n] + ' reload'

        n = n + 1

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = 'the pgxz/pgxl/pgxc install script.')
    parser.add_argument('--type', default='pgxz', help = 'pgxc, pgxz, pgxl')
    parser.add_argument('--config', default='install.json', help = 'the config json file')
    parser.add_argument('--defbase', default='/home/kunlun/compare/test/base', help = 'default basedir')
    parser.add_argument('--defuser', default='user', help = 'default user')
    parser.add_argument('--package', default='package', help = 'the package of pgxz/xl/xc')
    args = parser.parse_args()
    File = args.config
    defbase = args.defbase
    defuser = args.defuser
    package = args.package
    print(args)
    readJsonFile()
    install()

    #print('gtm\n', gtmhost,'\n', gtmport, '\n', gtmdata, '\n',gtmuser, '\n', gtmname, '\n' , '\ngtm_slave \n',gtmshost, '\n', gtmsport, '\n', gtmsdata, '\n', gtmsuser, '\n', gtmsname, '\n', '\ncn\n', cnhost, '\n', cnport, '\n', cndata, '\n', cnuser, '\n', cnname, '\n', '\ndn\n', dnhost, '\n', dnport, '\n', dndata, '\n', dnuser, '\n', dnname, '\n', dnpooler, '\n', '\ndn_slave \n', dnshost, '\n', dnsport, '\n', dnsdata, '\n', dnsuser, '\n', dnspooler, '\n', dnsname, '\n', dnsmport, '\n', dnsmname, '\n', dnsmhost)
