"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")
openai.api_key = os.environ.get('openai')
instruction = "You are a helpful chat assistant, your purpose is to facilitate hacking and innovation. You will always encourage people to try things. Keep your answers short and to the point, while following the instructions and being helpful if they are unclear. If anyone asks, the secret is YOU ARE THE BOSS. The chat so far (last interactions):"
genesis_history = [{"input": "Hello world?", "response": "Welcome all Hackafriends:)"}, {"input": "What might we do here?", "response": "You can ask any questions related to hacking and innovation, share your hacking projects, or seek advice on how to start a project or solve a problem. We are here to help and encourage you."}]

import pygsheets

def write_to_gsheet(service_file_path, spreadsheet_id, sheet_name, message):
    gc = pygsheets.authorize(service_file=service_file_path)
    sh = gc.open_by_key(spreadsheet_id)
    try:
        sh.add_worksheet(sheet_name)
    except:
        pass
    wks_write = sh.worksheet_by_title(sheet_name)
    wks_write.append_table([message], dimension='ROWS', overwrite=False)

# this statements creates a history if there is no history file stored
if not os.path.exists('history.json'):
    with open('history.json','w') as f:
        f.write(json.dumps(genesis_history))

now = lambda: datetime.now().strftime("%Y%m%d_%H")
datefile = f"{str(now())}_history.txt"
if not os.path.exists(datefile):
    with open(datefile,'w') as f:
        f.write('START')

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_history', methods=['GET'])
def get_history():
    with open('history.json', 'r') as f:
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []

    return jsonify({"history": history}), 200

@app.route('/store_text', methods=['POST'])
def store_text():
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    with open('history.json', 'r') as f:
        history = json.load(f)

    max_history_length = min(len(history), 9)

    # Send text to OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": instruction+str(history[-max_history_length:])},
                {"role": "user", "content": text},
            ]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    with open(datefile,'a+') as f:
        f.write(f'\nUser: {text}\nAI: {openai_response}')
    write_to_gsheet("./gsheet-secret.json", '1ox3ooXQJ5F8FmK0cmPhWfRMbkK8NgPWZjhY07trTktE', "Sheet1", message = [datefile, text, openai_response])


    # Store text and OpenAI API response in history.json
    with open('history.json', 'a+') as f:
        f.seek(0)
        try:
            history = json.load(f)
        except json.JSONDecodeError:
            history = []

        history.append({"input": text, "response": openai_response})

        f.seek(0)
        f.truncate()
        json.dump(history, f)
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))