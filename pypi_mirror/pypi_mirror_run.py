#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging

with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

def buildpypimirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/pypi_mirror/files/templates'))
    template = env.get_template('bandersnatch.conf.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')
    print(output_from_parsed_template)

    # Create mirrors from config file
    print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
    with open("/opt/transferbuddy/pypi_mirror/files/bandersnatch.conf", "w") as fh:
        fh.write(output_from_parsed_template)

    # Configure Entrypoint file
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/pypi_mirror/files/templates'))
    template = env.get_template('entrypoint.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/pypi_mirror/files/entrypoint.sh", "w") as fh:
        fh.write(output_from_parsed_template)

    # Create the Dockerfile
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/pypi_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/pypi_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for pypi-mirror...')
        print('Building the container for pypi-mirror...')
        client = docker.from_env()
        client.images.build(tag='pypi-mirror:latest',path='/opt/transferbuddy/pypi_mirror/files/',rm=True)
    except Exception as e:
        logger.error('There was an error building the image.')
        logger.error(e)
        print('There was an error building the image.')
        print(e)
    else:
        print('Built pypi-image image successfully')
        logger.info('Built pypi-mirror image successfully')

# Docker SDK
def runpypimirror():

    # Try to run the container
    try:
        client = docker.from_env()
        client.containers.get('pypi-mirror')
    except:
        print('Starting container pypi-mirror to sync any pypi packages...')
        logger.info('Starting container pypi-mirror to sync any pypi packages...')
        # If the systemd user is not root, create the directory as the other user.
        if cfg['transferbuddy']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['pypi']['destination']], check=True)
        client.containers.run('pypi-mirror',volumes={cfg['pypi']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'}},name='pypi-mirror',remove=True,detach=True,user=cfg['transferbuddy']['systemduser'])
    else:
        print('Container is running for pypi-mirror. Nothing to do')
        logger.info('Container is running for pypi-mirror. Nothing to do')

