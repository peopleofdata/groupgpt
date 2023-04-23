"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from utils import write_to_gsheet, deployment_name, genesis_history, bot_role, background_info

app = Flask(__name__, static_folder=".", static_url_path='')
openai.api_key = os.environ.get('openai')

def instruction(background_info, top_history):
    return f"{bot_role}\nSome background info for you: {background_info}\nThe chat so far (last interactions):{top_history}"

# this statements creates a history if there is no history file stored
if not os.path.exists('history.json'):
    with open('history.json','w') as f:
        f.write(json.dumps(genesis_history))

now = lambda: datetime.now().strftime("%Y%m%d_%H%M%S")

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
                {"role": "system", "content": instruction(background_info, str(history[-max_history_length:]))},
                {"role": "user", "content": text},
            ]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    write_to_gsheet(row = [deployment_name, now(), text, openai_response])

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
