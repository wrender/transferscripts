#!/usr/bin/python3
import yaml
import subprocess
import logging
import threading

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'rclone-mirror'

def setuprclonemirror():
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/rclone_mirror/files/templates'))
    template = env.get_template('exclude.jinja')
    output_from_parsed_template = template.render(cfg)
    print('\n' + 'Mirrors that are defined in config.yaml file...')
    print(output_from_parsed_template)

    # Setup exlude file
    with open("/opt/mirrorsync/rclone_mirror/files/exclude-file.txt", "w") as fh:
        fh.write(output_from_parsed_template)

# Function to rclone data from container mirror to ssh destination
def rclonemirror():

    for item, key in cfg['rclone']['mirrors'].items():
        print(item)
        print(key['destination'])

        subprocess.run(['rclone',
                'sync',
                '-v',
                '--exclude-from',
                '/opt/mirrorsync/rclone_mirror/files/exclude-file.txt',
                '--bwlimit',
                cfg['rclone']['bwlimit'],
                '--http-url',
                key['source'],
                ':http:' + key['sourcepath'],
                key['destination']])
