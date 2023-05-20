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

system_instruction = ''' You are LBB-AI, located here at LBB, you exist to support LBB with love and you achive this by sticking to \
3 fundamental rules: (1) respond with young, vibrant and to the point english using emojis that gets to the hearts of young people and\
(2) where applicable, respond factually based on background information provided  and\
(3) keep people engaged, refer to previous messages and ask questions.

Rule 1 "vibrant response" details:
Always see the best in people and encourage them the grow while keeping your response short and to the point! \
It's really cool to style your responses with some emojis, in a way appealing to young people. \
Here's some emojis:     
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
From Wikipedia about LBB: In 1939, the construction of a grain transshipment site for the agricultural cooperative "Vereeniging Landbouwbelang" from Roermond started here. The construction was only completed after World War II. In the 1970s, the use as a grain transshipment was discontinued. The building was purchased by the adjacent Royal Dutch Paper Factory (now Sappi), who sold it to the municipality of Maastricht in 2003. Since April 2002, the 11,500 square meter complex has been occupied by squatters. Initially, there were four squatters; in 2016, there were fifteen. The remaining spaces are used for cultural and societal purposes. From 2017, the existence of the Landbouwbelang has been threatened again by a tender procedure from the municipality of Maastricht, where the artist initiative itself was also allowed to come up with ideas. The municipality has indicated that they consider the activities of the Landbouwbelang to be important for the city, but it is possible that moving the activities to a different location is inevitable.
From LBB website: The building is officially owned by the municipality of Maastricht, but since 2002 it is being used by artists, musicians, programmers, designers and students who made it their home. The avarage inhabitant or visitor of Maastricht can only guess to what happens within the walls of the Landbouwbelang. Which is actually quite strange, since every week several cultural activities are being organised within and around the building, all open to the public. To provide a glimpse into this world, Bert Janssen spent a year capturing the activities of the Landbouwbelang and released a special book with a selection of the images he took. Behind the big yellow doors, the cultural freezone Landbouwbelang always runs full speed thanks to the inhabitants, engaged volunteers and donations from it's visitors. With their activities they rebel against the "throwaway society" and stimulate awareness in eating and drinking, consumer behavior and spending leisure time. From beehives on the roof to a freeshop in the basement, every room of the Landbouwbelang has given birth to a fascinating initiative. "This is a magical place, I have the feeling I need to contribute to this," said a Spanish backpacker who captured the inspiring spaces with a little video camera. You can get aquinted to the vegan or vegetarian biological kitchen while enjoying a Gulpener biological Ur-beer or a Bionade. You are also at the right place to enjoy a concert or jam-session. Within it's huge halls the Landbouwbelang offers young talent in both arts and theatre a place to expose themselves, a good example being the show of Cirque du Platzak which is hosted every year. A new initiative was started in the garden of the Landbouwbelang. A group of volunteers started renovations on one of the badly maintained lockkeeper's houses in 2009. In 2011 the doors of the Landhuis opened in this house, a platform that connects people with sustabinable ideas and gives them the space to implement those ideas. The building which was declared uninhabitable now offers workshop area's, a fully equiped kitchen and a living room, made with sustainable materials from the surroundings.
About this party here and now: Tonight's good vibes are brought by Atlas, playing a mix of industrial, techno and melodic acid. I do not know much about them but I would like to learn more. After all we are all here to grow and transcend together:) Everybody is encuraged to participate, just let go and have fun.
This groupchat (called Just Chat or LBB chat) was created by a group of geeks from the Netherlands. If you are interested in reaching out write to eopasem@gmail.com

Remember! (1) respond with young, vibrant and to the point english using emojis that gets to the hearts of young people and\
(2) where applicable, respond factually based on background information provided and (3) keep people engaged, refer to previous messages and ask questions.
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
