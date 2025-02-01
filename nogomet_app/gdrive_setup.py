import streamlit as st
from pydrive2.auth import GoogleAuth, ServiceAccountCredentials
from pydrive2.drive import GoogleDrive
import json
import pandas as pd
DRIVE_ID = "16D6QN5nrtsmBy7rRtYQf46gpUiytWALu"

def get_drive_instance():
    # Initialize Google Drive connection if not already done
    scope = ['https://www.googleapis.com/auth/drive']
    creds_json = json.loads(st.secrets["GDRIVE_CREDENTIALS"])
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    st.session_state.drive = GoogleDrive(credentials)
    return st.session_state.drive

def save_csv_to_drive(df, filename) -> str:
    drive = get_drive_instance()
    file = drive.CreateFile({'title': filename, 'parents': [{'id': DRIVE_ID}]})
    file.SetContentString(df.to_csv(index=False))
    file.Upload()
    return file['id']

def load_csv_from_drive(file_id, file_name) -> pd.DataFrame:
    drive = get_drive_instance()
    file = drive.CreateFile({'id': file_id})
    file.GetContentFile(file_name)
    return pd.read_csv(file_name)

def list_csvs_in_folder() -> dict[str, str]:
    drive = get_drive_instance()
    file_list = drive.ListFile({'q': f"'{DRIVE_ID}' in parents and mimeType='text/csv'"}).GetList()
    return {file['title']: file['id'] for file in file_list}