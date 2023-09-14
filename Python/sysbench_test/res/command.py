from res.getconf import *

class sysbench_command():
    def __init__(self):
        self.dbInfo = readcnf().getDbInfo()
        self.necInfo = readcnf().get_necessary_info()
        self.otherInfo = readcnf().get_other_info()
        self.db_opts = '--tables=%s --table-size=%s --db-driver=%s --%s-user=%s --%s-password=%s --%s-db=%s ' \
                       '' % (self.necInfo['tables'], self.necInfo['table_size'], self.dbInfo['driver'],
                             self.dbInfo['driver'],self.dbInfo['user'], self.dbInfo['driver'], self.dbInfo['pwd'],
                             self.dbInfo['driver'], self.dbInfo['db'])

    def preapre(self):
        threads = self.necInfo['prepare_thread']
        db_opts = self.db_opts
        host = self.dbInfo['host'].replace(' ', '').split(',')[0]
        port = self.dbInfo['port'].replace(' ', '').split(',')[0]
        driver = self.dbInfo['driver']
        db_opts += '--%s-host=%s --%s-port=%s ' % (driver, host, driver, port)
        command = 'sysbench oltp_point_select %s --threads=%s prepare' % (db_opts, threads)
        return command

    def cleanup(self):
        db_opts = self.db_opts
        host = self.dbInfo['host'].replace(' ', '').split(',')[0]
        port = self.dbInfo['port'].replace(' ', '').split(',')[0]
        driver = self.dbInfo['driver']
        db_opts += '--%s-host=%s --%s-port=%s ' % (driver, host, driver, port)
        command = 'sysbench oltp_point_select %s cleanup' % db_opts
        return command

    def run(self, case, threads, position):
        db_opts = self.db_opts
        otherInfo = self.otherInfo
        host = self.dbInfo['host'].replace(' ', '').split(',')[position]
        port = self.dbInfo['port'].replace(' ', '').split(',')[position]
        time = int(self.necInfo['time'])
        driver = self.dbInfo['driver']
        db_opts += '--%s-host=%s --%s-port=%s --time=%s' % (driver, host, driver, port, time)
        otherOpt = ' '
        command = 'sysbench %s %s --threads=%s ' % (case, db_opts, threads)
        for i in otherInfo:
            opt = '--%s=%s ' % (i, otherInfo[i])
            otherOpt += opt
        command += otherOpt + ' run'
        return command