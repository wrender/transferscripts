# mirrorsync

A simple set of scripts to automate the syncronization of various public repositories like apt, yum, pypi, & docker images.
DNF is used for yum mirrors, apt-mirror is used for apt mirrors, SKOPEO is used for docker images, bandersnatch is used for Pypi.

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
- Internet access
- python3, python3-yaml, python3-jinja2, Python Docker SDK
- RSYNC,SSH
- Docker
- A linux user to run as
- User is able to access docker (added to docker group)
- SSH public/private keys for SSH destination

## Installation & Usage
1. Git clone the project to /opt/mirrorsync/
2. Edit the configuration of /opt/mirrorsync/config.yaml to suit your needs
3. Setup destination directories
4. Run setup: `sudo /opt/mirrosync/setup.py`
5. Run the service:  systemctl start mirrorsync
6. Watch the log at: /opt/mirrorsync/mirrorsync.log
