from pydrive2.auth import GoogleAuth
from pydrive2.drive import GoogleDrive
import streamlit as st
import json
import os
import pandas as pd

DRIVE_ID = "16D6QN5nrtsmBy7rRtYQf46gpUiytWALu"



def get_drive_instance():
    if 'drive' not in st.session_state:
        # Create a temporary credentials file
        creds_json = json.loads(st.secrets["GDRIVE_CREDENTIALS"])

        with open("temp_creds.json", "w") as f:
            json.dump(creds_json, f)


        # Initialize GoogleAuth
        gauth = GoogleAuth()
        # Disable automatic webserver authentication
        gauth.settings['get_refresh_token'] = False

        # Set up service account authentication
        gauth.ServiceAuth()

        # Create and store GoogleDrive instance
        st.session_state.drive = GoogleDrive(gauth)

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