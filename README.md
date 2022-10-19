# transferscripts

A simple set of scripts to automate the syncronization of apt, yum, docker images.
DNF is used for yum mirrors, apt-mirror is used for apt mirrors, SKOPEO is used for docker images.

## How it works

- Scripts run on Linux Server in DMZ on a cron schedule
- apt-mirror, dnf, and skopeo sync the latest data from the internet.
- Scripts rsync data to secure location

## Example repository types
- Centos 7/8, RockyLinux, Ubuntu, DockerHub, Quay.IO

## Requirements

- python3, python3-yaml, python3-jinja2
- RSYNC 
- Docker
- Passwordless sudo access to docker, and filesystem.
- SSH public/private keys setup for user to syncronization destination
