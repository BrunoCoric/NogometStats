from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload
import pandas as pd
import io
import streamlit as st
import json

FOLDER_ID = "16D6QN5nrtsmBy7rRtYQf46gpUiytWALu"

class GoogleDriveService:
    def __init__(self):
        # Load credentials from Streamlit secrets
        credentials_dict = json.loads(st.secrets["GDRIVE_CREDENTIALS"])
        credentials = service_account.Credentials.from_service_account_info(
            credentials_dict,
            scopes=['https://www.googleapis.com/auth/drive.file',
                   'https://www.googleapis.com/auth/drive']
        )
        self.service = build('drive', 'v3', credentials=credentials)


def list_csvs_in_folder():
    """
    List all CSV files in the specified Google Drive folder.
    Returns a dictionary with filename as key and file ID as value.
    """
    try:
        drive_service = GoogleDriveService().service

        # Query for CSV files in the specified folder
        query = f"'{FOLDER_ID}' in parents and mimeType='text/csv'"
        results = drive_service.files().list(
            q=query,
            fields="files(id, name)"
        ).execute()

        # Create dictionary of filename: file_id
        files_dict = {
            file['name']: file['id']
            for file in results.get('files', []) if file['name'].endswith('.csv')
        }

        return files_dict

    except Exception as e:
        raise Exception(f"Error listing CSV files: {str(e)}")

def load_file_from_drive(file_id):
    try:
        drive_service = GoogleDriveService().service

        # Get the file
        request = drive_service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        # Reset the file handle position and read as DataFrame
        file_handle.seek(0)
        return file_handle

    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")

def load_csv_from_drive(file_id):
    """
    Download and read a CSV file from Google Drive.
    Returns a pandas DataFrame.
    """
    try:
        drive_service = GoogleDriveService().service

        # Get the file
        request = drive_service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)

        done = False
        while not done:
            _, done = downloader.next_chunk()

        # Reset the file handle position and read as DataFrame
        file_handle.seek(0)
        return pd.read_csv(file_handle)

    except Exception as e:
        raise Exception(f"Error loading CSV file: {str(e)}")



def save_csv_to_drive(df, filename):
    """
    Save a pandas DataFrame as a CSV file to Google Drive.
    Returns the file ID of the uploaded file.
    """
    try:
        drive_service = GoogleDriveService().service

        # Convert DataFrame to CSV in memory
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        # Prepare the file metadata and media
        file_metadata = {
            'name': filename,
            'parents': [FOLDER_ID],
            'mimeType': 'text/csv'
        }

        # Convert to bytes for upload
        media = MediaIoBaseUpload(
            io.BytesIO(csv_buffer.getvalue().encode()),
            mimetype='text/csv',
            resumable=True
        )

        # Upload the file
        file = drive_service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()

        return file.get('id')

    except Exception as e:
        raise Exception(f"Error saving CSV file: {str(e)}")