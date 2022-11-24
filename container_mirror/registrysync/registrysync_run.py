#!/usr/bin/python3
import logging
import yaml
import os
import subprocess
import time


# Get Configuration Values
with open('/opt/registrysync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)


def toregistry():
    tempsrcdir = cfg['registrysync']['skopeo']['source'] +'tmp/'

    if os.path.exists(cfg['registrysync']['skopeo']['source'] + '/completed.txt'):

        # Move files to a temporary directory to syncronize them to image registry
        os.mkdir(tempsrcdir)
        subprocess.call(['mv ' + cfg['registrysync']['skopeo']['source'] + '*',tempsrcdir],shell=True)

        try:
            # Try to syncronize files to image registry
            print('Syncing images to repository...')
            logger.info('Syncing images to repository...')
            skopeocommand = ['sync','--dest-tls-verify=' + str(cfg['registrysync']['skopeo']['dest-tls-verify']),'--src','dir','--dest','docker','/mnt/repos',cfg['registrysync']['skopeo']['registrydestination'] ]


            subprocess.run(['docker','run','--rm','-v',tempsrcdir + ':/mnt/repos','registry-sync:v1.0',skopeocommand])
            
        except Exception as e:
            print(e)
            logger.error(e)

        else:
            # Remove temporary directory once done
            subprocess.call(['rm','-rf',tempsrcdir])
            print("Syncronization complete")
            logger.info("Syncronization complete")
            time.sleep(1)

    else:
        print('Nothing to do')
        time.sleep(1)
        return

toregistry()