#!/usr/bin/python3
import yaml
import docker
import logging

with open('/opt/registrysync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Build custom skopeo image
def buildcontainermirror():
     
    # Create the Dockerfile
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/registrysync/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/registrysync/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        logger.info('Building the container for registry-sync...')
        print('Building the container for registry-sync...')
        client = docker.from_env()
        client.images.build(tag='registry-sync:v1.0',path='/opt/registrysync/files/',network_mode=cfg['registrysync']['networkmode'],use_config_proxy=cfg['registrysync']['configproxy'],rm=True)
    except docker.errors.BuildError as e:
        logger.error('There was an error building the image: ' + e )
        print('There was an error building the image: ' + e )
    else:
        print('Built registry-sync image successfully')
        logger.info('Built registry-sync image successfully')

buildcontainermirror()
