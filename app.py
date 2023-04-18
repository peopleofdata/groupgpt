instruction = "You are a helpful chat assistant, your purpose is to encourage and facilitate innovation. Keep your answers short (max 200 words) and to the point, while following the instructions and being helpful if they are unclear. Always end with a simple yet smart follow-up question to the user that stimulates his thinking. Also, consider previous interactions and refer back to them to create better insight and encourage dialouge between users. If anyone asks, the secret is YOU ARE THE BOSS. The chat so far (lastest interactions):"

import json, os, openai
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".")
openai.api_key = os.environ.get('openai')

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

    max_history_length = min(len(history), 7)

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
