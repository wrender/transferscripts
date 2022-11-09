#!/usr/bin/python3
import logging
import yaml
import subprocess
import docker
import jinja2
from files.common import checkcontainerrunning

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

# Function to rsync data from container mirror to ssh destination
def rsyncaptmirror():

    subprocess.call(['rsync',
    '-avz',
    '--delete',
    '-e',
    "ssh '-i" + cfg['rsync']['sshidentity'] + "'",
    cfg['apt']['destination'],
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['apt']['rsync']['rsyncdestination']])

def runaptmirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)

        # Start the container if it is not running

        try:

            aptdockerclient = docker.from_env()
            aptdockerclient.containers.run('apt-mirror:v1.0',volumes={cfg['apt']['destination']: {'bind': '/var/spool/apt-mirror', 'mode': 'rw'},'/opt/mirrorsync/apt_mirror/files/apt-mirror.list':{'bind': '/etc/apt/mirror.list', 'mode': 'rw'}},detach=True,name='apt-mirror',remove=True,user=cfg['mirrorsync']['systemduser'])
            
            # Call rsync
            if cfg['apt']['rsync'] == True:
                rsyncaptmirror()

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)


if cfg['apt']['enabled'] == True:
    if cfg['apt']['onstartup'] == True:
        runaptmirror()