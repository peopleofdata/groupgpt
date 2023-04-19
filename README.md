# groupgpt

ChatGPT only allows one person to talk to it. But what if multiple people could share one session?

Aside from a lot of swearing, I hope this collaborative approach makes things more interesting ;)

# Workflow

"Your branch" => main (autodeploy) => stable (do not merge/push without consent)

You can merge your own fixes into main to autodeploy & test. But stay away from "stable" ;)

# Local installation:
pip install -r requirements.txt
add a system variable with openai api key (ask Oskar) like $openai='key'
python app.py
