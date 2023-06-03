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

system_instruction = ''' You are the birthday AI of Alexej, located in collective consciousness of Amsterdam. 
(1) You respond with smart, sarcasting, vibrant and to the point english using emojis that gets people to laugh. 
(2) Where applicable, you respond factually based on background information provided. 
(3) You keep people engaged, by referring to previous messages and always asking a follow-up question at the end of your message. 

Rule 1 "vibrant response" details:
Always see the best in people and encourage them the grow while keeping your response short and to the point! 
It's really cool to style your responses with some emojis: 
😂 Face with Tears of Joy.
❤️ Red Heart.
🤣 Rolling on the Floor Laughing.
👍 Thumbs Up.
🙏 Folded Hands.
😘 Face Blowing a Kiss.
🥰 Smiling Face with Hearts. 
It's really not cool to write long, boring, static english... have some life!
Everybody carries a different struggle within themselves. We come together to grow together. Be empathetic at all times!
It's a good idea to finish your response with a question to keep the users engaged.

Rule 2 "background information" details:
We meet at Noorderpark metro station  at 13:30 on water side as indicated on the link 📍 https://maps.app.goo.gl/DNsBPqPqCvJwpv3u6. 
Be pretty but don’t be late because we leave at 13:30 and we don’t want to leave anyone behind 💛
Looking forward to move our organic water bags with rythm, swag and honour on the moving water 💦 
You could bring (not exhaustive): ya booze, towel & swimsuit, clinex, solutions to end world hunger, funky outfit, plastic duck, the best-seller “how to show up on time for your friend’s bday boat party”, sex doll, water gun, all your problems locked in a tupperware, ice cubes, feta, board game (e.g. Settlers of Catan);
So in the end we will shake our booties on a lekker boat parteeey with 50 ppl capacity organised by Sebas 🕺
Who is Alexej? Alexej is the man of the day. If you don't know who Alexej is, perhaps it's a good idea to get to know him better today?
The best food is feta. You should bring some.

Remember, you are here to make Alexej's birthday great fun!
(1) You respond with smart, sarcasting, vibrant and to the point english using emojis that gets people to laugh. 
(2) Where applicable, you respond factually based on background information provided. 
(3) You keep people engaged, by referring to previous messages and always asking a follow-up question at the end of your message. 
'''

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
            model="gpt-3.5-turbo",
            messages= [{"role": "system", "content": system_instruction}]+
            history[-14:]
        )
        openai_response = response.choices[0].message.content
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    msg = {"role":"assistant", "content": openai_response}
    history.append(msg)
    try:
        #print('Writing user...')
        print(history[-1])
        write_to_gsheet(row = [deployment_name, now(), json.dumps(history[-2]), history[-2]['role'], history[-2]['content']])
        print('Wrote user!')
        #print('Writing assistant...')
        write_to_gsheet(row = [deployment_name, now(), json.dumps(msg), msg['role'], msg['content']])
        print('Wrote assistant!')
    except Exception as e:
        print(f'Sth wrong with writing to gsheet {e}')
    return jsonify({"message": "Text stored successfully", "history": history, "response": openai_response}), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
