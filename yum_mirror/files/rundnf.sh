#!/bin/bash
# Refresh mirror every X hours
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=saltstack-redhat8 --download-metadata
