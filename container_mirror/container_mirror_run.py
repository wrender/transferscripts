#!/usr/bin/python3
import logging
import subprocess
import sqlite3
import socket
import json
import docker
import yaml
import psutil
import os


# Get Configuration Values
with open('/opt/mirrorsync/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup Module logger
logger = logging.getLogger(__name__)

# Setup SQLITE Database
connection = sqlite3.connect('/opt/mirrorsync/container_mirror/transferred-containers.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transferred (name TEXT,digest TEXT)")
cursor.close()


# Function to run skopeo
def skopeosync(dockerimage):

    if cfg['skopeo']['dryrun'] == True:
        skopeocmd = ['sync','--keep-going','--dry-run','--scoped','--src','docker','--dest', 'dir', dockerimage,'/var/lib/containers/storage']
    else:
        skopeocmd = ['sync','--keep-going','--scoped','--src','docker','--dest','dir', dockerimage,'/var/lib/containers/storage']
     
    # Try to get image with scopeo
    try:
        imagedigest = getimagedigest(dockerimage)
        # Call function to check local database for image
        if checkdb(imagedigest) == True:
            print('Skopeo Sync: Image already synced - ' + dockerimage + ' ' + imagedigest)
            logger.info('Skopeo Sync: Image already synced - ' + dockerimage + ' ' + imagedigest)
        else:
            # Try syncing the image
            print('Skopeo Sync: Syncing image ' + dockerimage + ' ' + imagedigest)
            logger.info('Skopeo Sync: Syncing image ' + dockerimage + ' ' + imagedigest)
            client = docker.from_env()
            client.containers.run('container-mirror:latest',volumes={cfg['skopeo']['destination']: {'bind': '/var/lib/containers/storage', 'mode': 'rw'}},command=skopeocmd,remove=True,user=cfg['mirrorsync']['systemduser'])

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
    

# Function to inspect images
def getimagedigest(name):
    skopeoinspectcmd = ['inspect','docker://' + name ]
    try:
        client = docker.from_env()
        result = client.containers.run('container-mirror:latest',command=skopeoinspectcmd,remove=True)
        jsonresult = json.loads(result)
        imagedigest = jsonresult['Digest']
    except:
        logger.error('Could not get digest of image')
    
    return imagedigest


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

    subprocess.call(['rsync',
    '--remove-source-files',
    '-avz',
    '-e',
    "ssh '-i" + cfg['rsync']['sshidentity'] + "'",
    cfg['skopeo']['destination'],
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['skopeo']['rsyncdestination']])


    # For Skopeo remove old directories, as Skopeo currently doesn't support syncing files
    subprocess.call(['find',cfg['skopeo']['destination'],'-empty','-delete'])


# Main function for running this module
def runcontainermirror():

    if cfg['mirrorsync']['systemduser'] != 'root':
            subprocess.run(['mkdir','-p',cfg['skopeo']['destination']], check=True)

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
            skopeolisttagscmd = ['list-tags','docker://' + line ]

            # Run skopeo list tags to get all tags for image
            try:
                client = docker.from_env()
                result = client.containers.run('container-mirror:latest',command=skopeolisttagscmd,remove=True)
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

runcontainermirror()