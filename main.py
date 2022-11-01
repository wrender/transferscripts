#!/usr/bin/python3
import logging
import yaml
import schedule, time



# Get Configuration Values
with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.safe_load(f)

def main():
    logger = logging.getLogger()
    fhandler = logging.FileHandler(filename='/opt/mirrorsync/mirrorsync.log', mode='a')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fhandler.setFormatter(formatter)
    logger.addHandler(fhandler)
    logger.setLevel(logging.INFO)
    
    from threading import Thread
    
    from apt_mirror.apt_mirror_run import setupaptmirror
    from apt_mirror.apt_mirror_run import runaptmirror
    from yum_mirror.yum_mirror_run import runyummirror
    from yum_mirror.yum_mirror_run import setupyummirror
    from container_mirror.container_mirror_run import runcontainermirror
    from pypi_mirror.pypi_mirror_run import setuppypimirror
    from pypi_mirror.pypi_mirror_run import runpypimirror

    # Build the custom mirror images on startup
    print('Setting up different container file components...')
    logger.info('Setting up different container file components...')
    setupaptmirror()
    setupyummirror()
    setuppypimirror()

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

    if cfg['yum']['onstartup'] == True:      
        callyummirror()

    if cfg['pypi']['onstartup'] == True:      
        callpypimirror()

    # Function to check and call hourly or at a specific daily time
    def scheduletocall(mirror,frequency,timeofday: str=None):
        if timeofday is not None and len(timeofday) != 0:
            schedule.every().day.at(str(timeofday)).do(mirror)
        if frequency is not None and len(frequency) != 0:
            schedule.every(int(frequency)).minutes.do(mirror)

    # Schedule to call various module runs at different times
    scheduletocall(mirror=callaptmirror,frequency=cfg['apt']['frequency'],timeofday=cfg['apt']['timeofday'])
    scheduletocall(mirror=callyummirror,frequency=cfg['yum']['frequency'],timeofday=cfg['yum']['timeofday'])
    scheduletocall(mirror=callcontainermirror,frequency=cfg['skopeo']['frequency'])
    scheduletocall(mirror=callpypimirror,frequency=cfg['pypi']['frequency'],timeofday=cfg['pypi']['timeofday'])

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
