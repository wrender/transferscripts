#!/usr/bin/python3
import jinja2
import yaml
import subprocess

with open('../config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('./files/templates'))
template = env.get_template('ubuntu-mirrors.jinja')
output_from_parsed_template = template.render(basepath=cfg['apt']['basepath'],nthreads=cfg['apt']['nthreads'],tilde=cfg['apt']['tilde'],repos=cfg['apt']['repos'],clean=cfg['apt']['clean'])
print(output_from_parsed_template)

# Create mirrors from config file
with open("./files/ubuntu-mirror.list", "w") as fh:
    fh.write(output_from_parsed_template)

# Configure Entrypoint file
env = Environment(loader=FileSystemLoader('./files/templates'))
template = env.get_template('entrypoint.jinja')
output_from_parsed_template = template.render(repos=cfg['apt']['repos'],destination=cfg['apt']['destination'],frequency=cfg['apt']['frequency'])

# Create entrypoint file that runs at certain times
with open("./files/entrypoint.sh", "w") as fh:
    fh.write(output_from_parsed_template)


result = subprocess.run(['sudo','docker', 'build', '-t', 'apt-mirror:latest', '.'], check=True)
