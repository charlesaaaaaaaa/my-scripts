from res.getconf import *
from res.test import *
from time import sleep

if __name__ == "__main__":
    necInfo = readcnf().get_necessary_info()
    action_list = necInfo['action'].replace(' ', '').split(',')
    caseLen = len(necInfo['case'].replace(' ', '').split(','))
    threadLen = len(necInfo['threads'].replace(' ', '').split(','))
    sleeptime = int(necInfo['sleeptime'])
    time = int(necInfo['time'])
    run_time = caseLen * threadLen * (time + sleeptime + 1)
    action = action()
    for act in action_list:
        if act == 'prepare':
            action.prepare()
        elif act == 'run':
            action.run()
            sleep(sleeptime)
        elif act == 'cleanup':
            action.cleanup()

