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

modulename = 'epel-mirror'

# Create a class and put into own thread to run in background
class EPELRsyncRemote(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p= subprocess.Popen(['rsync',
                            '-aSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/epel_mirror/rsync-2.log',
                            cfg['epel']['destination'],
                            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['epel']['rsync']['rsyncdestination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                            
        writepidfile('/tmp/mirrorsync/epelrsync.txt', p.pid)

        self.stdout, self.stderr = p.communicate()

# Create a class and put into own thread to run in background
class EPELMirrorLocal(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(['rsync',
                            '-avSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/epel_mirror/rsync-1.log',
                            '--exclude-from=/opt/mirrorsync/epel_mirror/excludelist.txt',
                            cfg['epel']['sourcemirror'],
                            cfg['epel']['destination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                                 
        writepidfile('/tmp/mirrorsync/epelmirror.txt', p.pid)

        self.stdout, self.stderr = p.communicate()


# Main function to run epel rsync
def rsyncepelmirror():

    if checkpid('/tmp/mirrorsync/epelrsync.txt') == True:
        print('Not doing anything, epel rsync process is already running')
        logger.debug('Not doing anything, epel rsync process is already running')
    else:
        if os.path.exists('/opt/mirrorsync/epel_mirror/rsync-2.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/epel_mirror/rsync-2.log'
            dst_path = '/opt/mirrorsync/epel_mirror/rsync-2-previous.log'
            shutil.move(src_path, dst_path)

        # Run RSYNC to local directory
        logger.debug('Trying to start remote rsync of epel')
        print('Trying to start remote rsync of epel')
        myclass = EPELRsyncRemote()
        myclass.start()


# Main function to run epel mirror locally
def runepelmirror():

    if checkpid('/tmp/mirrorsync/epelmirror.txt') == True:
        print('Not doing anything, process is already running')
        logger.debug('Not doing anything, process is already running')
    else:
        # Setup local directory
        isExist = os.path.exists(cfg['epel']['destination'])
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(cfg['epel']['destination'])

        if os.path.exists('/opt/mirrorsync/epel_mirror/rsync-1.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/epel_mirror/rsync-1.log'
            dst_path = '/opt/mirrorsync/epel_mirror/rsync-1-previous.log'
            shutil.move(src_path, dst_path)

        # Run RSYNC to local directory
        logger.debug('Trying to start rsync of epel')
        print('Trying to start rsync of epel')      
        myclass = EPELMirrorLocal()
        myclass.start()