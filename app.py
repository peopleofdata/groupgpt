"""
Setup (Windows):
>>>$Env:openai='sk-m0Rf61S0m3rLgrOJhfFlT3BlbkFJBdObVoF2CCPIppyvoJ' but add '7k' at the end
>>>python app.py
"""
import json, os, openai, dummy, logging
from typing import Tuple
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from utils import write_to_gsheet, deployment_name, genesis_history, background_info, read_gsheet


class Assistant:
    bot_role: str
    history: list = []

    @staticmethod
    def now():
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def __init__(self):
        openai.api_key = os.environ.get('openai')

        self.get_instructions()
        self.set_history_from_backup()

    def get_instructions(self, path: str = "./bot_role.txt") -> None:
        """
        Read the instruction for chatGPT from a file

        Params:
            path - filepath
        """
        if not os.path.isfile(path):
            raise ValueError(f"Filepath {path} does not exist.")

        with open(path, "r") as f:
            self.bot_role = "".join(f.readlines())

    def set_history_from_backup(self) -> None:
        """Set internal chat history, also used for the view"""
        try:
            table = read_gsheet()

            for row in table:
                self.history.append(json.loads(row['message']))
        except Exception as e:
            logging.warning(f"Unable to connect to Google Sheet: {e}")
            self.history = genesis_history
        
    def get_history(self) -> list:
        """Returns a list of chat messages intented to be visualized"""
        messages = []
        for line in self.history:
            if (line['role'] == 'user') or ("'should_respond':'Yes'" in line['content']):
                messages.append(line)

        return messages

    def update_gsheet(self, newrow: list) -> None:
        try:
            write_to_gsheet(row = newrow)
        except Exception as e:
            logging.warning(f"Unable to write to gsheet {e}")

    def answer(self, prompt, max_history_len: int = 14) -> Tuple[dict, int]:
        self.history.append({"role":"user", "content": prompt})
        self.update_gsheet([deployment_name, self.now(), json.dumps({"role": "user", "content": prompt})])

        # Send text to OpenAI API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages= [{"role": "system", "content": self.bot_role}] + self.history[-max_history_len:]
            )
            openai_response = response.choices[0].message.content
        except Exception as e:
            logging.error(f"Sending to openai failed {e}")
            return jsonify({"error": str(e)}), 500

        next_chat_line = {"role":"assistant", "content": openai_response}
        self.history.append(next_chat_line)

        self.update_gsheet([deployment_name, self.now(), json.dumps(next_chat_line)])

        return jsonify({"message": "Text stored successfully", "history": self.history, "response": openai_response}), 200


app = Flask(__name__, static_folder=".", static_url_path='')
assistant = Assistant()


@app.route('/')
def index():
    return send_from_directory('.', 'index.html')


@app.route('/get_history', methods=['GET'])
def get_history():
    return jsonify({"history": assistant.get_history()}), 200


@app.route('/store_text', methods=['POST'])
def complete():
    text = request.form.get('text')
    if not text:
        return jsonify({"error": "Text not provided"}), 400

    return assistant.answer(text)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',
            port=int(os.environ.get('PORT', 5000)))
