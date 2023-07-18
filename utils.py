# General information
deployment_name = 'GroupGPTv0.2.0'

# Loading prompt data
genesis_history = [{"role": "user", "content": "Welcome all Hackafriends:)"}, \
                   {"role": "assistant", "content": "You can ask any questions related to innovation and things that you would like to create. I am here to help, encourage you and moderate the discussion:)"}]

# Gsheet manipulation details
import pygsheets, os, json
from google.oauth2 import service_account


class gSheetHandler:
    spreadsheet_id = '1ox3ooXQJ5F8FmK0cmPhWfRMbkK8NgPWZjhY07trTktE'

    def __init__(self):
        scopes = ['https://www.googleapis.com/auth/spreadsheets']
        service_secret = os.environ.get('GDRIVE_API_CREDENTIAL')
        if not service_secret:
            with open("./gsheet-secret.json", "rb") as f:
                service_secret = json.load(f)
        #print(f'Service secret: {service_secret}')

        credentials = service_account.Credentials.from_service_account_info(service_secret, scopes=scopes)
        gc = pygsheets.authorize(custom_credentials=credentials)
        self.sh = gc.open_by_key(self.spreadsheet_id)
        try:
            self.sh.add_worksheet(deployment_name)
        except:
            pass

    def read_gsheet(self, sheet_name):
        shread= self.sh.worksheet_by_title(sheet_name)
        table = shread.get_all_records()
        return table

    def write_to_gsheet(self, sheet_name, row):
        wks_write = self.sh.worksheet_by_title(sheet_name)
        wks_write.append_table([row], dimension='ROWS', overwrite=False)