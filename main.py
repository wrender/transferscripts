#!/usr/bin/python3
import logging
import yaml
import schedule, time
import threading
# import tracemalloc

# Import different modules
from apt_mirror.apt_mirror_run import setupaptmirror
from apt_mirror.apt_mirror_run import runaptmirror
from yum_mirror.yum_mirror_run import runyummirror
from yum_mirror.yum_mirror_run import setupyummirror
from container_mirror.container_mirror_run import runcontainermirror
from pypi_mirror.pypi_mirror_run import setuppypimirror
from pypi_mirror.pypi_mirror_run import runpypimirror
from rclone_mirror.rclone_mirror_run import rclonemirror


# Get Configuration Values
with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.safe_load(f)


logger = logging.getLogger()
fhandler = logging.FileHandler(filename='/opt/mirrorsync/mirrorsync.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)

# Build the custom mirror images on startup
print('Setting up different container file components...')
logger.info('Setting up different container file components...')
setupaptmirror()
setupyummirror()
setuppypimirror()

def main():

    def run_threaded(threadname:str,job_func):
        for th in threading.enumerate():
            if th.name == threadname:
                logger.info(threadname + " is still running. Nothing to do right now")
                return
        job_thread = threading.Thread(name=threadname,target=job_func)
        job_thread.start()

    # Function to check and call hourly or at a specific daily time
    def scheduletocall(threadname: str,task,frequency,timeofday: str=None):
        if timeofday is not None and len(timeofday) != 0:
            schedule.every().day.at(str(timeofday)).do(run_threaded,threadname,task)
        if frequency is not None and len(frequency) != 0:
            schedule.every(int(frequency)).minutes.do(run_threaded,threadname,task)

    # Schedule to call various module runs at different times
    if cfg['apt']['enabled'] == True:
        scheduletocall(threadname='runaptmirror',task=runaptmirror,frequency=cfg['apt']['frequency'],timeofday=cfg['apt']['timeofday'])

    if cfg['yum']['enabled'] == True:
        scheduletocall(threadname='runyummirror',task=runyummirror,frequency=cfg['yum']['frequency'],timeofday=cfg['yum']['timeofday'])

    if cfg['pypi']['enabled'] == True:
        scheduletocall(threadname='runpypimirror',task=runpypimirror,frequency=cfg['pypi']['frequency'],timeofday=cfg['pypi']['timeofday'])

    if cfg['rclone']['enabled'] == True:
        scheduletocall(threadname='rclonemirror',task=rclonemirror,frequency=cfg['rclone']['frequency'],timeofday=cfg['rclone']['timeofday'])

    if cfg['skopeo']['enabled'] == True:
        scheduletocall(threadname='runcontainermirror',task=runcontainermirror,frequency=cfg['skopeo']['frequency'])

    
    # Run these jobs below only once on startup if they are enabled.
    def run_threaded_once(threadname:str, job_func):
        for th in threading.enumerate():
            if th.name == threadname:
                logger.info(threadname + " is still running. Nothing to do right now")
                return
        job_thread = threading.Thread(name=threadname,target=job_func)
        job_thread.start()
        return schedule.CancelJob

    if cfg['yum']['enabled'] == True:
        if cfg['yum']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,'runyummirror',runyummirror)

    if cfg['apt']['enabled'] == True:
        if cfg['apt']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,'runaptmirror',runaptmirror)

    if cfg['pypi']['enabled'] == True:
        if cfg['pypi']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,'runpypimirror',runpypimirror)

    if cfg['rclone']['enabled'] == True:
        if cfg['rclone']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,'rclonemirror',rclonemirror)
    
    # Main while loop for program that schedules jobs
    while 1:
        
        schedule.run_pending()
        time.sleep(1)

if __name__ == '__main__':
    main()
