#!/usr/bin/python3
import yaml
import subprocess
import docker
import logging

with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Docker SDK
def runyummirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/yum_mirror/files/templates'))
    template = env.get_template('repos.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')
    print(output_from_parsed_template)

    # Create mirrors from config file
    print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
    with open("/opt/transferbuddy/yum_mirror/files/yum-mirrors.repo", "w") as fh:
        fh.write(output_from_parsed_template)

    # Configure Entrypoint file
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/yum_mirror/files/templates'))
    template = env.get_template('entrypoint.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/yum_mirror/files/entrypoint.sh", "w") as fh:
        fh.write(output_from_parsed_template)

    # Create the Dockerfile
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/yum_mirror/files/templates'))
    template = env.get_template('Dockerfile.jinja')
    output_from_parsed_template = template.render(cfg)
    print(output_from_parsed_template)

    # Create mirrors from config file
    with open("/opt/transferbuddy/yum_mirror/files/Dockerfile", "w") as fh:
        fh.write(output_from_parsed_template)

    # Build the container
    try:
        print('Building the container...')
        client = docker.from_env()
        client.images.build(tag='yum-mirror:latest',path='/opt/transferbuddy/yum_mirror/files/')
    except docker.errors.BuildError as e:
        logging.error('There was an error building the image: ' + e )
        print('There was an error building the image: ' + e )
    else:
        print('Built yum-image image successfully')
        logging.info('Built yum-mirror image successfully')

    # Try to run the container
    try:
        client = docker.from_env()
        client.containers.get('yum-mirror')
    except:
        print('Trying to start container')
        # If the systemd user is not root, create the directory as the other user.
        if cfg['transferbuddy']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['yum']['destination']], check=True)
        client.containers.run('yum-mirror',volumes={cfg['yum']['destination']: {'bind': '/mnt/repos/', 'mode': 'rw'}},name='yum-mirror',auto_remove=True,detach=True,user=cfg['transferbuddy']['systemduser'])

if cfg['yum']['onstartup'] == True:      
    runyummirror()