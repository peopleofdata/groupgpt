# groupgpt

ChatGPT only allows one person to talk to it. But what if multiple people could share one session?

Aside from a lot of swearing, I hope this collaborative approach makes things more interesting ;)

This is deployed on Heroku through an automated CI/CD pipeline. Push to "prod" branch to trigger a build.

Local installation:
pip install -r requirements.txt
add a system variable with openai api key (ask Oskar) like $openai='key'
python app.py
