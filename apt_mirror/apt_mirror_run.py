#!/usr/bin/python3
import logging
import yaml
import subprocess
import docker
import os
import shutil
from files.common import checkcontainerrunning
from files.common import checkforadditional

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'apt-mirror'

def setupaptmirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/apt_mirror/files/templates'))
    template = env.get_template('apt-mirrors.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/mirrorsync/apt_mirror/files/apt-mirror.list", "w") as fh:
        fh.write(output_from_parsed_template)

# Section to rclone data from container mirror to ssh destination
def rcloneaptmirror():


    if os.path.exists('/opt/mirrorsync/apt_mirror/rclone.log'):
        # Keep one rsync logging file for review
        src_path = '/opt/mirrorsync/apt_mirror/rclone.log'
        dst_path = '/opt/mirrorsync/apt_mirror/rclone.log-previous.log'
        shutil.move(src_path, dst_path)

    subprocess.run(['rclone',
                    'sync',
                    '-v',
                    '--log-file',
                    '/opt/mirrorsync/apt_mirror/rclone.log',
                    cfg['apt']['destination'],
                    'remote:' + cfg['apt']['rclone']['destination']])

def runaptmirror():

    # Setup local directory
    isExist = os.path.exists(cfg['apt']['destination'])
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(cfg['apt']['destination'])

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)

        # Start the container if it is not running
        try:
            aptdockerclient = docker.from_env()
            aptdockerclient.containers.run('apt-mirror:v1.0',volumes={cfg['apt']['destination']: {'bind': '/var/spool/apt-mirror', 'mode': 'rw'},'/opt/mirrorsync/apt_mirror/files/apt-mirror.list':{'bind': '/etc/apt/mirror.list', 'mode': 'rw'}},detach=False,name='apt-mirror',remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
            
            checkforadditional(cfg['apt']['repos'],cfg['apt']['destination'])

            # Call rclone
            if cfg['apt']['rclone']['enabled'] == True:
                rcloneaptmirror()

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)
