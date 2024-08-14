from res.config_my import *
from res.config_pg import *

def conf_storage():
    conf = readcnf().getKunlunInfo()
    configure_storage().change_variables()
    if conf['db_write_file'] == 'on':
        configure_storage().write_config_file()
    if conf['db_restart'] == 'on':
        configure_storage().restart()

def conf_server():
    configure_server().write_config_file()
    configure_server().restart()

def show_var():
    configure_server().show_variables()
    configure_storage().show_variables()

if __name__ == '__main__':
    conf = readcnf().getKunlunInfo()
    if conf['only_show_variables'] == 'on':
        show_var()
    elif conf['component'] == 'all':
        conf_server()
        conf_storage()
        show_var()
    elif conf['component'] == 'storage':
        conf_storage()
        configure_storage().show_variables()
    elif conf['component'] == 'server':
        conf_server()
        configure_server().show_variables()
