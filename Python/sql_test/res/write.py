import logging
import os.path


def to_other(file_name, txt):
    of = open(file_name, 'a')
    of.write(txt)

def to_log(txt, level=0):
    if level == 0:
        logging.log()
    pass