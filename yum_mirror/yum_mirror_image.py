#!/usr/bin/python3
import yaml
import docker
import logging

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

def buildyummirror():
   
    # Create the Dockerfile
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/yum_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/mirrorsync/yum_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for yum-mirror...')
        print('Building the container for yum-mirror...')
        client = docker.from_env()
        client.images.build(tag='yum-mirror:v1.0',path='/opt/mirrorsync/yum_mirror/files/',rm=True)
    except Exception as e:
        logger.error('There was an error building the image.')
        logger.error(e)
        print('There was an error building the image.')
        print(e)
    else:
        print('Built yum-image image successfully')
        logger.info('Built yum-mirror image successfully')

buildyummirror()