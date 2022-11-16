#!/usr/bin/python3
import yaml
import subprocess
import logging
import shutil
import os
import threading
from files.common import checkpid
from files.common import writepidfile

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'ubuntu-mirror'

# Create a class and put into own thread to run in background
class UbuntuRsyncRemote(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p= subprocess.Popen(['rsync',
                            '-avSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/ubuntu_mirror/rsync-1.log',
                            cfg['ubuntu']['sourcemirror'],
                            cfg['ubuntu']['rsyncdestination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                            
        writepidfile('/tmp/mirrorsync/ubuntumirror.txt', p.pid)

        self.stdout, self.stderr = p.communicate()



# Main function to run ubuntu mirror locally
def runubuntumirror():

    if checkpid('/tmp/mirrorsync/ubuntumirror.txt') == True:
        print('Not doing anything, process is already running')
        logger.debug('Not doing anything, process is already running')
    else:
        if os.path.exists('/opt/mirrorsync/ubuntu_mirror/rsync-1.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/ubuntu_mirror/rsync-1.log'
            dst_path = '/opt/mirrorsync/ubuntu_mirror/rsync-1-previous.log'
            shutil.move(src_path, dst_path)

        # Run RSYNC to local directory
        logger.debug('Trying to start rsync of ubuntu')
        print('Trying to start rsync of ubuntu')
        myclass = UbuntuRsyncRemote()
        myclass.start()




        
