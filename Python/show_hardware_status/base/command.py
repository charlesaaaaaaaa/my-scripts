class comm():
    def __init__(self, ip, user):
        self.ip = ip
        self.half_comm = 'ssh %s@%s ' % (user, ip)

    def cpu(self):
        comm = self.half_comm
        cpu_c = "'date;mpstat' >> ./result/%s/cpu 2>&1" % self.ip
        comm += cpu_c
        return comm

    def mem(self):
        comm = self.half_comm
        mem_c = "'date;free -h' >> ./result/%s/mem 2>&1" % self.ip
        comm += mem_c
        return comm

    def net(self):
        comm = self.half_comm
        net_c = "'date; sudo iftop -ts 1 -o 2s' >> ./result/%s/net 2>&1" % self.ip
        comm += net_c
        return comm

    def disk(self):
        comm = self.half_comm
        disk_c = "'date; iostat -dxh' >> ./result/%s/disk 2>&1" % self.ip
        comm += disk_c
        return comm