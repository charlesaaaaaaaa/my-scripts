import os
from configparser import ConfigParser

def Mode(mode):
    dir_path_config = 'config=' + os.path.abspath('./conf/config.conf')
    conf = ConfigParser()
    dir_path_log = 'log=' + os.path.abspath('log/file')
    info = '%s\n%s' % (dir_path_config, dir_path_log)
    if mode == 'regular':
        location = ['./']
    elif mode == 'review':
        location = ['base/api/', 'base/other/', 'base/srcTable/', './', 'base/']
    else:
        print('mode应为 "regular" 或者 "review"')
        exit(0)
    for i in location:
        with open(i+'.location.txt', 'w')as f:
            f.write(info)
        f.close()