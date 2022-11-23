#!/usr/bin/python3
import yaml
import subprocess
import logging
import os
import shutil
import json
import container_mirror.container_mirror_run

with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

modulename = 'helm-mirror'

def runhelmmirror():
    # Setup local directory
    isExist = os.path.exists(cfg['helm']['destination'])
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(cfg['helm']['destination'])

    for item, key in cfg['helm']['mirrors'].items():
        
        # Run process to add helm repo
        subprocess.run(['/opt/mirrorsync/helm_mirror/linux-amd64/helm',
                        'repo',
                        'add',
                        item,
                        key['url']])

        # Update helm repo
        subprocess.run(['/opt/mirrorsync/helm_mirror/linux-amd64/helm',
                        'repo',
                        'update',
                        item])

        # Loop through charts and download them to destination
        for chart in key['charts']:
            logger.info('Getting charts for ' + chart)
            print('Getting charts for ' + chart)

            # Setup local directory
            isExist = os.path.exists(cfg['helm']['destination'] + '/' + item)
            if not isExist:
                # Create a new directory because it does not exist
                os.makedirs(cfg['helm']['destination'] + '/' + item)

            subprocess.run(['/opt/mirrorsync/helm_mirror/linux-amd64/helm',
                            'pull',
                            item + '/' + chart,
                            '--destination',
                            cfg['helm']['destination'] + '/' + item])
        
        # Extract the chart and get image names
            subprocess.run(['/opt/mirrorsync/helm_mirror/linux-amd64/helm',
                            'pull',
                            item + '/' + chart,
                            '--untar',
                            '--untardir',
                            cfg['helm']['destination'] + '/tmp'])

            p1 = subprocess.Popen(["/opt/mirrorsync/helm_mirror/linux-amd64/helm","--kube-version",cfg['helm']['kubeversion'],"template",cfg['helm']['destination'] + "tmp/" + chart], stdout=subprocess.PIPE)
            p2 = subprocess.Popen(["/opt/mirrorsync/helm_mirror/yq_linux_amd64","-N","..|.image? | select(.)"],stdin=p1.stdout, stdout=subprocess.PIPE)
            p1.stdout.close()
            output = p2.communicate()[0]
            jsonresult = json.dumps(output.decode('utf-8'))
            result = json.loads(jsonresult)
            resultlist = result.splitlines()
           
            # Remove the tmp chart directory once done with it
            if os.path.exists(cfg['helm']['destination'] + "tmp/" + chart):
                shutil.rmtree(cfg['helm']['destination'] + "tmp/" + chart)

            logger.info('Running Skopeo to get images for chart: ' + chart)
            print('Running Skopeo to get images for chart: ' + chart)
            # Use the container_mirror Skopeo sync functions to fetch the images
            container_mirror.container_mirror_run.runcontainermirror(resultlist)
