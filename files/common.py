#!/usr/bin/python3
import docker
import logging
import os
import psutil
import subprocess


# Setup Module logger
logger = logging.getLogger(__name__)

# Check if a container is running
def checkcontainerrunning(container_name: str):
    client = docker.from_env()
    try:
        client.containers.get(container_name)
    except:
        return False
    else:
        return True

# Check if pid is running if not delete pid file if it exists
def checkpid(pidfile: str):
    if os.path.exists(pidfile):
        f = open(pidfile, "r")
        mypid = (f.readline())
        if psutil.pid_exists(int(mypid)):
            return True
        else:
            os.remove(pidfile)
            return False
    else:
        return False

# Wite the pid file
def writepidfile(pidfile: str, pid):
    with open(pidfile, 'w', encoding='utf-8') as f:
        f.write(str(pid))

def checkforadditional(repos, destination):
    # Check for additional files
    
    for item, repokey in repos.items():
        # Setup local directory
        isExist = os.path.exists(destination + '/downloads')
        if not isExist:
            # Create a new directory because it does not exist
            os.makedirs(destination + '/downloads')
        if 'additionalfiles' in repokey:
            # Loop through files and download    
            for file in repokey['additionalfiles']:
                logger.info('Additional files downloading item for: ' + item + ' ' + file )
                subprocess.run(['wget','-c','-P',destination + '/downloads/',file])

        if 'additionaldirectories' in repokey:
            # Loop through folders and download    
            for file in repokey['additionaldirectories']:
                logger.info('Additional folders downloading item for: ' + item + ' ' + file )
                subprocess.run(['wget','-nH','-np','-m','-P',destination + '/downloads/',file])

        if 'gpgkeyfiles' in repokey:
            # Loop through files and download    
            for file in repokey['gpgkeyfiles']:
                logger.info('Downloading GPG Items: ' + item + ' ' + file )
                subprocess.run(['wget','-c','-P',destination + '/downloads/',file])