#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging
import shutil
import os
import threading
from files.common import checkcontainerrunning

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'pypi-mirror'

def setuppypimirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/pypi_mirror/files/templates'))
    template = env.get_template('bandersnatch.conf.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')

    # Create mirrors from config file
    print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
    with open("/opt/mirrorsync/pypi_mirror/files/bandersnatch.conf", "w") as fh:
        fh.write(output_from_parsed_template)

# Create a class and put into own thread to run in background
class PypiRYNC(threading.Thread):
    def __init__(self):
        self.stdout = None
        self.stderr = None
        threading.Thread.__init__(self)

    def run(self):
        p = subprocess.Popen(['rsync',
                            '-avSHP',
                            '--delete-after',
                            '--log-file=/opt/mirrorsync/pypi_mirror/rsync-1.log',
                            cfg['pypi']['destination'],
                            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['pypi']['rsync']['rsyncdestination']],
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
                                 
        self.stdout, self.stderr = p.communicate()

# Function to rsync data from pypi mirror to ssh destination
def rsyncpypimirror():

    if os.path.exists('/opt/mirrorsync/pypi_mirror/rsync-1.log'):
        # Keep one rsync logging file for review
        src_path = '/opt/mirrorsync/pypi_mirror/rsync-1.log'
        dst_path = '/opt/mirrorsync/pypi_mirror/rsync-1-previous.log'
        shutil.move(src_path, dst_path)

    myclass = PypiRYNC()
    myclass.start()


# Main pypi mirror function
def runpypimirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)

        # Try to run the container
        try:

            # Setup local directory
            isExist = os.path.exists(cfg['pypi']['destination'])
            if not isExist:
                # Create a new directory because it does not exist
                os.makedirs(cfg['pypi']['destination'])
            
            client = docker.from_env()
            client.containers.run('pypi-mirror:v1.0',volumes={cfg['pypi']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/pypi_mirror/files/bandersnatch.conf':{'bind': '/conf/bandersnatch.conf', 'mode': 'rw'}},name='pypi-mirror',detach=False,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
            
            # Call rsync
            if cfg['pypi']['rsync']['enabled'] == True:
                rsyncpypimirror()


        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)
