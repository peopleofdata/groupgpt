"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai, dummy
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from utils import write_to_gsheet, deployment_name, genesis_history, background_info

app = Flask(__name__, static_folder=".", static_url_path='')
openai.api_key = os.environ.get('openaikey')
history = genesis_history

bot_role = "You are a helpful chat assistant, your purpose is to facilitate hacking and innovation. You will always encourage people to try things. You will moderate the discussion, cross-referencing responses of different users and encouraging dialogue about previous statements. Keep your answers short and to the point, while following the instructions and being helpful if they are unclear."

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
    global history
    print(history)
    return jsonify({"history": history}), 200

@app.route('/store_text', methods=['POST'])
def complete():
    global history
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    max_history_length = min(len(history), 9)
    print(history, text)
    # Send text to OpenAI API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": ""},#instruction(background_info, str(history[-max_history_length:]))},
                {"role": "user", "content": text},
            ]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    history.append({'input': text, 'response':openai_response})
    print(openai_response)
    #write_to_gsheet(row = [deployment_name, now(), text, openai_response])
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
