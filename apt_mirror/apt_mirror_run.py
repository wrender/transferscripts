#!/usr/bin/python3
import logging
import yaml
import subprocess
import docker
import jinja2

with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

def buildaptmirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/apt_mirror/files/templates'))
    template = env.get_template('apt-mirrors.jinja')
    output_from_parsed_template = template.render(cfg)
    logging.info(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/apt_mirror/files/ubuntu-mirror.list", "w") as fh:
        fh.write(output_from_parsed_template)

    # Configure Entrypoint file
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/apt_mirror/files/templates'))
    template = env.get_template('entrypoint.jinja')
    output_from_parsed_template = template.render(cfg)

    # Create entrypoint file that runs at certain times
    with open("/opt/transferbuddy/apt_mirror/files/entrypoint.sh", "w") as fh:
        fh.write(output_from_parsed_template)

    # Create the Dockerfile
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/apt_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/apt_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for apt-mirror...')
        print('Building the container for apt-mirror...')
        client = docker.from_env()
        client.images.build(tag='apt-mirror:latest',path='/opt/transferbuddy/apt_mirror/files/',rm=True)
    except Exception as e:
        logger.error('There was an error building the image.')
        logger.error(e)
        print('There was an error building the image.')
        print(e)
    else:
        print('Built apt-image image successfully')
        logger.info('Built apt-mirror image successfully')

def runaptmirror():


    # Start the container if it is not running
    try:
        client = docker.from_env()
        client.containers.get('apt-mirror')
        
    except:
        print('Starting container apt-mirror to sync any apt repos...')
        logger.info('Starting container apt-mirror to sync any apt repos...')
        # If the systemd user is not root, create the directory as the other user.
        if cfg['transferbuddy']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['apt']['destination']], check=True)
        client.containers.run('apt-mirror',volumes={cfg['apt']['destination']: {'bind': '/var/spool/apt-mirror', 'mode': 'rw'}},name='apt-mirror',remove=True,detach=True,user=cfg['transferbuddy']['systemduser'])
    else:
        print('Container is running for apt-mirror. Nothing to do')
        logger.info('Container is running for apt-mirror. Nothing to do')

