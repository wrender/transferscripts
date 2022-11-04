#!/usr/bin/python3
import logging
import docker
import yaml
import os
import subprocess
import time


# Get Configuration Values
with open('/opt/sync_registry/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)


def toregistry():
    tempsrcdir = cfg['sync_registry']['skopeo']['source'] +'/tmp/'

    if os.path.exists(cfg['sync_registry']['skopeo']['source'] + '/completed.txt'):

        # Move files to a temporary directory to syncronize them to image registry
        os.mkdir(tempsrcdir)
        subprocess.call('mv',cfg['sync_registry']['skopeo']['source'] + '/*',tempsrcdir)

        try:
            # Try to syncronize files to image registry
            print('Syncing images to repository...')
            logger.info('Syncing images to repository...')
            skopeocommand = ['sync','--dest-tls-verify=' + str(cfg['sync_registry']['skopeo']['dest-tls-verify']),'--src','dir','--dest','docker',tempsrcdir,cfg['sync_registry']['skopeo']['registrydestination'] ]
            client = docker.from_env()
            client.containers.run('sync-registry:v1.0',volumes={tempsrcdir: {'bind': '/var/lib/containers/storage', 'mode': 'rw'}},command=skopeocommand,remove=True)
            
        except Exception as e:
            print(e)
            logger.error(e)

        else:
            # Remove temporary directory once done
            subprocess.call('rm -rf',tempsrcdir)
            time.sleep(5)

    else:
        return

toregistry()