#!/usr/bin/python3
import jinja2
import yaml
import subprocess

with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

try:
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/transferbuddy/files/templates'))
    template = env.get_template('systemd.jinja')
    output_from_parsed_template = template.render(cfg=cfg['transferbuddy'])

    try:       
        # Create systemd from config
        with open("/etc/systemd/system/transferbuddy.service", "w") as fh:
            fh.write(output_from_parsed_template)
    except Exception as e:
        print('This needs to be run with sudo or root: ')
        print(e)

    subprocess.Popen(['systemctl', 'daemon-reload'])

except Exception as e:
    print('Could not setup systemd: ')
    print(e)

else:
    print('Systemd service setup. You can start service with "systemctl enable transferbuddy --now')

