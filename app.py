"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai, dummy
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from utils import write_to_gsheet, deployment_name, genesis_history, background_info, read_gsheet

#from easylogging import Logger
#logger = Logger('GroupGPTv0.2.0')
# turned off to make use of basic Flask logger

app = Flask(__name__, static_folder=".", static_url_path='')
logger = app.logger
openai.api_key = os.environ.get('openaikey')


history = []

def history_from_gsheet():
    global history
    table = read_gsheet()
    logger.debug(table)
    for row in table:
        try:
            history.append({'role':row['role'],'content':row['content']})#{'input': row['user'], 'response': row['assistant']})
        except Exception as e:
            logger.error(f'Exception in loading history {e} for row {row}')
        #history = genesis_history
    logger.debug(history)
    logger.info(f'History has been prepared!')
    return history

history = history_from_gsheet()

system_instruction = '''You are a helpful assistant that replies shortly and smartly.'''

now = lambda: datetime.now().strftime("%Y%m%d_%H%M%S")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/status')
def status():
    global history
    global system_instruction
    return jsonify({"system_instruction": system_instruction, "history": history}), 200

@app.route('/refresh')
def refresh():
    global history
    history = []
    history = history_from_gsheet()
    return jsonify({"history": history}), 200

@app.route('/get_history', methods=['GET'])
def get_history():
    global history
    return jsonify({"history": history}), 200

@app.route('/store_text', methods=['POST'])
def complete():
    global history
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    max_history_length = min(len(history), 9)
    #print(f"Received a prompt from user: {text}")
    history.append({"role":"user", "content":text})

    # Send text to OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages= [{"role": "system", "content": system_instruction}]+
            history[-10:]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    msg = {"role":"assistant", "content": openai_response}
    history.append(msg)
    print(f"Preparing to write messages to gsheet. User: {history[-2]} and System: {history[-1]}")
    try:
        print('Writing user...')
        print(history[-1])
        write_to_gsheet(row = [deployment_name, now(), json.dumps(history[-2]), history[-2]['role'], history[-2]['content']])
        print('Wrote user!')
        print('Writing assistant...')
        write_to_gsheet(row = [deployment_name, now(), json.dumps(history[-1]), history[-1]['role'], history[-1]['content']])
        print('Wrote assistant!')
    except Exception as e:
        print(f'Sth wrong with writing to gsheet {e}')
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
