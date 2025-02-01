import streamlit as st
from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import json
import pandas as pd
import os

creds_json = json.loads(st.secrets["GDRIVE_CREDENTIALS"])
print(creds_json)
with open("temp_gdrive_creds.json", "w") as f:
    json.dump(creds_json, f)

gauth = GoogleAuth()
gauth.LoadCredentialsFile("temp_gdrive_creds.json")
if gauth.credentials is None:
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    gauth.Refresh()
else:
    gauth.Authorize()

drive = GoogleDrive(gauth)
os.remove("temp_gdrive_creds.json")

DRIVE_ID = "16D6QN5nrtsmBy7rRtYQf46gpUiytWALu"

def save_csv_to_drive(df, filename) -> str:
    file = drive.CreateFile({'title': filename, 'parents': [{'id': DRIVE_ID}]})
    file.SetContentString(df.to_csv(index=False))
    file.Upload()
    return file['id']  # Returns the file ID

def load_csv_from_drive(file_id, file_name) -> pd.DataFrame:
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(file_name)
    return pd.read_csv(file_name)

def list_csvs_in_folder() -> dict[str, str]:
    file_list = drive.ListFile({'q': f"'{DRIVE_ID}' in parents and mimeType='text/csv'"}).GetList()
    return {file['title']: file['id'] for file in file_list}