#!/bin/bash
# Refresh mirror every X hours
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=saltstack-redhat8 --newest-only --download-metadata
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-base --newest-only --download-metadata
/bin/dnf reposync -g --delete -p /mnt/repos/ --repoid=centos-7-updates --newest-only --download-metadata
