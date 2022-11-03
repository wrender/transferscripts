#!/usr/bin/python3
import logging
import docker
import yaml


# Get Configuration Values
with open('/opt/sync_registry/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)


def toregistry():
    print('Syncing images to repository...')
    logger.info('Syncing images to repository...')
    skopeocommand = ['sync','--dest-tls-verify=' + str(cfg['sync_registry']['skopeo']['dest-tls-verify']),'--src','dir','--dest','docker',cfg['sync_registry']['skopeo']['source'],cfg['sync_registry']['skopeo']['destination'] ]

    client = docker.from_env()
    client.containers.run('sync-registry:v1.0',command=skopeocommand,remove=True)
    
    return

toregistry()