#!/usr/bin/python3
import yaml
import subprocess
import sqlite3
import socket
import json

# Get Configuration Values
with open('../config.yaml') as f:
    cfg = yaml.load(f, Loader=yaml.FullLoader)

# Setup SQLITE Database
connection = sqlite3.connect("transferred-containers.db")
cursor = connection.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS transferred (name TEXT,skopeosynced INTEGER)")

# Bind to a socket port to make sure script only runs once.
s = socket.socket()         # Create a socket object
host = socket.gethostname() # Get local machine name
port = 2236                 # Reserve a port for your service.
s.bind((host, port))        # Bind to the port

# Using readlines() to iterate through list of repositories. 
with open('images.txt', 'r+') as f:
	alist = [line.rstrip() for line in f]
	#f.truncate(0)

# Function to run skopeo
def skopeosubprocess(dockerimage):

    if cfg['skopeo']['dryrun'] == 'True':
        skopeocmd = ['sudo','docker','run','--rm','-v', cfg['skopeo']['destination'] + ':/var/lib/containers/storage','--name','container-mirror',cfg['skopeo']["image"],'sync','--keep-going','--dry-run','--scoped', '--src', 'docker', '--dest', 'dir', dockerimage, '/var/lib/containers/storage']
    else:
        skopeocmd = ['sudo','docker','run','--rm','-v', cfg['skopeo']['destination'] + ':/var/lib/containers/storage','--name','container-mirror',cfg['skopeo']["image"],'sync','--keep-going','--scoped', '--src', 'docker', '--dest', 'dir', dockerimage, '/var/lib/containers/storage']

    # Use Skopeo to check if new version to download and download it
    result = subprocess.run(skopeocmd, check=True)

    return result

# Function to check database if item has been synced before 
# If it has not call skopeo sync function
def checkdbandsync(itemname):
    cursor.execute("SELECT name, skopeosynced FROM transferred WHERE name = ?", (itemname,))
    data=cursor.fetchone()
    if data is None:
        print('There is no component named %s'%itemname)
        # Call Skopeo Sync Function
        skopeosubprocess(itemname)
        
        # Insert this image and tag into database to track
        cursor.execute("INSERT INTO transferred (name, skopeosynced) VALUES (?, ?)",(itemname, '1'))
        connection.commit()
    else:
        print('Component already synced: ' + itemname)

# For each container image name in the file list images.txt
for line in alist:
    
    # Check if colon is not in line item. As skopeo will download all tags in this case.
    if ':' not in line:
      print('There is no tag. Checking for available tags...')
      skopeoinspectcmd = ['sudo','docker','run','--rm',cfg['skopeo']["image"],'inspect','docker://' + line ]
      result = subprocess.run(skopeoinspectcmd, capture_output=True)
      jsonresult = json.loads(result.stdout)

      # Loop through each image tag and skopep sync it
      for item in jsonresult['RepoTags']:
        newitemwithtag = (line + ':' + item)

        checkdbandsync(newitemwithtag)

    # Don't loop and just try and skopeo sync the single image  
    else:

        checkdbandsync(line)


# Close Database connection
cursor.close()