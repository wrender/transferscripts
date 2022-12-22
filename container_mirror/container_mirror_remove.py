#!/usr/bin/python3
import logging
import subprocess
import sqlite3
import json
import docker
import yaml


# Get Configuration Values
with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Setup SQLITE Database
connection = sqlite3.connect('/opt/mirrorsync/container_mirror/transferred-containers.db', check_same_thread=False)
cursor = connection.cursor()


# Function to inspect images
def getimagedigest(name):
    try:
        client = docker.from_env()
        # Check if docker authentication is enabled
        if cfg['skopeo']['authentication']['enabled'] == True:
            skopeoinspectcmd = ['inspect','--authfile=/tmp/auth.json','docker://' + name ]
            # Run container to inspect container image and get the image digest with authentication
            result = client.containers.run('container-mirror:v1.0',volumes={cfg['skopeo']['authentication']['authfile']: {'bind': '/tmp/auth.json', 'mode': 'ro'}},command=skopeoinspectcmd,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
        else:
            skopeoinspectcmd = ['inspect','docker://' + name ]
            # Run container to inspect container image and get the image digest without authentication
            result = client.containers.run('container-mirror:v1.0',command=skopeoinspectcmd,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
        
        jsonresult = json.loads(result)
        imagedigest = jsonresult['Digest']
    except Exception as e:
        logger.error(e)
        logger.error('Could not get digest of image')
    return imagedigest


# Function to remove image from database
def skopeosyncremove(dockerimage):

    try:
        # Write image name, and digest to database so it is not downloaded again.
        print('Trying to remove image: ' + dockerimage)
        removedbitem(dockerimage)
    except Exception as e:
        logger.error('Skopeo Sync: There was an error with the skopeo sync')
        logger.error(e)
        print('Skopeo Sync: There was an error with the skopeo sync')
        print(e)
        return False
    else:
        print('Skopeo Sync: Ran removal process for ' + dockerimage + ' on database')
        logger.info('Skopeo Sync: Ran removal process for ' + dockerimage + ' on database')


# Function to remove item from database
def removedbitem(name):
    cursor = connection.cursor()
    cursor.execute("DELETE FROM transferred WHERE name= ?",(name,))
    connection.commit()
    cursor.close()
    return


# Main function for running this module
def removecontainer():

    # Using readlines() to iterate through list of container images. 
    with open('/opt/mirrorsync/container_mirror/remove-images.txt', 'r+') as f:
        alist = [line.rstrip() for line in f]

    # For each container image name in the file list images.txt
    for line in alist:

        
        # Check if colon is not in line item. As skopeo will download all tags in this case.
        if ':' not in line:
            logger.info('Skopeo Sync: There is no tag. Checking for available tags...')
            print('Skopeo Sync: There is no tag. Checking for available tags...')
            # Run skopeo list tags to get all tags for image
            try:
                client = docker.from_env()
                skopeolisttagscmd = ['list-tags','docker://' + line ]
                result = client.containers.run('container-mirror:v1.0',command=skopeolisttagscmd,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
                jsonresult = json.loads(result)

                # Loop through each image tag and skopep sync it
                for item in jsonresult['Tags']:
                    newitemwithtag = (line + ':' + item)
                    skopeosyncremove(newitemwithtag)
                    
            except Exception as e:
                logger.error('Skopeo Sync: There was an error with the skopeo sync')
                logger.error(e)
                print('Skopeo Sync: There was an error with the skopeo sync')
                print(e)


        # Don't loop and just try and skopeo sync the single image  
        else:
            skopeosyncremove(line)

removecontainer()