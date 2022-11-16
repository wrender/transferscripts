#!/bin/bash
# Refresh mirror every X hours
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=saltstack-redhat8 --download-metadata
/bin/wget -P /mnt/repos/saltstack-redhat8 https://repo.saltproject.io/py3/redhat/8/x86_64/3004/SALTSTACK-GPG-KEY.pub
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-base --download-metadata
/bin/wget -P /mnt/repos/centos-7-base http://mirror.csclub.uwaterloo.ca/centos/RPM-GPG-KEY-CentOS-7
