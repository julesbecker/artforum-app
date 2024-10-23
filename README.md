# Development/running locally:

1. set the path to the Google Cloud key (for Firestore DB access) in `main.py`
2. setup a virtual environment and install requirements:
```
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
```
3. for debugging, run with `python main.py`. otherwise, use [gunicorn](https://flask.palletsprojects.com/en/1.1.x/deploying/wsgi-standalone/), which is what runs inside the Docker container below. The app can be killed/restarted with `sudo pkill -HUP gunicorn` if you're running it with that.

# Running in production with Dockerfile:

- make sure the google cloud `key.json` is copied to the root of this directory
- run:
```bash
sudo docker rm -f artforum # to remove previous built container
sudo docker build -t artforum-app .
sudo docker run -d --name artforum -p 8080:8080 artforum-app
sudo docker logs artforum -f # to view logs
```
