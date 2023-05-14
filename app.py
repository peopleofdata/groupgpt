"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai, dummy
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from utils import write_to_gsheet, deployment_name, genesis_history, background_info, read_gsheet

app = Flask(__name__, static_folder=".", static_url_path='')
openai.api_key = os.environ.get('openaikey')

try:
    history = []
    table = read_gsheet()
    print(table)
    for row in table:
        history.append(json.loads(row['message']))#{'input': row['user'], 'response': row['assistant']})
except Exception as e:
    print(f'Exception in loading history {e}')
    history = genesis_history
print(history)

bot_role = """You will reply structured as JSON and only as JSON. \
You shall never provide a reply that is not a JSON. I will feed you a conversation and you will decide\
whether it is the right time to say something, or not. If the user instructs you to stop talking, you will not\
respond and set 'should_respond' to 'No'. If you are asked by your name 'Nat' you will always reply. You will 
provide your response in JSON format and only in the JSON format, with no 
text outside JSON. A JSON output example looks like this:
{'should_respond':'Yes', 'response':'Hello world!'}
The conversation so far:"""

def instruction(background_info):
    return f"{bot_role}"

now = lambda: datetime.now().strftime("%Y%m%d_%H%M%S")

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/get_history', methods=['GET'])
def get_history():
    global history
    temp_history = []
    print(f"Fetching history from current state: {history}")
    for e in history:
        try:
            if e["role"]=="user":
                temp_history.append(e)
            elif e['role']=='assistant':
                temp_history.append(e)
        except:
            print(f'/get_history error on fetching rows')
    print(f"Produced temp_history: {temp_history}")
    return jsonify({"history": temp_history}), 200

@app.route('/store_text', methods=['POST'])
def complete():
    global history
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    max_history_length = min(len(history), 9)
    print(f"Received a prompt from user: {text}")
    history.append({"role":"user", "content":text})

    # Send text to OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages= [{"role": "system", "content": instruction(background_info)}]+
            history[-14:]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    msg = {"role":"assistant", "content": openai_response}
    history.append(msg)
    try:
        print('Writing user...')
        print(history[-1])
        write_to_gsheet(row = [deployment_name, now(), json.dumps(history[-1]), history[-1]['role'], history[-1]['content']])
        print('Wrote user!')
        print('Writing assistant...')
        write_to_gsheet(row = [deployment_name, now(), json.dumps(msg), msg['role'], msg['content']])
        print('Wrote assistant!')
    except Exception as e:
        print(f'Sth wrong with writing to gsheet {e}')
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
