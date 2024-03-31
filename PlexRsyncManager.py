#!/usr/bin/python3
import pathlib
import shutil
import subprocess
import plexapi
import arrapi
import os
import json
from logging import exception
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
from plexapi.base import PlexObject
from arrapi import SonarrAPI


# Load secrets
with open('secrets.json') as f:
    secrets = json.load(f)

# Extract Rsync details
rsync_Mode = secrets['Rsync Details']['Mode']
rsync_Direction = secrets['Rsync Details']['Direction']
remote_username = secrets['sending Server Details']['remote_username']
sending_Plex_token = secrets['sending Server Details']['sending_Plex_token']
sending_TV_folder = secrets['sending Server Details']['sending_TV_folder']
sending_movie_folder = secrets['sending Server Details']['sending_movie_folder']
sending_Server_name = secrets['sending Server Details']['sending_Server_name']
sending_TV_name = secrets['sending Server Details']['sending_TV_name']
sending_Movies_name = secrets['sending Server Details']['sending_Movies_name']

recieving_Plex_token = secrets['recieving Server Details']['recieving_Plex_token']
recieving_tv_folder = secrets['recieving Server Details']['recieving_tv_folder']
recieving_movie_folder = secrets['recieving Server Details']['recieving_movie_folder']
recieving_server_name = secrets['recieving Server Details']['recieving_server_name']
recieving_TV_name = secrets['recieving Server Details']['recieving_TV_name']
recieving_Movies_name = secrets['recieving Server Details']['recieving_Movies_name']

# Sonarr connect
sonarr_url = secrets['Sonarr connect']['sonarr_url']
sonarr_api_key = secrets['Sonarr connect']['sonarr_api_key']
sonarr = SonarrAPI(sonarr_url, sonarr_api_key)


#connect to Connect To sending server
sending_account = MyPlexAccount(token=sending_Plex_token)
sending_resources = sending_account.resources()

sending_plex = sending_account.resource(sending_Server_name).connect()
sending_connected_server = sending_plex.account()
sending_ip = (sending_connected_server.publicAddress)
sending_url = ("http://"+sending_connected_server.publicAddress+":"+sending_connected_server.publicPort)


#connect to recieving server
recieving_account = MyPlexAccount(token=recieving_Plex_token)
recieving_resources = recieving_account.resources()
recieving_plex = recieving_account.resource(recieving_server_name).connect()
recieving_connected_server = recieving_plex.account()
recieving_url = ("http://"+recieving_connected_server.publicAddress+":"+recieving_connected_server.publicPort)


print("---------------------------------\n---- Rsyncing from {} to {} ----\n---------------------------------".format(sending_account, recieving_account))
#connect to sending server
plex = PlexServer(sending_url, sending_Plex_token)

