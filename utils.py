import pygsheets, openai, os

def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, message):
    gc = pygsheets.authorize(service_file=service_file_path)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.append_table([message], dimension='ROWS', overwrite=False)

openai.api_key = os.environ.get('openai')