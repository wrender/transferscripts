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
    if cfg['skopeo']['dryrun'] == True:
        skopeocmd = ['sync','--keep-going','--dry-run','--scoped','--src','docker','--dest', 'dir', dockerimage,'/var/lib/containers/storage']
    else:
        skopeocmd = ['sync','--keep-going','--scoped','--src','docker','--dest','dir', dockerimage,'/var/lib/containers/storage']
     
    # Try to get image with scopeo
    try:
        client = docker.from_env()
        print(skopeocmd)
        result = client.containers.run('container-mirror:latest',volumes={cfg['skopeo']['destination']: {'bind': '/var/lib/containers/storage', 'mode': 'rw'}},command=skopeocmd,remove=True,user=cfg['mirrorsync']['systemduser'])
    except Exception as e:
        logger.error('There was an error with the skopeo sync')
        logger.error(e)
        print('There was an error with the skopeo sync')
        print(e)
    
    return result

# Function to check database if item has been synced before 
# If it has not call skopeo sync function
def checkdbandsync(itemname):
    cursor = connection.cursor()
    cursor.execute("SELECT name, skopeosynced FROM transferred WHERE name = ?", (itemname,))
    data=cursor.fetchone()
    if data is None:
        logger.info('New item. Calling Skopeo Sync for %s'%itemname)
        # Call Skopeo Sync Function
        skopeosubprocess(itemname)
        
        # Insert this image and tag into database to track
        cursor.execute("INSERT INTO transferred (name, skopeosynced) VALUES (?, ?)",(itemname, '1'))
        connection.commit()
        cursor.close()
    else:
        logger.info('Image already synced: ' + itemname)
        print('Image already synced: ' + itemname)


# Function to check for pid file
def checkforpid(pidfile):

   # Check if path exists
    if os.path.isfile(pidfile):
        openpidfile = open(pidfile, "r")
        pidline = openpidfile.readline()
        pid = int(pidline)
        print(pid)
        openpidfile.close()

        # Check for running pid
        if psutil.pid_exists(pid):
            print("a process with pid %d exists" % pid)
            logger.info("Not going to run again now. A process with pid %d exists" % pid)
            return True
        else:
            print("Process with pid %d does not exist" % pid)
            logger.info("Process with pid %d does not exist" % pid)
            return False

    # Return false if no pid file
    else:
        return False


# Function to rsync data from container mirror to ssh destination
def rsynccontainermirror():

    subprocess.call(['rsync',
    '--remove-source-files',
    '-avz',
    '-e',
    "ssh '-i" + cfg['rsync']['sshidentity'] + "'",
    cfg['skopeo']['destination'],
    cfg['rsync']['sshuser'] + '@' + cfg['rsync']['sshserver'] + ':' + cfg['skopeo']['rsyncdestination']])

    subprocess.call(['find',cfg['skopeo']['destination'] + '/','-empty','-delete'])



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
            logger.info('There is no tag. Checking for available tags...')
            print('There is no tag. Checking for available tags...')
            skopeolisttagscmd = ['list-tags','docker://' + line ]

            # Run skopeo list tags to get all tags for image
            try:
                client = docker.from_env()
                result = client.containers.run('container-mirror:latest',command=skopeolisttagscmd,remove=True)
                jsonresult = json.loads(result)

                # Loop through each image tag and skopep sync it
                for item in jsonresult['Tags']:
                    newitemwithtag = (line + ':' + item)
                    checkdbandsync(newitemwithtag)
                    
            except Exception as e:
                logger.error('There was an error with the skopeo sync')
                logger.error(e)
                print('There was an error with the skopeo sync')
                print(e)


        # Don't loop and just try and skopeo sync the single image  
        else:
            checkdbandsync(line)

    # Run function to syncronize containers to destination
    rsynccontainermirror()
