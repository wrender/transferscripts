#!/usr/bin/python3
import jinja2
import yaml
import subprocess

with open('../config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

print('\n' + 'Running the container "apt-mirror" to sync to ' + cfg['apt']['destination'] + '\n')
print('\n' + 'Run "docker logs apt-mirror" to view logs' + '\n')

result = subprocess.run(['sudo','docker','run','--rm','-d','-v', cfg['apt']['destination'] + ':/var/spool/apt-mirror','--name','apt-mirror','apt-mirror:latest'], check=True)