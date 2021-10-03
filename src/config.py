from os import getenv

import gspread
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials

load_dotenv()

# gets the spreadsheet's keys
SPREADSHEET_KEY = getenv("SPREADSHEET_KEY")

# use creds to create a client to interact with the google drive api
creds = ServiceAccountCredentials.from_json_keyfile_name(
    "credentials.json",
    [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive",
    ],
)
client = gspread.authorize(creds)

# gets the spreadsheet's info
ss = client.open_by_key(SPREADSHEET_KEY)
sheets = ss.worksheets()
