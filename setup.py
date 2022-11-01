#!/usr/bin/python3
import jinja2
import yaml
import subprocess
import apt_mirror.apt_mirror_image
import yum_mirror.yum_mirror_image
import container_mirror.container_mirror_image
import pypi_mirror.pypi_mirror_image

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

try:
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/mirrorsync/files/templates'))
    template = env.get_template('systemd.jinja')
    output_from_parsed_template = template.render(cfg=cfg['mirrorsync'])

    try:       
        # Create systemd from config
        with open("/etc/systemd/system/mirrorsync.service", "w") as fh:
            fh.write(output_from_parsed_template)
    except Exception as e:
        print('This needs to be run with sudo or root: ')
        print(e)

    subprocess.Popen(['systemctl', 'daemon-reload'])

except Exception as e:
    print('Could not setup systemd: ')
    print(e)

else:
    print('\n' + 'Systemd service setup. You can start service with "systemctl enable mirrorsync --now')

