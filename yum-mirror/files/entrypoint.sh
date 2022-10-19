#!/bin/bash
# Refresh mirror every X hours
while true;
do
  /bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-base --newest-only --download-metadata
  /bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-updates --newest-only --download-metadata
  /bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-extras --newest-only --download-metadata
  
done