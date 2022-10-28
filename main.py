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
    logger.setLevel(logging.INFO)
    
    from threading import Thread
    
    from apt_mirror.apt_mirror_run import runaptmirror
    from apt_mirror.apt_mirror_run import buildaptmirror
    from yum_mirror.yum_mirror_run import runyummirror
    from yum_mirror.yum_mirror_run import buildyummirror
    from container_mirror.container_mirror_run import runcontainermirror
    from container_mirror.container_mirror_run import buildcontainermirror
    from pypi_mirror.pypi_mirror_run import runpypimirror
    from pypi_mirror.pypi_mirror_run import buildpypimirror

    # Build the custom mirror images on startup
    print('Building different container image components...')
    logger.info('Building different container image components...')
    buildaptmirror()
    buildyummirror()
    buildcontainermirror()
    buildpypimirror()

    # Define different modules as different threads
    def callaptmirror():
        Thread(target = runaptmirror).start()

    def callyummirror():
        Thread(target = runyummirror).start()

    def callcontainermirror():
        Thread(target = runcontainermirror).start()

    def callpypimirror():
        Thread(target = runpypimirror).start()

    # If modules are set to run on startup run them right away
    if cfg['apt']['onstartup'] == True:
        callaptmirror()

    if cfg['apt']['onstartup'] == True:      
        callyummirror()

    if cfg['pypi']['onstartup'] == True:      
        callpypimirror()

    # Schedule to call various module runs at different times
    schedule.every(cfg['apt']['frequency']).minutes.do(callaptmirror)
    schedule.every(cfg['yum']['frequency']).minutes.do(callyummirror)
    schedule.every(cfg['skopeo']['frequency']).seconds.do(callcontainermirror)
    schedule.every(cfg['pypi']['frequency']).minutes.do(callpypimirror)

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
