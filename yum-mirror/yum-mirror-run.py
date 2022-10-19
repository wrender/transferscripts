#!/usr/bin/python3
import jinja2
import yaml
import subprocess

with open('../config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

print('\n' + 'Running the container "yum-mirror" to sync to ' + cfg['yum']['destination'] + '\n')
print('\n' + 'Run "docker logs yum-mirror" to view logs' + '\n')
result = subprocess.run(['sudo','docker','run','--rm','-d','-v', cfg['yum']['destination'] + ':/mnt/repos','--name','yum-mirror','yum-mirror:latest'], check=True)