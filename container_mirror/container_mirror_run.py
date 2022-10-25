#!/usr/bin/python3
import logging
import subprocess
import sqlite3
import socket
import json
import docker
import yaml
import time


# Get Configuration Values
with open('/opt/transferbuddy/config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup SQLITE Database
connection = sqlite3.connect('/opt/transferbuddy/container_mirror/transferred-containers.db', check_same_thread=False)
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transferred (name TEXT,skopeosynced INTEGER)")
cursor.close()

# Bind to a socket port to make sure script only runs once.
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 2236                 # Reserve a port for your service.
s.bind((host, port))        # Bind to the port


# Function to run skopeo
def skopeosubprocess(dockerimage):

    print(dockerimage)
    if cfg['skopeo']['dryrun'] == 'True':
        skopeocmd = ['sync','--keep-going','--dry-run','--scoped','--src','docker','--dest', 'dir', dockerimage,'/var/lib/containers/storage']
    else:
        skopeocmd = ['sync','--keep-going','--scoped','--src','docker','--dest','dir', dockerimage,'/var/lib/containers/storage']
     
    # Try to get image with scopeo
    try:
        client = docker.from_env()
        print(skopeocmd)
        result = client.containers.run(cfg['skopeo']["image"],volumes={cfg['skopeo']['destination']: {'bind': '/var/lib/containers/storage', 'mode': 'rw'}},command=skopeocmd,remove=True)
    except docker.errors.ContainerError as e:
        logging.error('There was an error with the skopeo sync' + e)
        print('There was an error with the skopeo sync' + e)
        print(result)
    
    return result

# Function to check database if item has been synced before 
# If it has not call skopeo sync function
def checkdbandsync(itemname):
    cursor = connection.cursor()
    cursor.execute("SELECT name, skopeosynced FROM transferred WHERE name = ?", (itemname,))
    data=cursor.fetchone()
    if data is None:
        logging.info('New item. Calling Skopeo Sync for %s'%itemname)
        # Call Skopeo Sync Function
        skopeosubprocess(itemname)
        
        # Insert this image and tag into database to track
        cursor.execute("INSERT INTO transferred (name, skopeosynced) VALUES (?, ?)",(itemname, '1'))
        connection.commit()
        cursor.close()
    else:
        logging.info('Image already synced: ' + itemname)
        print('Image already synced: ' + itemname)

def runcontainermirror():
    # Using readlines() to iterate through list of repositories. 
    with open('/opt/transferbuddy/container_mirror/images.txt', 'r+') as f:
        alist = [line.rstrip() for line in f]
        f.truncate(0)

    # For each container image name in the file list images.txt
    for line in alist:
        
        # Check if colon is not in line item. As skopeo will download all tags in this case.
        if ':' not in line:
            logging.info('There is no tag. Checking for available tags...')
            print('There is no tag. Checking for available tags...')
            skopeolisttagscmd = ['list-tags','docker://' + line ]
            client = docker.from_env()
            result = client.containers.run(cfg['skopeo']["image"],command=skopeolisttagscmd,remove=True)
            jsonresult = json.loads(result)

            # Loop through each image tag and skopep sync it
            for item in jsonresult['Tags']:
                newitemwithtag = (line + ':' + item)
                checkdbandsync(newitemwithtag)

        # Don't loop and just try and skopeo sync the single image  
        else:
            checkdbandsync(line)

    logging.info('Checking for images in /opt/transferbuddy/container_mirror/images.txt...')

runcontainermirror()