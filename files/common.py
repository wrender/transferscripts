#!/usr/bin/python3
import docker
import logging


# Setup Module logger
logger = logging.getLogger(__name__)


def checkcontainerrunning(container_name: str):
    client = docker.from_env()
    try:
        client.containers.get(container_name)
    except:
        return False
    else:
        return True