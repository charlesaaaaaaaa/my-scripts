from res.getconf import *
from res.test import *
from time import sleep

if __name__ == "__main__":
    action_list = readcnf().getDbInfo()['action'].replace(' ', '').split(',')
    for act in action_list:
        if act == 'prepare':
            action().prepare()
        elif act == 'run':
            action().run()
        elif act == 'cleanup':
            action().cleanup()

            