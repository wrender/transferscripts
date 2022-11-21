#!/usr/bin/python3
import jinja2
import yaml
import subprocess
import registrysync_build

with open('/opt/registrysync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

try:
    from jinja2 import Environment, FileSystemLoader
    env = Environment(loader=FileSystemLoader('/opt/registrysync/files/templates'))
    template = env.get_template('systemd.jinja')
    output_from_parsed_template = template.render(cfg=cfg['registrysync'])

    try:       
        # Create systemd from config
        with open("/etc/systemd/system/registrysync.service", "w") as fh:
            fh.write(output_from_parsed_template)
    except Exception as e:
        print('This needs to be run with sudo or root: ')
        print(e)

    subprocess.Popen(['systemctl', 'daemon-reload'])

except Exception as e:
    print('Could not setup systemd: ')
    print(e)

else:
    print('\n' + 'Systemd service setup. You can start service with "systemctl enable registrysync --now')

