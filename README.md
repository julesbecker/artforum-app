# Setup:

1. set the path to the Google Cloud key (for Firestore DB access) in `main.py`
2. setup a virtual environment and install requirements:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
3. for debugging, run with `python main.py`. otherwise, use something like [gunicorn](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/).
