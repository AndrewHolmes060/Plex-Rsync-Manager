# Plex-Remote-to-Local-Sync
A small python script to sync files from a remote plex server to another plex server based on whats on the watchlist.

# Requirements:
openssh 
plexapi


# How to use
add an item to your watchlist and run the script/have the script run as a cronjob



# How to configure:

setup a rsync daemon config file [guide to setup rsync daemon](https://www.atlantic.net/vps-hosting/how-to-setup-rsync-daemon-linux-server/)

ip = 'remote access IP for your home server'

port = 'port of remote access for home plex server'

home_token = 'token of your home server'

home_tv_folder = 'folder of your TV series on your home plex server'

home_movie_folder = 'folder of your Movies on your home plex server'

user = 'name of rsync daemon user'

remote_url = 'remote access address for remote plex server'

token = 'remote plex token'

tv_folder = 'folder path of TV series on your plex server'

movie_folder = 'folder path of Movies on your plex server'
