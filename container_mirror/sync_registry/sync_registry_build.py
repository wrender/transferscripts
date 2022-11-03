#!/usr/bin/python3
import yaml
import docker
import logging

with open('/opt/sync_registry/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Build custom skopeo image
def buildcontainermirror():
     
    # Create the Dockerfile
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/sync_registry/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/sync_registry/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for sync-registry...')
        print('Building the container for sync-registry...')
        client = docker.from_env()
        client.images.build(tag='sync-registry:v1.0',path='/opt/sync_registry/files/',rm=True)
    except docker.errors.BuildError as e:
        logger.error('There was an error building the image: ' + e )
        print('There was an error building the image: ' + e )
    else:
        print('Built sync-registry image successfully')
        logger.info('Built sync-registry image successfully')

buildcontainermirror()
