# mirrorsync

A simple set of scripts to automate the syncronization of various public repositories like apt, yum, pypi, & docker images. Please note this is a very interim solution. There is not a lot of error checking built into these scripts.
DNF is used for yum mirrors, apt-mirror is used for apt mirrors, SKOPEO is used for docker images, bandersnatch is used for Pypi.

## How it works

- Runs on Linux Server in DMZ
- apt-mirror, dnf, and skopeo sync the latest data from the internet
- SQLlite local db to track previosuly skopeo synced container images so they are not downloaded again
- Skopeo sync is limited to 100 anonymous pulls per day from docker hub
- Scripts rsync data to secure location

## Example repository types
- Any APT, YUM, Container
- Centos 7/8, RockyLinux, Ubuntu, DockerHub, Quay.IO

## Requirements
- Internet access
- python3, python3-pip on either Ubuntu or RHEL/CentOS/RockyLinux
- RSYNC,SSH
- Docker
- A linux user to run as
- User is able to access docker (added to docker group)
- SSH public/private keys for SSH destination From DMZ to Secure Server

## Installation & Usage
### DMZ Server
1. Git clone the project to /opt/mirrorsync/
2. Install python3, python3-pip
3. Install python plugins in files/python plugins. For example: `python3 -m pip install ./downloads/SomeProject-1.0.4.tar.gz`
4. Edit the configuration of /opt/mirrorsync/config.yaml to suit your needs
5. Setup local destination directories  (Should be larger storage. 1TB at least)
6. Ensure the directories are setup with ownership of user defined in config.yaml
7. Set ownership of /opt/mirrorsync to user defined in config.yaml
8. Run setup: `sudo /opt/mirrosync/setup.py`
9. Run the service:  sudo systemctl  enable mirrorsync --now

### Secure Server
1. Put contents of /opt/mirrorsync/container_mirror/sync_registry into /opt/sync_registry
2. Edit /opt/sync_registry/config.yaml to suit your needs
2. Setup local destination directories  (Should be larger storage. 1TB at least)
2. Setup user, ssh key, and destination directories (Setup passwordless ssh key, so both systems can ssh)
3. Run setup: `sudo /opt/sync_registry/setup.py`
4. Run the service:  sudo systemctl  enable mirrorsync --now

### Usage
-  Once the service is running on the DMZ server, you can view the log at /opt/mirrorsync/mirrorsync.log to view information, or run `sudo systemctl status mirrorsync` to view systemctl status

-  You can list images in /opt/mirrorsync/container_mirror/images.txt that you want to syncronize from the internet. For example: `echo "httpd:2.4.54" >> /opt/mirrorsync/container_images.txt`