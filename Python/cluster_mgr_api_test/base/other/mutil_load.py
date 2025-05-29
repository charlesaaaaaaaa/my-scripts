from base.other import connect
from base.other import info


class LoadPg:
    def __init__(self, pginfo_list):
        # pginfo_list = [host, port, user, pass]
        self.pg_list = pginfo_list

    def run(self, process=None, thread=None, data_size=10000, db='testdb', table='testtb'):
        pass
