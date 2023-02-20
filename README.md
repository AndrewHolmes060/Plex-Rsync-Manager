# Plex-Remote-to-Local-Sync
A small python script to sync files from a remote plex server to another plex server based on whats on the watchlist.

# Requirements:
openssh 
plexapi
sonarr

# How to use
add an item to your watchlist and run the script and the file will use rsync to transfer the file

have the script run as a cronjob for automated server updating

This script uses sonarr to reference whether a show is ongoing or ended to decide whether or not to remove them from your watchlist automatically

# How to configure:

you will need to setup an rsync daemon witha credentials secret on the server thats set to recieve the files: [guide to setup rsync daemon](https://www.atlantic.net/vps-hosting/how-to-setup-rsync-daemon-linux-server/)

as rsync runs in daemon mode it needs port 873 on the recievers router to be open.

then on the server thats sending the files add this script and change the variables to reflect your desired states:

user = 'user in the recievers rsync secrets file'

#details for recieving server to send files and read watchlist
home_token = 'plex token of user whos recieving server'
home_tv_folder = '/TV/Folder/from/rsync/location/'
home_movie_folder = '/Movie/Folder/from/rsync/location/'
server_name = 'Name Of Plex Server to recieve files'

#details for the sending server
remote_token = 'token of user who managed sending server'
tv_folder = '/TV/Folder/from/plex/location/'
movie_folder = '/movie/Folder/from/plex/location/'
remote_server_name='sending server name'

#Sonarr connect
# Set Host URL and API-Key
sonarr_url = 'URL for Sonarr'
sonarr_api_key = 'Sonarr API Key'