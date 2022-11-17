#!/usr/bin/python3
import logging
import subprocess
import sqlite3
import json
import docker
import yaml
import os


# Get Configuration Values
with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.SafeLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Setup SQLITE Database
connection = sqlite3.connect('/opt/mirrorsync/container_mirror/transferred-containers.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transferred (name TEXT,digest TEXT)")
cursor.close()

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


# Function to run skopeo
def skopeosync(dockerimage):
    skopeocmd = ['sync','--keep-going']
    if cfg['skopeo']['dryrun']:
        skopeocmd.append("--dry-run")
    if cfg['skopeo']['authentication']['enabled']:
        skopeocmd.append('--authfile=' + cfg['skopeo']['authentication']['authfile'])
    skopeocmd.extend(['--scoped','--src','docker','--dest', 'dir', dockerimage,'/mnt/repos'])
            
    # Try to get image with scopeo
    try:
        imagedigest = getimagedigest(dockerimage)
        # Call function to check local database for image
        if checkdb(imagedigest) == True:
            print('Skopeo Sync: Image already synced - ' + dockerimage + ' ' + imagedigest)
            logger.info('Skopeo Sync: Image already synced - ' + dockerimage + ' ' + imagedigest)
        else:
            try:
                # Try syncing the image
                print('Skopeo Sync: Syncing image ' + dockerimage + ' ' + imagedigest)
                logger.info('Skopeo Sync: Syncing image ' + dockerimage + ' ' + imagedigest)
                client = docker.from_env()
                if cfg['skopeo']['authentication']['enabled']:
                    client.containers.run('container-mirror:v1.0',volumes={cfg['skopeo']['authentication']['authfile']: {'bind': '/tmp/auth.json', 'mode': 'ro'},cfg['skopeo']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'}},command=skopeocmd,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
                else:
                    client.containers.run('container-mirror:v1.0',volumes={cfg['skopeo']['destination']: {'bind': '/mnt/repos', 'mode': 'rw'}},command=skopeocmd,remove=True,user=cfg['mirrorsync']['systemduser'],network_mode=cfg['mirrorsync']['networkmode'],use_config_proxy=cfg['mirrorsync']['configproxy'])
            except Exception as e:
                logger.error('Skopeo Sync: There was an error with the skopeo sync')
                logger.error(e)
                print('Skopeo Sync: There was an error with the skopeo sync')
                print(e)
                return False
            else:
                print('Skopeo Sync: Successfully synced image ' + dockerimage + ' ' + imagedigest)
                logger.info('Skopeo Sync: Successfully synced image ' + dockerimage + ' ' + imagedigest)
                # Write image name, and digest to database so it is not downloaded again.
                writedb(dockerimage, imagedigest)

                # Run function to syncronize container to destination
                rsynccontainermirror()

                return True
            
    except Exception as e:
        logger.error('Skopeo Sync: There was an error with the skopeo sync')
        logger.error(e)
        print('Skopeo Sync: There was an error with the skopeo sync')
        print(e)


# Function to check database if item has been synced before 
def checkdb(digest):
    cursor = connection.cursor()
    cursor.execute("SELECT name, digest FROM transferred WHERE digest = ?", (digest,))
    data=cursor.fetchone()
    cursor.close()
    if data is None:
        return False
    else:
        return True

# Function to write name and digest to database
def writedb(name, digest):
    # Insert this image and tag into database to track
    cursor = connection.cursor()
    cursor.execute("INSERT INTO transferred (name, digest) VALUES (?, ?)",(name, digest))
    connection.commit()
    cursor.close()

    return

# Function to rsync data from container mirror to ssh destination
def rsynccontainermirror():

    if cfg['skopeo']['rsync']['enabled'] == True:
        try:
            subprocess.call(['rsync',
            '--remove-source-files',
            '-avz',
            cfg['skopeo']['destination'],
            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['skopeo']['rsync']['rsyncdestination']])
        except Exception as e:
            logger.error(e)
            print(e)
        else:
            # Write a file showing completed
            finishpath = cfg['skopeo']['destination'] + '/completed.txt'
            f = open(finishpath, "x")
            f.write("completed transfer run")

            subprocess.call(['rsync',
            '--remove-source-files',
            '-avz',
            cfg['skopeo']['destination'] + '/completed.txt',
            cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['skopeo']['rsync']['rsyncdestination']])
        finally:    
            # For Skopeo remove old directories, as Skopeo currently doesn't support syncing files
            subprocess.call(['find',cfg['skopeo']['destination'],'-empty','-delete'])
    else:
        return


# Main function for running this module
def runcontainermirror():

    # Setup local directory
    isExist = os.path.exists(cfg['skopeo']['destination'])
    if not isExist:
        # Create a new directory because it does not exist
        os.makedirs(cfg['skopeo']['destination'])

    logger.info('Checking for images in /opt/mirrorsync/container_mirror/images.txt...')

    # Using readlines() to iterate through list of repositories. 
    with open('/opt/mirrorsync/container_mirror/images.txt', 'r+') as f:
        alist = [line.rstrip() for line in f]
        f.truncate(0)

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
                    skopeosync(newitemwithtag)
                    
            except Exception as e:
                logger.error('Skopeo Sync: There was an error with the skopeo sync')
                logger.error(e)
                print('Skopeo Sync: There was an error with the skopeo sync')
                print(e)


        # Don't loop and just try and skopeo sync the single image  
        else:
            skopeosync(line)
