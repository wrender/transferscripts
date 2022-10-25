#!/usr/bin/python3
import logging
import yaml
import subprocess
import docker
import jinja2

with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)


def runaptmirror():
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
        print('Building the container...')
        client = docker.from_env()
        client.images.build(tag='apt-mirror:latest',path='/opt/transferbuddy/apt_mirror/files/')
    except docker.errors.BuildError as e:
        logging.error('There was an error building the image: ' + e )
        print(e)
    else:
        print('Built apt-image image successfully')
        logging.info('Built apt-mirror image successfully')

    # Start the container if it is not running
    try:
        client = docker.from_env()
        client.containers.get('apt-mirror')
        
    except:
        print('Trying to start container')
        # If the systemd user is not root, create the directory as the other user.
        if cfg['transferbuddy']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['apt']['destination']], check=True)
        client.containers.run('apt-mirror',volumes={cfg['apt']['destination']: {'bind': '/var/spool/apt-mirror', 'mode': 'rw'}},name='apt-mirror',auto_remove=True,detach=True,user=cfg['transferbuddy']['systemduser'])

if cfg['apt']['onstartup'] == True:
    runaptmirror()