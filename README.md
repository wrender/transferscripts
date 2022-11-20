# mirrorsync

A simple set of scripts (Python modules) to automate the syncronization of various public repositories like apt, yum, pypi, & docker images. DNF is used for yum mirrors, apt-mirror is used for apt mirrors, SKOPEO is used for docker images, bandersnatch is used for Pypi.

Please note this is a very interim solution. There is not a lot of error checking built into these scripts.

## How it works

- Runs on Linux Server in DMZ
- apt-mirror, dnf, skopeo, bandersnatch sync the latest packages from the internet
- SQLlite local database to track previosuly skopeo synced container images so they are not downloaded again
- Scripts rclone data to secure location

Note: Skopeo sync is limited to about 200 anonymous pulls per day from docker hub. This is due limitations put in place by docker hub. An enterprise account can be purchased that allows more.

## Example repository types
- Any APT, YUM, Container
- Centos 7/8, RockyLinux, Ubuntu, DockerHub, Quay.IO

## Requirements
- Internet access
- Ubuntu 20.04+ or RHEL/CentOS/RockyLinux 8.0+
- Python 3.10+
- RCLONE,SSH
- Docker
- A linux user to run as
- User is able to access docker (added to docker group)
- SSH public/private keys for SSH destination From DMZ to Secure Server

## Installation
### DMZ Server
This service runs on a server in the DMZ that has access to the internet. It downloads repositories from the internet using various methods.
1. Git clone the project to /opt/mirrorsync/
2. Install python3.10 or newer, python3.10-pip or newer
3. Setup a virtual environment:  See: https://docs.python.org/3/library/venv.html
4. Switch to the virtual environment and install python plugins in files/python-plugins. For example: `pip3.10 install ./downloads/SomeProject-1.0.4.tar.gz`
5. Edit the configuration of /opt/mirrorsync/config.yaml to suit your needs
6. Setup local destination directories  (Should be larger storage. 1TB at least)
7. Ensure the directories are setup with ownership of user defined in config.yaml
8. Set ownership of /opt/mirrorsync to user defined in config.yaml
9. Run setup: `sudo /opt/mirrosync/setup.py`
10. Generate ssh keys for the user. `ssh-keygen` and setup SSH connection to secure server.
11. Run `rclone config` and setup a new remote called "remote" using the SSH keys to authenticate to the remote. The remote should be address of the secure server.
12. Run the service:  sudo systemctl  enable mirrorsync --now

### Secure Server
The sync_registry service is installed on the server that can view the remote directory, and has access to the docker registry.
1. Put contents of /opt/mirrorsync/container_mirror/sync_registry into /opt/sync_registry
2. Edit /opt/sync_registry/config.yaml to suit your needs
3. Setup local destination directories  (Should be larger storage. 1TB at least)
4. Setup user, ssh key, and destination directories (Setup passwordless ssh key, so both systems can ssh)
5. Install python plugins in files/python-plugins. For example: `python3 -m pip install ./downloads/SomeProject-1.0.4.tar.gz`
6. Run setup: `sudo /opt/sync_registry/setup.py`
7. Run the service:  sudo systemctl  enable mirrorsync --now

## Usage
-  Once the service is running on the DMZ server, you can view the log at /opt/mirrorsync/mirrorsync.log to view information, or run `sudo systemctl status mirrorsync` to view systemctl status

-  You can list images in /opt/mirrorsync/container_mirror/images.txt that you want to syncronize from the internet. For example: `echo "httpd:2.4.54" >> /opt/mirrorsync/container_images.txt`