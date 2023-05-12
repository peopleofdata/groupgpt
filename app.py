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
    print(f'Exception {e}')
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
    for e in history:
        print(e)
        try:
            if e["role"]=="user":
                temp_history.append(e)
        except:
            pass
        try:
            if "'should_respond':'Yes'" in e['content']:
                text = json.loads(e['content'])
                temp_history.append({"role":"assistant","content":text['content']})
        except:
            pass
    return jsonify({"history": temp_history}), 200

@app.route('/store_text', methods=['POST'])
def complete():
    global history
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    max_history_length = min(len(history), 9)
    print(history, text)
    history.append({"role":"user", "content":text})
    try:
        print('Writing...')
        write_to_gsheet(row = [deployment_name, now(), json.dumps({"role":"user", "content":text})])
        print('Wrote!')
    except Exception as e:
        print(f'Sth wrong with writing to gsheet {e}')
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
    next_chat_line = {"role":"assistant", "content": openai_response}
    history.append(next_chat_line)
    try:
        print('Writing...')
        write_to_gsheet(row = [deployment_name, now(), json.dumps(next_chat_line)])
        print('Wrote!')
    except Exception as e:
        print(f'Sth wrong with writing to gsheet {e}')
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