#get user watchlist
watchlist = recieving_account.watchlist()
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
                last_episode = sending_plex.library.section(sending_TV_folder).get('{}'.format(title)).episodes()[-1]
                for part in last_episode.iterParts():
                    directory = (part.file)
                    directory = pathlib.Path(directory)
                    dir_length = ("{}".format(directory))
                    dir_list = dir_length.split('/')
                    directory = directory.parts[len(dir_list)-3]
                    show_directory = directory
                    directory = sending_TV_folder+directory
                    print("syncing {}...".format(title))
                    if rsync_Direction == "receive_to":
                        if rsync_Mode == "daemon_rsync":
                            subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress", "{}@{}::{}/".format(remote_username, sending_ip, directory),"{}{}".format(recieving_tv_folder, show_directory)])
                        elif rsync_Mode == "remote_shell_rsync":
                            subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress", "{}@{}:{}/".format(remote_username, sending_ip, directory),"{}{}".format(recieving_tv_folder, show_directory)])
                        else:
                            print("Rsync Setup Script not run please run that to populate the secrets file")
                            exit
                    elif rsync_Direction == "send_from":
                        if rsync_Mode == "daemon_rsync":
                            subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress","{}{}".format(recieving_tv_folder, show_directory), "{}@{}::{}/".format(remote_username, sending_ip, directory)])
                        elif rsync_Mode == "remote_shell_rsync":
                            subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress","{}{}".format(recieving_tv_folder, show_directory), "{}@{}:{}/".format(remote_username, sending_ip, directory)])
                        else:
                            print("Rsync Setup Script not run please run that to populate the secrets file")
                            exit
                    else:
                        print("Rsync Setup Script not run please run that to populate the secrets file")
                        exit                    
                    sonarr_series = sonarr.search_series(title)
                    sonarr_status = sonarr_series[0].status
                    print("This show status is: {}".format(sonarr_status))
                    if sonarr_status == "ended":
                        #get the list of episodes on the sending server
                        sending_episodes = set(plex.library.section(sending_TV_folder').get('{}'.format(title)).episodes())
                        sending_formatted_episodes = ["<{}-{}-{}>".format(title, episode.seasonNumber, episode.index) for episode in sending_episodes]
                        sending_formatted_episodes = set(sending_formatted_episodes)
                        #get the list of episodes on the home server
                        home_episodes = set(sending_plex.library.section(sending_TV_folder).get('{}'.format(title)).episodes())
                        home_formatted_episodes = ["<{}-{}-{}>".format(title, episode.seasonNumber, episode.index) for episode in home_episodes]
                        home_formatted_episodes = set(home_formatted_episodes)
                        #check if the sending server's episodes are a subset of the home server's episodes
                        if sending_formatted_episodes.issubset(home_formatted_episodes):
                            #if they are a subset, remove the episode from the watchlist
                            sending_account.removeFromWatchlist(Watchlist_item)
            except Exception as e: print(e)
            item = item + 1
        else :
            #if  watchlist item isnt on the sending server
            item = item + 1
            print("{} is not on the server".format(title))

    #if the watchlist item is a movie
    elif Watchlist_item.type == "movie":
        if result != None:
            title = (Watchlist_item.title)
            print(title)
            try:
                movie = sending_plex.library.section(sending_Movies_name).get('{}'.format(title)).media[0].parts[0].file
                directory = pathlib.Path(movie)
                dir_length = ("{}".format(directory))
                dir_list = dir_length.split('/')
                directory = directory.parts[len(dir_list)-2]
                directory = sending_movie_folder+directory
                print("syncing {}...".format(title))
                if rsync_Direction == "receive_to":
                    if rsync_Mode == "daemon_rsync":
                        subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress", "{}@{}::{}/".format(remote_username, sending_ip, directory),"{}".format(recieving_movie_folder)])
                        sending_account.removeFromWatchlist(Watchlist_item)
                    elif rsync_Mode == "remote_shell_rsync":
                        subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress", "{}@{}:{}/".format(remote_username, sending_ip, directory),"{}".format(recieving_movie_folder)])
                        sending_account.removeFromWatchlist(Watchlist_item)
                    else:
                        print("Rsync Setup Script not run please run that to populate the secrets file")
                        exit
                elif rsync_Direction == "send_from":
                    if rsync_Mode == "daemon_rsync":
                        subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress","{}".format(recieving_movie_folder), "{}@{}::{}/".format(remote_username, sending_ip, directory)])
                        sending_account.removeFromWatchlist(Watchlist_item)
                    elif rsync_Mode == "remote_shell_rsync":
                        subprocess.run(["rsync", "-avO", "--ignore-existing", "--bwlimit=100000","--progress","{}".format(recieving_movie_folder), "{}@{}:{}/".format(remote_username, sending_ip, directory)])
                        sending_account.removeFromWatchlist(Watchlist_item)
                    else:
                        print("Rsync Setup Script not run please run that to populate the secrets file")
                        exit
                else:
                    print("Rsync Setup Script not run please run that to populate the secrets file")
                    exit                       
            except Exception as e: print(e)
           #if any errors
            item = item + 1
        else :
            #if  watchlist item isnt on the sending server
            item = item + 1
            print("{} has not arrived on the server yet...".format(title))
    else:
        #finished checking the watchlist
        
        item = item + 1
        print("all done!")
        exit
