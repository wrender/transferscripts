#!/usr/bin/python3
import logging
import yaml
import schedule, time
import os
import threading

# Import different modules
from apt_mirror.apt_mirror_run import setupaptmirror
from apt_mirror.apt_mirror_run import runaptmirror
from yum_mirror.yum_mirror_run import runyummirror
from yum_mirror.yum_mirror_run import setupyummirror
from container_mirror.container_mirror_run import runcontainermirror
from pypi_mirror.pypi_mirror_run import setuppypimirror
from pypi_mirror.pypi_mirror_run import runpypimirror

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

# Setup pid folder
pidpath = '/tmp/mirrorsync'
isExist = os.path.exists(pidpath)
if not isExist:
    # Create a new directory because it does not exist
    os.makedirs(pidpath)


# If modules are set to run on startup run them right away
if cfg['apt']['onstartup'] == True:
    runaptmirror()

if cfg['yum']['onstartup'] == True:      
    runyummirror()

if cfg['pypi']['onstartup'] == True:      
    runpypimirror()

def main():

    # Setup scheduling/threading
    def run_continuously(interval=1):
        """Continuously run, while executing pending jobs at each
        elapsed time interval.
        @return cease_continuous_run: threading. Event which can
        be set to cease continuous run. Please note that it is
        *intended behavior that run_continuously() does not run
        missed jobs*. For example, if you've registered a job that
        should run every minute and you set a continuous run
        interval of one hour then your job won't be run 60 times
        at each interval but only once.
        """
        cease_continuous_run = threading.Event()

        class ScheduleThread(threading.Thread):
            @classmethod
            def run(cls):
                while not cease_continuous_run.is_set():
                    schedule.run_pending()
                    time.sleep(interval)

        continuous_thread = ScheduleThread()
        continuous_thread.start()
        return cease_continuous_run

    # Function to check and call hourly or at a specific daily time
    def scheduletocall(mirror,frequency,timeofday: str=None):
        if timeofday is not None and len(timeofday) != 0:
            schedule.every().day.at(str(timeofday)).do(mirror)
        if frequency is not None and len(frequency) != 0:
            schedule.every(int(frequency)).minutes.do(mirror)

    # Schedule to call various module runs at different times
    scheduletocall(mirror=runaptmirror,frequency=cfg['apt']['frequency'],timeofday=cfg['apt']['timeofday'])
    scheduletocall(mirror=runyummirror,frequency=cfg['yum']['frequency'],timeofday=cfg['yum']['timeofday'])
    scheduletocall(mirror=runcontainermirror,frequency=cfg['skopeo']['frequency'])
    scheduletocall(mirror=runpypimirror,frequency=cfg['pypi']['frequency'],timeofday=cfg['pypi']['timeofday'])

    # Start the background thread
    run_continuously()
       

if __name__ == '__main__':
    main()
