#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

def setuppypimirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/pypi_mirror/files/templates'))
    template = env.get_template('bandersnatch.conf.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')
    print(output_from_parsed_template)

    # Create mirrors from config file
    print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
    with open("/opt/mirrorsync/pypi_mirror/files/bandersnatch.conf", "w") as fh:
        fh.write(output_from_parsed_template)

# Docker SDK
def runpypimirror():

    # Try to run the container
    try:
        client = docker.from_env()
        # If the systemd user is not root, create the directory as the other user.
        if cfg['mirrorsync']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['pypi']['destination']], check=True)
        client.containers.run('pypi-mirror',volumes={cfg['pypi']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'},'/opt/mirrorsync/pypi_mirror/files/bandersnatch.conf':{'bind': '/conf/bandersnatch.conf', 'mode': 'rw'}},name='pypi-mirror',remove=True,detach=True,user=cfg['mirrorsync']['systemduser'])

    except Exception as e:
        logger.error('There was an error running the image.')
        logger.error(e)
        print('There was an error running the image.')
        print(e)

    else:
        print('Container is running for pypi-mirror.')
        logger.info('Container is running for pypi-mirror.')

