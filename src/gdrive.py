from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import io
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


import json

from cryptography.fernet import Fernet

from dotenv import dotenv_values
config = dotenv_values(".env")
gdrive_info = dict(
    project_id = config.get("GDRIVE_project_id"),
    private_key_id = config.get("GDRIVE_private_key_id"),
    private_key = config.get("GDRIVE_private_key"),

    client_email = config.get("GDRIVE_client_email"),
    client_id = config.get("GDRIVE_client_id"),
    auth_uri = config.get("GDRIVE_auth_uri"),

    token_uri = config.get("GDRIVE_token_uri"),
    auth_provider_x509_cert_url = config.get("GDRIVE_auth_provider_x509_cert_url"),
    client_x509_cert_url = config.get("GDRIVE_client_x509_cert_url"),
    universe_domain = config.get("GDRIVE_universe_domain")
    )
gdrive_file_id = config.get("GDRIVE_file_id")
gdrive_key = config.get("GDRIVE_key")



def load_test() -> dict:

    credentials = Credentials.from_service_account_info(gdrive_info, scopes=['https://www.googleapis.com/auth/drive'])

    drive_service = build('drive', 'v3', credentials=credentials)
    
    # key = b'0Xba4xpw8hCqwXI5dqVnNC4N2DUyIXLkVtaEYcOX8so='
    key = gdrive_key.encode()
    cipher_suite = Fernet(key)
    file_id = gdrive_file_id

    request = drive_service.files().get_media(fileId=file_id)
    fh = io.FileIO('downloaded_test_dict.json', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    print('downloaded')
    with open('downloaded_test_dict.json', 'r') as f:
        downloaded_dict = json.load(f)
    # print(downloaded_dict)

    plain_test_dict = {cipher_suite.decrypt(k.encode('utf-8')).decode(): {k1: cipher_suite.decrypt(v1.encode('utf-8')).decode() for k1, v1 in v.items()} for k, v in downloaded_dict.items()}
    # print(plain_test_dict)
    # print()

    plain_test_dict_prep = {k: {k1: v1 if k1 != 'team_name' else v1.split("*&%") for k1, v1 in v.items()} for k, v in plain_test_dict.items()}
    # print(plain_test_dict_prep)
    return plain_test_dict_prep
