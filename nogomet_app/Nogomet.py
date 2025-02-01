import streamlit as st
from nogomet_app.gdrive_setup import save_csv_to_drive, load_csv_from_drive, list_csvs_in_folder

st.title("Nogometni termin statistika")
