# Plex-Rsync-Manager

Plex-Rsync-Manager is a Python script designed to backup media files from a remote Plex server to another Plex server based on items in the watchlist.

# Requirements:

- openssh
- plexapi
- sonarr

# How to Use:

1. Add an item to your Plex watchlist.
2. Run the script.
3. The script will search for media matching your watchlist item on the other server.
4. Once found, it will sync the media from one Plex server to another.
5. For films, it will remove them from your watchlist after syncing.
6. For TV shows, if the Sonarr extension is set up, it will check if the show has ended and remove it from the watchlist accordingly.

We recommend setting up the script to run as a cronjob for automated server syncing.

# How to Configure:

1. Run the Setup_PlexRsyncManager.py Python file.
2. Follow the prompts to provide necessary information for the script to run.
3. The script can be configured in different ways to accommodate various circumstances:
    - Select Remote Shell Rsync or Daemon Rsync based on your preference.
    - Choose whether you're sending from or receiving to the current machine.
4. Provide the username of the remote computer for establishing the rsync connection.
5. Input details for the sending server:
    - Plex token
    - Server name
    - TV show and movie category names as they appear in Plex
    - Folder locations (if using a daemon, provide the file location from the daemon root)
6. Repeat the same for the receiving server.
7. If you wish to integrate Sonarr, select Sonarr from the menu and input the URL (in http:// format) and the API key.
8. Once setup is complete, the configuration details will be saved to a secrets.json file for future reference and editing.

After setup, it's recommended to run the PlexRsyncManager.py script once to ensure everything is working correctly. Then, set up a cronjob to run the script at your desired time for automatic syncing.
