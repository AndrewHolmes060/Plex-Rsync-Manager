#!/usr/bin/python3
import pathlib
import shutil
import subprocess
import plexapi
import arrapi
from logging import exception
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.base import PlexObject
from arrapi import SonarrAPI

#details for home server to send files and read watchlist

#username for rsync recieiving user

user = 'user on the recievers rsync machine'

#details for recieving server to send files and read watchlist
home_token = 'token of user whos recieving server'
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
sonarr = SonarrAPI(sonarr_url, sonarr_api_key)

#connect to Connect To reciever server
home_account = MyPlexAccount(token=home_token)
home_resources = home_account.resources()
print(home_account)
home_plex = home_account.resource(server_name).connect()
connected_server = home_plex.account()
home_ip = (connected_server.publicAddress)

#connect to sending server
remote_account = MyPlexAccount(token=remote_token)
remote_resources = remote_account.resources()
remote_plex = remote_account.resource(remote_server_name).connect()
remote_connected_server = remote_plex.account()
remote_url = ("http://"+remote_connected_server.publicAddress+":"+remote_connected_server.publicPort)

#connect to remote server
plex = PlexServer(remote_url, remote_token)

#get user watchlist
watchlist = home_account.watchlist()
print (watchlist)
item = 0
while item < len(watchlist):
    #search through the watchlist to check for new files
    Watchlist_item = (watchlist[item])
    result = plex.library.search(guid=Watchlist_item.guid, libtype=Watchlist_item.type)
    #if the watchlist item is a TV Show
    if Watchlist_item.type == "show" :
        if result != None:
            title = (Watchlist_item.title)
            try:
                #get file location of tv folder to sync
                last_episode = plex.library.section('TV shows').get('{}'.format(title)).episodes()[-1]
                for part in last_episode.iterParts():
                    directory = (part.file)
                    directory = pathlib.Path(directory)
                    dir_length = ("{}".format(directory))
                    dir_list = dir_length.split('/')
                    directory = directory.parts[len(dir_list)-3]
                    directory = tv_folder+directory
                    print("syncing {}...".format(title))
                    subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress","{}".format(directory), "{}@{}::files{}/".format(user, home_ip, home_tv_folder)])
                    sonarr_series = sonarr.search_series(title)
                    sonarr_status = sonarr_series[0].status
                    print("This show status is: {}".format(sonarr_status))
                    if sonarr_status == "ended":
                        #get the list of episodes on the remote server
                        remote_episodes = set(plex.library.section('TV shows').get('{}'.format(title)).episodes())
                        remote_formatted_episodes = ["<{}-{}-{}>".format(title, episode.seasonNumber, episode.index) for episode in remote_episodes]
                        remote_formatted_episodes = set(remote_formatted_episodes)
                        #get the list of episodes on the home server
                        home_episodes = set(home_plex.library.section('TV shows').get('{}'.format(title)).episodes())
                        home_formatted_episodes = ["<{}-{}-{}>".format(title, episode.seasonNumber, episode.index) for episode in home_episodes]
                        home_formatted_episodes = set(home_formatted_episodes)
                        #check if the remote server's episodes are a subset of the home server's episodes
                        if remote_formatted_episodes.issubset(home_formatted_episodes):
                            #if they are a subset, remove the episode from the watchlist
                            home_account.removeFromWatchlist(Watchlist_item)
            except Exception as e: print(e)
            item = item + 1
        else :
            #if  watchlist item isnt on the remote server
            item = item + 1
            print("{} is not on the server".format(title))

    #if the watchlist item is a movie
    elif Watchlist_item.type == "movie":
        if result != None:
            title = (Watchlist_item.title)
            print(title)
            try:
                movie = plex.library.section('Movies').get('{}'.format(title)).media[0].parts[0].file
                directory = pathlib.Path(movie)
                dir_length = ("{}".format(directory))
                dir_list = dir_length.split('/')
                directory = directory.parts[len(dir_list)-2]
                directory = movie_folder+directory
                print("syncing {}...".format(title))
                subprocess.run(["rsync", "-avO", "--bwlimit=100000", "--ignore-existing", "--progress","{}".format(directory), "{}@{}::files{}".format(user, home_ip, home_movie_folder)])
                home_account.removeFromWatchlist(Watchlist_item)
            except Exception as e: print(e)
           #if any errors
            item = item + 1
        else :
            #if  watchlist item isnt on the remote server
            item = item + 1
            print("{} has not arrived on the server yet...".format(title))
    else:
        #finished checking the watchlist
        
        item = item + 1
        print("all done!")
        exit