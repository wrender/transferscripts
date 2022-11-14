#!/usr/bin/python3
import docker
import logging
import os
import psutil


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