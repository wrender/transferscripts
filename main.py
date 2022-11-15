#!/usr/bin/python3
import logging
import yaml
import schedule, time
import threading
import os
# import tracemalloc

# tracemalloc.start()

# Import different modules
from apt_mirror.apt_mirror_run import setupaptmirror
from apt_mirror.apt_mirror_run import runaptmirror
from apt_mirror.apt_mirror_run import rsyncaptmirror
from yum_mirror.yum_mirror_run import runyummirror
from yum_mirror.yum_mirror_run import setupyummirror
from yum_mirror.yum_mirror_run import rsyncyummirror
from container_mirror.container_mirror_run import runcontainermirror
from pypi_mirror.pypi_mirror_run import setuppypimirror
from pypi_mirror.pypi_mirror_run import runpypimirror
from pypi_mirror.pypi_mirror_run import rsyncpypimirror
from centos_mirror.centos_mirror_run import runcentosmirror
from centos_mirror.centos_mirror_run import rsynccentosmirror

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

# Setup pid directory
isExist = os.path.exists('/tmp/mirrorsync/')
if not isExist:
   # Create a new directory because it does not exist
   os.makedirs('/tmp/mirrorsync/')

def main():

    def run_threaded(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()

    # Function to check and call hourly or at a specific daily time
    def scheduletocall(task,frequency,timeofday: str=None):
        if timeofday is not None and len(timeofday) != 0:
            schedule.every().day.at(str(timeofday)).do(run_threaded,task)
        if frequency is not None and len(frequency) != 0:
            schedule.every(int(frequency)).minutes.do(run_threaded,task)

    # Schedule to call various module runs at different times
    if cfg['apt']['enabled'] == True:
        scheduletocall(task=runaptmirror,frequency=cfg['apt']['frequency'],timeofday=cfg['apt']['timeofday'])
        if cfg['apt']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncaptmirror,frequency=cfg['apt']['rsync']['frequency'],timeofday=cfg['apt']['rsync']['timeofday'])

    if cfg['yum']['enabled'] == True:
        scheduletocall(task=runyummirror,frequency=cfg['yum']['frequency'],timeofday=cfg['yum']['timeofday'])
        if cfg['yum']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncyummirror,frequency=cfg['yum']['rsync']['frequency'],timeofday=cfg['yum']['rsync']['timeofday'])

    if cfg['pypi']['enabled'] == True:
        scheduletocall(task=runpypimirror,frequency=cfg['pypi']['frequency'],timeofday=cfg['pypi']['timeofday'])
        if cfg['pypi']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncpypimirror,frequency=cfg['pypi']['rsync']['frequency'],timeofday=cfg['pypi']['rsync']['timeofday'])

    if cfg['centos']['enabled'] == True:
        scheduletocall(task=runcentosmirror,frequency=cfg['centos']['frequency'],timeofday=cfg['centos']['timeofday'])
        if cfg['centos']['rsync']['enabled'] == True:
            scheduletocall(task=rsynccentosmirror,frequency=cfg['centos']['rsync']['frequency'],timeofday=cfg['centos']['rsync']['timeofday'])

    if cfg['skopeo']['enabled'] == True:
        scheduletocall(task=runcontainermirror,frequency=cfg['skopeo']['frequency'])

    

    # Run these jobs below only once on startup if they are enabled.
    def run_threaded_once(job_func):
        job_thread = threading.Thread(target=job_func)
        job_thread.start()
        return schedule.CancelJob

    if cfg['yum']['enabled'] == True:
        if cfg['yum']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,runyummirror)
            if cfg['yum']['rsync']['enabled'] == True:
                schedule.every(10).seconds.do(run_threaded_once,rsyncyummirror)

    if cfg['apt']['enabled'] == True:
        if cfg['apt']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,runaptmirror)
            if cfg['apt']['rsync']['enabled'] == True:
                schedule.every(10).seconds.do(run_threaded_once,rsyncaptmirror)

    # if cfg['ubuntu']['enabled'] == True:
    #     if cfg['ubuntu']['onstartup'] == True:
    #         schedule.every(3).seconds.do(startuprunonce(runubuntumirror))

    if cfg['centos']['enabled'] == True:
        if cfg['centos']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,runcentosmirror)
            if cfg['centos']['rsync']['enabled'] == True:
                schedule.every(10).seconds.do(run_threaded_once,rsynccentosmirror)


    if cfg['pypi']['enabled'] == True:
        if cfg['pypi']['onstartup'] == True:
            schedule.every(3).seconds.do(run_threaded_once,runpypimirror)
            if cfg['pypi']['rsync']['enabled'] == True:
                schedule.every(10).seconds.do(run_threaded_once,rsyncpypimirror)




    
    # Main while loop for program that schedules jobs
    while 1:
        schedule.run_pending()
        time.sleep(1)
        # snapshot = tracemalloc.take_snapshot()
        # top_stats = snapshot.statistics('lineno')

        # print("[ Top 10 ]")
        # for stat in top_stats[:10]:
        #     print(stat)
        #     logger.info(stat)

if __name__ == '__main__':
    main()
