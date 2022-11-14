#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging
import shutil
import os
import threading
from files.common import checkcontainerrunning
from files.common import checkpid
from files.common import writepidfile

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'yum-mirror'

def setupyummirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/yum_mirror/files/templates'))
    template = env.get_template('repos.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')
    print(output_from_parsed_template)

    # Create mirrors from config file
    print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
    with open("/opt/mirrorsync/yum_mirror/files/yum-mirrors.repo", "w") as fh:
        fh.write(output_from_parsed_template)

    # Configure RUN BASH Script
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/yum_mirror/files/templates'))
    template = env.get_template('rundnf.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Setup DNF Run script
    with open("/opt/mirrorsync/yum_mirror/files/rundnf.sh", "w") as fh:
        fh.write(output_from_parsed_template)

# Create a class and put into own thread to run in background
class YumRSYNC(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(['rsync',
                            '-avSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/yum_mirror/rsync-1.log',
                            cfg['yum']['destination'],
                            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['yum']['rsync']['rsyncdestination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                                 
        writepidfile('/tmp/mirrorsync/yummirror.txt', p.pid)

        self.stdout, self.stderr = p.communicate()

# Function to rsync data from container mirror to ssh destination
def rsyncyummirror():
    
    if checkpid('/tmp/mirrorsync/yummirror.txt') == True:
        print('Not doing anything, process is already running')
    else:
        if os.path.exists('/opt/mirrorsync/apt_mirror/rsync-1.log'):
            # Keep one rsync logging file for review
            src_path = '/opt/mirrorsync/yum_mirror/rsync-1.log'
            dst_path = '/opt/mirrorsync/yum_mirror/rsync-1-previous.log'
            shutil.move(src_path, dst_path)

        myclass = YumRSYNC
        myclass.start()

# Main function to run yum mirror
def runyummirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)
        
        # Try to run the container
        try:
            
            client = docker.from_env()
            client.containers.run('yum-mirror:v1.0',volumes={cfg['yum']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/rundnf.sh':{'bind': '/opt/rundnf.sh', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/yum-mirrors.repo':{'bind': '/etc/yum.repos.d/mirrors.repo', 'mode': 'rw'}},detach=True,name='yum-mirror',remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
            
            # Call rsync
            if cfg['yum']['rsync']['enabled'] == True:
                rsyncyummirror()

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)