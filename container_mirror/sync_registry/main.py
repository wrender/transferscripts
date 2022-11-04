#!/usr/bin/python3
import logging
import sync_registry

logger = logging.getLogger()
fhandler = logging.FileHandler(filename='/opt/sync_registry/sync_registry.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)

while True:
    sync_registry.toregistry()