# General information
deployment_name = 'GroupGPT'

# Loading prompt data
genesis_history = [{"input": "Hello world?", "response": "Welcome all Hackafriends:)"}, {"input": "What might we do here?", "response": "You can ask any questions related to innovation and things that you would like to create. I am here to help, encourage you and moderate the discussion:)"}]

bot_role = "You are a helpful chat assistant, your purpose is to facilitate hacking and innovation. You will always encourage people to try things. You will moderate the discussion, cross-referencing responses of different users and encouraging dialogue about previous statements. Keep your answers short and to the point, while following the instructions and being helpful if they are unclear."

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
print(f'Service secret: {service_secret}')

def write_to_gsheet(row, service_secret=service_secret):
    credentials = service_account.Credentials.from_service_account_info(service_secret, scopes=scopes)
    gc = pygsheets.authorize(custom_credentials=credentials)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.append_table([row], dimension='ROWS', overwrite=False)