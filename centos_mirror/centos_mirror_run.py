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

modulename = 'centos-mirror'

# Create a class and put into own thread to run in background
class CentOSRsyncRemote(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p= subprocess.Popen(['rsync',
                            '-aSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/centos_mirror/rsync-2.log',
                            cfg['centos']['destination'],
                            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['centos']['rsync']['rsyncdestination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                            
        writepidfile('/tmp/mirrorsync/centosrsync.txt', p.pid)

        self.stdout, self.stderr = p.communicate()

# Create a class and put into own thread to run in background
class CentOSMirrorLocal(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(['rsync',
                            '-avSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/centos_mirror/rsync-1.log',
                            '--exclude-from=/opt/mirrorsync/centos_mirror/excludelist.txt',
                            cfg['centos']['sourcemirror'],
                            cfg['centos']['destination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                                 
        writepidfile('/tmp/mirrorsync/centosmirror.txt', p.pid)

        self.stdout, self.stderr = p.communicate()


# Main function to run centos rsync
def rsynccentosmirror():

    if checkpid('/tmp/mirrorsync/centosrsync.txt') == True:
        print('Not doing anything, centos rsync process is already running')
        logger.debug('Not doing anything, centos rsync process is already running')
    else:
        if os.path.exists('/opt/mirrorsync/centos_mirror/rsync-2.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/centos_mirror/rsync-2.log'
            dst_path = '/opt/mirrorsync/centos_mirror/rsync-2-previous.log'
            shutil.move(src_path, dst_path)

        # Run RSYNC to local directory
        logger.debug('Trying to start remote rsync of centos')
        print('Trying to start remote rsync of centos')
        myclass = CentOSRsyncRemote()
        myclass.start()


# Main function to run centos mirror locally
def runcentosmirror():

    if checkpid('/tmp/mirrorsync/centosmirror.txt') == True:
        print('Not doing anything, process is already running')
        logger.debug('Not doing anything, process is already running')
    else:
        # Setup local directory
        isExist = os.path.exists(cfg['centos']['destination'])
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(cfg['centos']['destination'])

        if os.path.exists('/opt/mirrorsync/centos_mirror/rsync-1.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/centos_mirror/rsync-1.log'
            dst_path = '/opt/mirrorsync/centos_mirror/rsync-1-previous.log'
            shutil.move(src_path, dst_path)

        # Run RSYNC to local directory
        logger.debug('Trying to start rsync of centos')
        print('Trying to start rsync of centos')
        myclass = CentOSMirrorLocal
        myclass.start()




        
