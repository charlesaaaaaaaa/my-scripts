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
    global dnsname, dnshost, dnsport, dnsdata, dnsuser, dnspooler, dnsmname, dnsmport, dnsmhost

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
        Dnsmname = i["Master_name"]
        Dnsmhost = i["Master_host"]
        dnshost.append(Dnshost)
        dnsport.append(Dnsport)
        dnsdata.append(Dnsdata)
        dnsuser.append(Dnsuser)
        dnspooler.append(Dnspooler)
        dnsname.append(Dnsname)
        dnsmport.append(Dnsmport)
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
    
    # scp package & env file to every instance
    for i in ahost:
        stmt = 'scp' + ' ' + package + ' ' + defuser + '@' + i + ':' + defbase
        stmt3 = 'scp' + ' ./env.sh ' + defuser + '@' + i + ':' + defbase
        stmt5 = 'scp' + ' ./install.sh ' + defuser + '@' + i + ':' + defbase
        print(stmt)
        print(stmt3)
    print()
    
    # init gtm master node
    gtminit = 'initgtm -Z gtm -D ' + gtmdata[0]
    print(gtminit)

    print(type(gtmhost[0]))
    # change gtm configuration
    sgtmport=str(gtmport[0])
    gtmconf = '/bin/bash ./install.sh gtm ' + gtmhost[0] + ' ' + sgtmport[0] + ' ' + gtmname[0] + ' ' + gtmdata[0] + ' ' + gtmuser[0]
    print(gtmconf)



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
