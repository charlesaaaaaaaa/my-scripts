from base.connection import *
import random
from base.other import OPT
import psycopg2

class typeloader():
    def __init__(self):
        pass

    def genData(self, dataType):
        if dataType == 'integer' or dataType == 'int':
            res = random.randint(-2147483648, 2147483647)
        elif dataType == 'smallint':
            res = random.randint(-32768, 32767)
        elif dataType == 'bigint':
            res = random.randint(-9223372036854775808, 9223372036854775807)
        elif dataType == 'numeric':
            res = random.uniform(0, 10**44-1)
        elif dataType == 'real':
            res = random.uniform(0, 10**5-1)
        elif dataType == 'double precision':
            res = random.uniform(0, 10**16-1)
        elif dataType == 'money':
            res = random.uniform(-92233720368547758.08, +92233720368547758.07)
        elif dataType == 'character varying' or dataType == "character":
            res = OPT.randstr(32)
            res = "'%s'" % res
        elif dataType == 'text':
            res = OPT.randstr(100)
            res = "'%s'" % res
        elif dataType == 'date':
            res = OPT.randdate()
            res = "'%s'" % res
        elif dataType == 'time' or dataType == "time without time zone":
            res = OPT.randtime()
            res = "'%s'" % res
        elif dataType == "time with time zone":
            res = OPT.randtimez()
            res = "'%s'" % res
        elif dataType == "timestamp" or dataType == "timestamp without time zone":
            res = OPT.randtimestamp()
            res = "'%s'" % res
        elif dataType == "timestamp with time zone":
            res = OPT.randtimestampz()
            res = "'%s'" % res
        elif dataType == "macaddr" or dataType == "macaddr8":
            res = OPT.randMac()
            res = "'%s'" % res
        elif dataType == "cidr" or dataType == "inet":
            res = OPT.randnet()
            res = "'%s'" % res
        elif dataType == "boolean":
            res = random.choices(('TRUE', 'FALSE'))[0]
        elif dataType == "bytea":
            res = str(OPT.randstr(16))
            res = "'%s'" % res
        elif dataType == "bit":
            res = OPT.randbit(16)
            res = "'%s'" % res
        return res

# print(typeloader().genData("boolean"))
