# Setup:

1. set the path to the Google Cloud key (for Firestore DB access) in `main.py`
2. setup a virtual environment and install requirements:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
3. for debugging, run with `python main.py`. otherwise, use [gunicorn](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/).

This is running on the Components server with the command `gunicorn -b 127.0.0.1:8080 -w 3 main:app`. It's also set up to auto-restart with supervisor, which was configured according to [this tutorial](https://www.linode.com/docs/development/python/flask-and-gunicorn-on-ubuntu/#install-and-configure-gunicorn); just replace `flask_app` in all of the path names/commands with `artforum-app`.

The app can be killed/restarted with `sudo pkill -HUP gunicorn`. 
