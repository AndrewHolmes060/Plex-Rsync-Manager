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

remote_server_user = home_account.resource('Notflix')
watched_remote = remote_server_user.connect()

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

        #syncing watched TV Shows between servers
        remote_plex_shows = set(list(map((lambda x: x.title), watched_remote.library.section('TV').search())))
        home_plex_shows = set(list(map((lambda x: x.title), home_plex.library.section('TV Shows').search())))
        common_shows = remote_plex_shows & home_plex_shows
        for show_name in common_shows:
            remote_plex_show = watched_remote.library.section('TV').get(show_name)
            home_plex_show = home_plex.library.section('TV Shows').get(show_name)
            for ep in remote_plex_show.episodes():
                for ep2 in home_plex_show.episodes():
                    if ep.title == ep2.title:
                        if ep2.isWatched and not ep.isWatched:
                            print("marking {} as watched on remote server".format(ep))
                            ep.markWatched()
                        elif ep.isWatched and not ep2.isWatched:
                            print("marking {} as watched on home server".format(ep))
                            ep2.markWatched()
                        break
        
        #syncing watched movies between servers
        remote_plex_movies = set(list(map((lambda x: x.title), watched_remote.library.section('Movies').search())))
        home_plex_movies = set(list(map((lambda x: x.title), home_plex.library.section('Films').search())))
        common_movies = remote_plex_movies & home_plex_movies
        for movie_name in common_movies:
            remote_plex_movies = watched_remote.library.section('Movies').get(movie_name)
            home_plex_movies = home_plex.library.section('Films').get(movie_name)
            for watched_movie_home in remote_plex_movies:
                for watched_movie_remote in home_plex_movies:
                    if watched_movie_home.title == watched_movie_remote.title:
                        if watched_movie_home.isWatched and not watched_movie_remote.isWatched:
                            print("marking {} as watched on home server".format(watched_movie_remote))
                            watched_movie_remote.markWatched()
                        elif watched_movie_remote.isWatched and not watched_movie_home.isWatched:
                            print("marking {} as watched on remote server".format(watched_movie_home))
                            watched_movie_home.markWatched()
                        break
        print("all done!")
        exit


