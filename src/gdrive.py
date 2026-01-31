from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

import io
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.http import MediaFileUpload


import json

from cryptography.fernet import Fernet

from src.consts import loto_profiles

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
        downloaded_dict = json.loads(json.load(f))
    # print(downloaded_dict)

    plain_test_dict = {cipher_suite.decrypt(k.encode('utf-8')).decode(): {k1: cipher_suite.decrypt(v1.encode('utf-8')).decode() for k1, v1 in v.items()} for k, v in downloaded_dict.items()}
    # Ключ: "user_id" (старый формат) → считаем город moscow; "user_id:city" → профиль на город
    def _norm_key(k):
        if ":" in k:
            return k
        return f"{k}:moscow"

    plain_test_dict_prep = {_norm_key(k): {k1: v1 if k1 != 'team_name' else v1.split("*&%") for k1, v1 in v.items()} for k, v in plain_test_dict.items()}
    return plain_test_dict_prep


def change_profile_on_gdrive(user_id: str, city: str, profile: dict) -> None:
    """Сохраняет профиль на диск: ключ в файле — user_id:city (у каждого пользователя свой профиль на город)."""
    credentials = Credentials.from_service_account_info(gdrive_info, scopes=['https://www.googleapis.com/auth/drive'])

    drive_service = build('drive', 'v3', credentials=credentials)
    
    key = gdrive_key.encode()
    cipher_suite = Fernet(key)
    file_id = gdrive_file_id

    add_dict_prep = {k1: v1 if not isinstance(v1, list) else "*&%".join(v1) for k1, v1 in profile.items()}
    cipher_add_dict = {k1: cipher_suite.encrypt(v1.encode()).decode('utf-8') for k1, v1 in add_dict_prep.items()}

    composite_key = f"{user_id}:{city}"
    cipher_user_id = cipher_suite.encrypt(composite_key.encode()).decode('utf-8')

    print(f"FILE_ID:\t{file_id}")
    request = drive_service.files().get_media(fileId=file_id)

    fh = io.FileIO('tmp.json', 'wb')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()

    with open('tmp.json', 'r') as f:
        existing_dict = json.loads(json.load(f))

    # downloaded_file = request.execute()

    # Step 2: Deserialize the file
    # existing_dict = json.loads(downloaded_file.decode('utf-8'))

    # Step 3: Modify the dictionary
    existing_dict[cipher_user_id] = cipher_add_dict

    # Step 4: Serialize the dictionary
    updated_content = json.dumps(existing_dict)

    with open('tmp.json', 'w') as f:
        json.dump(updated_content, f)

    media = MediaFileUpload('tmp.json', mimetype='application/json')

    # Update the file on Google Drive
    request = drive_service.files().update(
        fileId=file_id,
        media_body=media
    )

    request.execute()

    plain_test_dict = {cipher_suite.decrypt(k.encode('utf-8')).decode(): {k1: cipher_suite.decrypt(v1.encode('utf-8')).decode() for k1, v1 in v.items()} for k, v in existing_dict.items()}
    # Ключи в файле: "user_id:city" или старый формат "user_id" → нормализуем для кэша
    def _norm_key(k):
        return k if ":" in k else f"{k}:moscow"
    plain_test_dict_prep = {_norm_key(k): {k1: v1 if k1 != 'team_name' else v1.split("*&%") for k1, v1 in v.items()} for k, v in plain_test_dict.items()}
    loto_profiles.update(plain_test_dict_prep)


