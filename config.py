from dotenv import load_dotenv
from os import getenv

import gspread
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# Gets the spreadsheet's keys
SPREADSHEET_KEY = getenv('SPREADSHEET_KEY')

# Use creds to create a client to interact with the Google Drive API
scope = [
    "https://spreadsheets.google.com/feeds",
    'https://www.googleapis.com/auth/spreadsheets',
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

# Gets the spreadsheet's info 
ss = client.open_by_key(SPREADSHEET_KEY)
sheets = ss.worksheets()