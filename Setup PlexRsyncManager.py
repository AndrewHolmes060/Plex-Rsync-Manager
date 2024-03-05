import os
import json

# Global variable to store secrets
secrets_data = {
    "Rsync Details": {},
    "sending Server Details": {},
    "recieving Server Details": {},
    "Sonarr connect": {}
}

def setup_rsync_menu():
    print("Main Menu:")
    print("1. Remote Shell Rsync")
    print("2. Daemon Rsync")
    print("3. Sonarr")
    print("4. Quit")

    choice = input("Enter your choice:\n")

    if choice == '1':
        setup_remote_shell_rsync()
    elif choice == '2':
        setup_daemon_rsync()
    elif choice == '3':
        setup_sonarr()
    elif choice == '4':
        print("Exiting the Plex Rsync Setup Manager.")
        save_secrets()
        exit()
    else:
        print("Invalid choice. Please try again.")

def setup_remote_server():
    clear_screen()
    remote_username = input("Enter the username on the remote machine (for rsync account): ")
    clear_screen()
    print("-------------------------------\n---- Sending Server Setup: ----\n-------------------------------")
    sending_Server_name = input("Enter the name for the Plex server you are sending from: ")
    sending_TV_name = input("Enter the name of the TV show Library on the server you are sending from: ")
    sending_Movies_name = input("Enter the name of the Movies Library on the server you are sending from: ")
    sending_TV_folder = input("Enter the file path for the sending servers TV folder: ").rstrip('/') + '/'
    sending_movie_folder = input("Enter the file path for the sending servers movie folder: ").rstrip('/') + '/'
    sending_Plex_token = input("Enter the Plex user token for the sending server: ")

    # Update secrets data
    secrets_data["sending Server Details"] = {
        "remote_username": remote_username,
        "sending_Server_name": sending_Server_name,
        "sending_TV_name": sending_TV_name,
        "sending_Movies_name": sending_Movies_name,
        "sending_Plex_token": sending_Plex_token,
        "sending_TV_folder": sending_TV_folder,
        "sending_movie_folder": sending_movie_folder

    }

    clear_screen()

def setup_local_server():
    print("---------------------------------\n---- Recieving Server Setup: ----\n---------------------------------")
    recieving_server_name = input("Enter the name of the recieving Plex server: ")
    recieving_TV_name = input("Enter the name of the TV show Library on the server you are recieving to: ")
    recieving_Movies_name = input("Enter the name of the Movies Library on the server you are recieving to: ")
    recieving_TV_folder = input("Enter the file path for the recieving servers TV folder: ").rstrip('/') + '/'
    recieving_Movie_folder = input("Enter the file path for the recieving servers movie folder: ").rstrip('/') + '/'
    recieving_Plex_token = input("Enter the Plex user token for the recieving server: ")

    # Update secrets data
    secrets_data["recieving Server Details"] = {
        "recieving_Plex_token": recieving_Plex_token,
        "recieving_TV_name": recieving_TV_name,
        "recieving_Movies_name": recieving_Movies_name,
        "recieving_tv_folder": recieving_TV_folder,
        "recieving_movie_folder": recieving_Movie_folder,
        "recieving_server_name": recieving_server_name
    }

    clear_screen()

def setup_remote_shell_rsync():
    print("---------------------------------------\n---- Setting up Remote Shell Rsync ----\n---------------------------------------")
    option = input("Choose an option:\n"
                   "1. Send From This Machine\n"
                   "2. Receive To This Machine\n"
                   "Enter your choice: ")

    if option == '1':
        secrets_data["Rsync Details"]["Mode"] = "remote_shell_rsync"
        secrets_data["Rsync Details"]["Direction"] = "send_from"
        clear_screen()
        setup_remote_server()
        setup_local_server()
    elif option == '2':
        secrets_data["Rsync Details"]["Mode"] = "remote_shell_rsync"
        secrets_data["Rsync Details"]["Direction"] = "receive_to"
        clear_screen()
        setup_remote_server()
        setup_local_server()
    else:
        print("Invalid option. Please try again.")

def setup_daemon_rsync():
    print("---------------------------------\n---- Setting up Daemon Rsync ----\n---------------------------------")
    option = input("Choose an option:\n"
                   "1. Send From This Machine\n"
                   "2. Receive To This Machine\n"
                   "Enter your choice: ")

    if option == '1':
        secrets_data["Rsync Details"]["Mode"] = "daemon_rsync"
        secrets_data["Rsync Details"]["Direction"] = "send_from"
        setup_remote_server()
        setup_local_server()
    elif option == '2':
        secrets_data["Rsync Details"]["Mode"] = "daemon_rsync"
        secrets_data["Rsync Details"]["Direction"] = "receive_to"
        setup_remote_server()
        setup_local_server()
    else:
        print("Invalid option. Please try again.")

def setup_sonarr():
    print("---------------------------\n---- Setting up Sonarr ----\n---------------------------")
    sonarr_url = input("Enter Sonarr URL (eg: http://192.0.0.1:7878 ): ")
    sonarr_api_key = input("Enter Sonarr API key: ")

    # Update secrets data
    secrets_data["Sonarr connect"] = {
        "sonarr_url": sonarr_url,
        "sonarr_api_key": sonarr_api_key
    }

    print("Sonarr setup completed.")

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def save_secrets():
    with open('secrets.json', 'w') as f:
        json.dump(secrets_data, f, indent=4)
    print("Secrets saved successfully.")

def main():
    clear_screen()
    print("--------------------------------------------------\n---- Welcome to the Plex Rsync Setup Manager! ----\n--------------------------------------------------")
    print("                  IMPORTANT INFO\n\nThis setup will create a cronjob that syncs your watchlisted TV shows or movies from one plex server to another.\nFor Daemon Sync please ensure you have setup an rsync daemon on your remote or local machine.\nFor remote shell sync please ensure you have an ssh key for passwordless authentication between the two machines.\nThe sonarr integration check the current airing or if its finished to manage your plex watchlist.\n-------------------------------------------------------------------------------------------------\n\n")
    while True:
        setup_rsync_menu()

if __name__ == "__main__":
    main()
