#!/usr/bin/python3
import yaml
import docker
import logging

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Build custom skopeo image
def buildcontainermirror():
     
    # Create the Dockerfile
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/container_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/mirrorsync/container_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for container-mirror...')
        print('Building the container for container-mirror...')
        client = docker.from_env()
        client.images.build(tag='container-mirror:v1.0',path='/opt/mirrorsync/container_mirror/files/',use_config_proxy=cfg['mirrorsync']['configproxy'],rm=True)
    except docker.errors.BuildError as e:
        logger.error('There was an error building the image: ' + e )
        print('There was an error building the image: ' + e )
    else:
        print('Built container-image image successfully')
        logger.info('Built container-mirror image successfully')

buildcontainermirror()
