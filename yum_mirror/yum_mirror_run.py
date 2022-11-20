#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging
import os
import shutil
from files.common import checkcontainerrunning
from files.common import checkforadditional

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

# Function to rclone data from container mirror to ssh destination
def rcloneyummirror():

    if os.path.exists('/opt/mirrorsync/yum_mirror/rclone.log'):
        # Keep one rsync logging file for review
        src_path = '/opt/mirrorsync/yum_mirror/rclone.log'
        dst_path = '/opt/mirrorsync/yum_mirror/rclone.log-previous.log'
        shutil.move(src_path, dst_path)
    
    subprocess.run(['rclone',
                    'sync',
                    '-v',
                    '--log-file',
                    '/opt/mirrorsync/yum_mirror/rclone.log',
                    cfg['yum']['destination'],
                    'remote:' + cfg['yum']['rclone']['destination']])

# Main function to run yum mirror
def runyummirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)
        
        # Setup local directory
        isExist = os.path.exists(cfg['yum']['destination'])
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(cfg['yum']['destination'])
        
        # Try to run the container
        try:
            
            client = docker.from_env()
            client.containers.run('yum-mirror:v1.0',volumes={cfg['yum']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/rundnf.sh':{'bind': '/opt/rundnf.sh', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/yum-mirrors.repo':{'bind': '/etc/yum.repos.d/mirrors.repo', 'mode': 'rw'}},detach=False,name='yum-mirror',remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
            
            checkforadditional(cfg['yum']['repos'],cfg['yum']['destination'])

            # Call rclone
            if cfg['yum']['rclone']['enabled'] == True:
                rcloneyummirror()

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)
