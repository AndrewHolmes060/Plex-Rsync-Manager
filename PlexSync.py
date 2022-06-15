#!/usr/bin/python3
import plexapi
from plexapi.myplex import MyPlexAccount
from plexapi.server import PlexServer
import pathlib
import shutil
import subprocess

#details for home_ server to send files and read watchlist
ip = 'remote access IP for home_ plex'
port = 'port of remote access plex'
home_token = 'token'
home_tv_folder = '/TVShows/'
home_movie_folder = '/Movies/'
user = 'name of rsync user'




#remote server details to grab videos and sync
remote_url = 'remote access address for remote plex server'
token = 'token'
tv_folder = '/mnt/data/media/TV/'
movie_folder = '/mnt/data/media/Movies/'

#connect to each server
home_url = 'http://{}:{}'.format(ip, port)
home_account = MyPlexAccount(home_token)
home_plex = PlexServer(home_url, home_token)

account = MyPlexAccount(token)
plex = PlexServer(remote_url, token)



#get user watchlist
watchlist = home_account.watchlist()
print (watchlist)
item = 0
while item < len(watchlist):
    #search through the watchlist to check for new files
    Watchlist_item = (watchlist[item])
    result = plex.library.search(guid=Watchlist_item.guid, libtype=Watchlist_item.type)
    home_result = home_plex.library.search(guid=Watchlist_item.guid, libtype=Watchlist_item.type)
    #if the watchlist item is a TV Show
    if Watchlist_item.type == "show" :
        if result != None:
            title = (Watchlist_item.title)
            try:
                #get file location of tv folder to sync
                last_episode = plex.library.section('TV').get('{}'.format(title)).episodes()[-1]
                for part in last_episode.iterParts():
                    directory = (part.file)
                    directory = pathlib.Path(directory)
                    directory = directory.parts[2]
                    directory = tv_folder+directory
                    print("syncing {}...".format(title))
                    subprocess.call(["rsync", "-a","-v","--backup","--progress","{}".format(directory), "{}@{}::files{}".format(user, ip, home_tv_folder)])            
            except Exception:
                pass
            #if any errors
            item = item + 1
        else :
            #if  watchlist item isnt on the remote server
            item = item + 1
            print("{} is not on the server".format(title))

    #if the watchlist item is a movie
    elif Watchlist_item.type == "movie":
        if result != None and Watchlist_item:
            title = (Watchlist_item.title)
            try:
                movie = plex.library.section('Movies').get('{}'.format(title)).media[0].parts[0].file
                directory = pathlib.Path(movie)
                directory = directory.parts[2]
                directory = movie_folder+directory
                print("syncing {}...".format(title))
                subprocess.call(["rsync", "-a","-v","--backup","--progress","{}".format(directory), "{}@{}::files{}".format(user, ip, home_movie_folder)])
                home_account.removeFromWatchlist(Watchlist_item)
            except Exception:
                pass
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


