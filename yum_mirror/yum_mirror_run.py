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

# Function to rsync data from container mirror to ssh destination
def rsyncyummirror():

    subprocess.call(['rsync',
    '-avz',
    '--delete',
    '-e',
    "ssh '-i" + cfg['rsync']['sshidentity'] + "'",
    cfg['yum']['destination'],
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['yum']['rsyncdestination']])

# Main function to run yum mirror
def runyummirror():

    if checkcontainerrunning(modulename) == False:
        print('Trying to start container ' + modulename)
        logger.info('Trying to start container ' + modulename)
        
        # Try to run the container
        try:
            
            # If the systemd user is not root, create the directory as the other user.
            if cfg['mirrorsync']['systemduser'] != 'root':
                subprocess.run(['mkdir','-p',cfg['yum']['destination']], check=True)
            client = docker.from_env()
            client.containers.run('yum-mirror:v1.0',volumes={cfg['yum']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/rundnf.sh':{'bind': '/opt/rundnf.sh', 'mode': 'rw'},'/opt/mirrorsync/yum_mirror/files/yum-mirrors.repo':{'bind': '/etc/yum.repos.d/mirrors.repo', 'mode': 'rw'}},name='yum-mirror',remove=True,user=cfg['mirrorsync']['systemduser'])
            # Call rsync
            if cfg['yum']['rsync'] == True:
                rsyncyummirror()

        except Exception as e:
            logger.debug('There was an error running the image.')
            logger.debug(e)

    else:
        print('Container is already running nothing to do ' + modulename)
        logger.info('Container is already running nothing to do ' + modulename)

