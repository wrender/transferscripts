#!/usr/bin/python3
import docker
import logging

# Shutdown different modules if they are running

# Setup Module logger
logger = logging.getLogger(__name__)

client = docker.from_env()

def stopcontainerrunning(container_name: str):
    RUNNING = "running"
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(container_name + " container is not running")
    else:
        container_state = container.attrs["State"]
        print('Stopping container: ' + container_name + ' . Shutting down.')
        logger.info('Stopping container: ' + container_name + ' . Shutting down.')
        container.stop()
        container.remove()
        return container_state["Status"] == RUNNING

stopcontainerrunning('apt-mirror')
stopcontainerrunning('yum-mirror')
stopcontainerrunning('container-mirror')
stopcontainerrunning('pypi-mirror')