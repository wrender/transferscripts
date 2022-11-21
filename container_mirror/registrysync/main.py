#!/usr/bin/python3
import logging
import registrysync

logger = logging.getLogger()
fhandler = logging.FileHandler(filename='/opt/registrysync/registrysync.log', mode='a')
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fhandler.setFormatter(formatter)
logger.addHandler(fhandler)
logger.setLevel(logging.INFO)

while True:
    registrysync.toregistry()