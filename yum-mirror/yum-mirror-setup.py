#!/usr/bin/python3
import jinja2
import yaml
import subprocess

with open('../config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./files/templates'))
template = env.get_template('yum.repos.jinja')
output_from_parsed_template = template.render(repos=cfg['yum']['repos'],destination=cfg['yum']['destination'],frequency=cfg['yum']['frequency'])
print('\n' + 'Mirrors that are defined in config.yaml file...')
print(output_from_parsed_template)

# Create mirrors from config file
print('Setting up mirrors to syncronize from config.yaml file...' + '\n')
with open("./files/mirrors.repo", "w") as fh:
    fh.write(output_from_parsed_template)

# Configure Entrypoint file
env = Environment(loader=FileSystemLoader('./files/templates'))
template = env.get_template('entrypoint.jinja')
output_from_parsed_template = template.render(repos=cfg['yum']['repos'],destination=cfg['yum']['destination'],frequency=cfg['yum']['frequency'])

# Create mirrors from config file
with open("./files/entrypoint.sh", "w") as fh:
    fh.write(output_from_parsed_template)


result = subprocess.run(['sudo','docker', 'build', '-t', 'yum-mirror:latest', '.'], check=True)