from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive

# UNfinished attempt to connect google drive

def connect_google_drive_api():
    # use Gdrive API to access Google Drive
    from pydrive2.auth import GoogleAuth
    from pydrive2.drive import GoogleDrive

    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()  # client_secrets.json need to be in the same directory as the script

    drive = GoogleDrive(gauth)

    return drive

drive = connect_google_drive_api()
file_list = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file1 in file_list:

    print('title: %s, id: %s, text: %s' % (file1['title'], file1['id'], file1['mimeType']))