#!/usr/bin/python3
import logging
import yaml
import docker
import jinja2

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

def buildaptmirror():
    # Create the Dockerfile
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/apt_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/mirrorsync/apt_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for apt-mirror...')
        print('Building the container for apt-mirror...')
        client = docker.from_env()
        client.images.build(tag='apt-mirror:v1.0',path='/opt/mirrorsync/apt_mirror/files/',use_config_proxy=cfg['mirrorsync']['configproxy'],rm=True)
    except Exception as e:
        logger.error('There was an error building the image.')
        logger.error(e)
        print('There was an error building the image.')
        print(e)
    else:
        print('Built apt-image image successfully')
        logger.info('Built apt-mirror image successfully')

buildaptmirror()