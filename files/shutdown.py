#!/usr/bin/python3
import docker

# Shutdown different modules if they are running

client = docker.from_env()

def checkcontainerrunning(container_name: str):
    RUNNING = "running"
    try:
        container = client.containers.get(container_name)
    except docker.errors.NotFound as exc:
        print(f"Check container name!\n{exc.explanation}")
    else:
        container_state = container.attrs["State"]
        container.stop()
        container.remove()
        return container_state["Status"] == RUNNING

checkcontainerrunning('apt-mirror')
checkcontainerrunning('yum-mirror')
checkcontainerrunning('container-mirror')
checkcontainerrunning('pypi-mirror')