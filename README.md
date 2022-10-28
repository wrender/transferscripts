# transferbuddy

A simple set of scripts to automate the syncronization of apt, yum, docker images.
DNF is used for yum mirrors, apt-mirror is used for apt mirrors, SKOPEO is used for docker images.

## How it works

- Runs on Linux Server in DMZ
- apt-mirror, dnf, and skopeo sync the latest data from the internet
- SQLlite local db to track previosuly skopeo synced container images so they are not downloaded again
- Skopeo sync is limited to 100 anonymous pulls per day from docker hub
- Scripts rsync data to secure location


## Example repository types
- Any APT, YUM, container
- Centos 7/8, RockyLinux, Ubuntu, DockerHub, Quay.IO

## Requirements

- python3, python3-yaml, python3-jinja2, Docker SDK
- RSYNC,SSH
- Docker
- A user to run as
- User is able to access docker.
- SSH public/private keys for SSH destination
