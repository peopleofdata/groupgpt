# General information
deployment_name = 'HackGPT'

# Loading prompt data
genesis_history = [{"input": "Hello world?", "response": "Welcome all Hackafriends:)"}, {"input": "What might we do here?", "response": "You can ask any questions related to innovation and things that you would like to create. I am here to help, encourage you and moderate the discussion:)"}]

bot_role = "You are a helpful chat assistant, your purpose is to facilitate hacking and innovation. You will always encourage people to try things. You will moderate the discussion, cross-referencing responses of different users and encouraging dialogue about previous statements. Keep your answers short and to the point, while following the instructions and being helpful if they are unclear."

with open('background_info.txt','r') as f:
    background_info = f.read()

# Gsheet manipulation details
import pygsheets

spreadsheet_id = '1ox3ooXQJ5F8FmK0cmPhWfRMbkK8NgPWZjhY07trTktE'
sheet_name = deployment_name
service_file_path = "./gsheet-secret.json"

def write_to_gsheet(row):
    gc = pygsheets.authorize(service_file=service_file_path)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.append_table([row], dimension='ROWS', overwrite=False)
