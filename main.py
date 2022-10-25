#!/usr/bin/python3
import logging
import yaml
import schedule, time

# Get Configuration Values
with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

def main():
    logger = logging.getLogger()
    fhandler = logging.FileHandler(filename='/opt/transferbuddy/transferbuddy.log', mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    logger.setLevel(logging.DEBUG)
    
    from threading import Thread

    from apt_mirror.apt_mirror_run import runaptmirror
    from yum_mirror.yum_mirror_run import runyummirror
    from container_mirror.container_mirror_run import runcontainermirror

    def callaptmirror():
        Thread(target = runaptmirror).start()

    def callyummirror():
        Thread(target = runyummirror).start()

    def callcontainermirror():
        Thread(target = runcontainermirror).start()

    #s.enter(1, 1, callcontainermirror )
    schedule.every(cfg['apt']['frequency']).hours.do(callaptmirror)
    schedule.every(cfg['yum']['frequency']).hours.do(callyummirror)
    schedule.every(cfg['skopeo']['frequency']).seconds.do(callcontainermirror)

    # Loop so that the scheduling task
    # keeps on running all time.
    while True:
    
        # Checks whether a scheduled task
        # is pending to run or not
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    while True:
        main()
