import dummy

# General information
try: 
    deployment_name = os.environ.get('DEPLOYMENT_NAME')
except:
    deployment_name = 'DeploymentError'

# Loading prompt data
genesis_history = [{"role":"user","content":"Hello world?"}, {"role":"assistant","content": "It's time to rock! I am here to help and moderate the discussion:)"}]

with open('background_info.txt','r') as f:
    background_info = f.read()

# Gsheet manipulation details
import pygsheets, os, json
from google.oauth2 import service_account

spreadsheet_id = '1ox3ooXQJ5F8FmK0cmPhWfRMbkK8NgPWZjhY07trTktE'
scopes = ['https://www.googleapis.com/auth/spreadsheets']
sheet_name = deployment_name
try:
    service_secret = os.environ.get('GDRIVE_API_CREDENTIAL')
    service_secret = json.loads(service_secret)
except:
    service_secret = json.load(open('./data/service_secret.json','r'))
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