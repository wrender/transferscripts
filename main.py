#!/usr/bin/python3
import logging
import yaml
import schedule, time
import threading

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
    def scheduletocall(task,frequency,timeofday: str=None):
        if timeofday is not None and len(timeofday) != 0:
            schedule.every().day.at(str(timeofday)).do(task)
        if frequency is not None and len(frequency) != 0:
            schedule.every(int(frequency)).minutes.do(task)

    # Schedule to call various module runs at different times
    if cfg['apt']['enabled'] == True:
        scheduletocall(task=runaptmirror,frequency=cfg['apt']['frequency'],timeofday=cfg['apt']['timeofday'])
        if cfg['apt']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncaptmirror,frequency=cfg['apt']['rsync']['frequency'])

    if cfg['yum']['enabled'] == True:
        scheduletocall(task=runyummirror,frequency=cfg['yum']['frequency'],timeofday=cfg['yum']['timeofday'])
        if cfg['yum']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncyummirror,frequency=cfg['yum']['rsync']['frequency'])

    if cfg['pypi']['enabled'] == True:
        scheduletocall(task=runpypimirror,frequency=cfg['pypi']['frequency'],timeofday=cfg['pypi']['timeofday'])
        if cfg['pypi']['rsync']['enabled'] == True:
            scheduletocall(task=rsyncpypimirror,frequency=cfg['pypi']['rsync']['frequency'])

    if cfg['skopeo']['enabled'] == True:
        scheduletocall(task=runcontainermirror,frequency=cfg['skopeo']['frequency'])


    # Start the background thread
    run_continuously()


if __name__ == '__main__':
    main()
