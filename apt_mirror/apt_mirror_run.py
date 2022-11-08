#!/usr/bin/python3
import logging
import yaml
import subprocess
import docker
import jinja2

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

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
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['apt']['rsyncdestination']])

def runaptmirror():

    # Start the container if it is not running
    try:
        client = docker.from_env()
        # If the systemd user is not root, create the directory as the other user.
        if cfg['mirrorsync']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['apt']['destination']], check=True)
        client.containers.run('apt-mirror:v1.0',volumes={cfg['apt']['destination']: {'bind': '/var/spool/apt-mirror', 'mode': 'rw'},'/opt/mirrorsync/apt_mirror/files/apt-mirror.list':{'bind': '/etc/apt/mirror.list', 'mode': 'rw'}},name='apt-mirror',remove=True,user=cfg['mirrorsync']['systemduser'])
        # Call rsync
        if cfg['apt']['rsync'] == True:
            rsyncaptmirror()

    except Exception as e:
        logger.error('There was an error running the image.')
        logger.error(e)
        print('There was an error running the image.')
        print(e)

    else:
        print('Container is running for apt-mirror.')
        logger.info('Container is running for apt-mirror.')

