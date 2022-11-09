#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging
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

# Function to rsync data from container mirror to ssh destination
def rsyncpypimirror():

    subprocess.call(['rsync',
    '-avz',
    '--delete',
    '-e',
    "ssh '-i" + cfg['rsync']['sshidentity'] + "'",
    cfg['pypi']['destination'],
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['pypi']['rsync']['rsyncdestination']])

# Main pypi mirror function
def runpypimirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)

        # Try to run the container
        try:
            
            client = docker.from_env()
            client.containers.run('pypi-mirror:v1.0',volumes={cfg['pypi']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/pypi_mirror/files/bandersnatch.conf':{'bind': '/conf/bandersnatch.conf', 'mode': 'rw'}},name='pypi-mirror',detach=True,remove=True,user=cfg['mirrorsync']['systemduser'])

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)

if cfg['pypi']['enabled'] == True:
    if cfg['pypi']['onstartup'] == True:
        runpypimirror()