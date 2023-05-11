# General information
deployment_name = 'GroupGPT'

# Loading prompt data
genesis_history = [{"input": "Hello world?", "response": "Welcome all Hackafriends:)"}, {"input": "What might we do here?", "response": "You can ask any questions related to innovation and things that you would like to create. I am here to help, encourage you and moderate the discussion:)"}]

with open('background_info.txt','r') as f:
    background_info = f.read()

# Gsheet manipulation details
import pygsheets, os, json
from google.oauth2 import service_account

spreadsheet_id = '1ox3ooXQJ5F8FmK0cmPhWfRMbkK8NgPWZjhY07trTktE'
scopes = ['https://www.googleapis.com/auth/spreadsheets']
sheet_name = deployment_name
service_secret = os.environ.get('GDRIVE_API_CREDENTIAL')
service_secret = json.loads(service_secret)
#print(f'Service secret: {service_secret}')
def open_gsheet(service_secret=service_secret):
    credentials = service_account.Credentials.from_service_account_info(service_secret, scopes=scopes)
    gc = pygsheets.authorize(custom_credentials=credentials)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    
    return sh

def read_gsheet():
    sh = open_gsheet()
    shread= sh.worksheet_by_title(sheet_name)
    table = shread.get_all_records()
    return table

def write_to_gsheet(row):
    sh = open_gsheet()
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.append_table([row], dimension='ROWS', overwrite=False)