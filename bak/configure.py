import subprocess
from time import sleep
import json

OpenCluster=open('install_nomgr.json', encoding='utf-8')
ReadCluster=json.loads(OpenCluster.read())

MetaTotal=ReadCluster['cluster']['meta']['nodes']
CompTotal=ReadCluster['cluster']['comp']['nodes']
DataTotal=ReadCluster['cluster']['data']

# get cluster info
MetaIp=[]
MetaPort=[]
MetaDir=[]
MetaUser=[]
CompIp=[]
CompPort=[]
CompDir=[]
CompUser=[]
DataIp=[]
DataPort=[]
DataDir=[]
DataUser=[]

for i in MetaTotal: #get metadata node info
    ip=i['ip']
    port=i['port']
    datadir=i['data_dir_path']
    user=i['user']
    MetaIp.append(ip)
    MetaPort.append(port)
    MetaDir.append(datadir)
    MetaUser.append(user)
    

for i in CompTotal: # get computing node info
    ip=i['ip']
    port=i['port']
    datadir=i['datadir']
    user=i['user']
    CompIp.append(ip)
    CompPort.append(port)
    CompDir.append(datadir)
    CompUser.append(user)

for i in DataTotal: # get data node info
    for a in i['nodes']:
        ip=a['ip']
        port=a['port']
        datadir=a['data_dir_path']
        user=a['user']
        DataIp.append(ip)
        DataPort.append(port)
        DataDir.append(datadir)
        DataUser.append(user)


print('Meta:', MetaIp, MetaPort, MetaDir, MetaUser, '\n','Comp:', CompIp, CompPort, CompDir, CompUser, '\n','Data:', DataIp, DataPort, DataDir, DataUser)

OpenConf=open("confs.json",encoding='utf-8') # get computing conf info
ReadConf=json.loads(OpenConf.read())

CompConf=ReadConf['comp'][0] # get data&metadata conf info
MedaConf=ReadConf['meta-storage'][0]

Compkeys=list(CompConf.keys())
Compvalues=list(CompConf.values())
Medakeys=list(MedaConf.keys())
Medavalues=list(MedaConf.values())

CompNum=len(Compkeys)
sCompNum = str(CompNum)
MedaNum=len(Medakeys)
print('CompNum=',CompNum,'\n',Compkeys,'\n', Compvalues, '\n', 'Medanum=', MedaNum, '\n', Medakeys, '\n', Medavalues)

CIPN=0
for i in CompIp:
    for a in range(0,CompNum):
        if Compvalues[a] :
            SCompkeys = ''.join(Compkeys[a])
            SCompDir = ''.join(CompDir[CIPN])
            SCompvalues = str(Compvalues[a])
            SCompUser = ''.join(MetaUser[CIPN])
            SCompIp = ''.join(CompIp[CIPN])
            
            of=open('config.sh','a')
            AddLine = "line=`cat %s/postgresql.conf | grep '%s =' | awk '{print $1}'` && " % (SCompDir,SCompkeys)
            SedDel = 'sed -i "${line}d" ' + SCompDir +'/postgresql.conf && '
            SedAdd = 'sed -i "${line}i ' + SCompkeys + ' = ' + SCompvalues + '"'
            BashStmt = AddLine + SedDel + SedAdd
            of.write("bash remote_run.sh --user=%s %s '%s'\n" %(SCompUser, SCompIp, BashStmt))
            of.close()
        else:
            err = 'Computing node' + CompId + ':' + CompPort + 'parameter :"' + Compkeys[ini] + '" not found'
            print(err)
    CIPN+=1
