# Questionnaire REST API
This article still writing
## How to deploy with docker:
Install [Docker Engine](https://docs.docker.com/engine/install/) if it's not.
Download rep and setup virtual enviroment:
```
git clone https://github.com/Holography7/DjangoQuestionnaireAPI.git
cd DjangoQuestionnaireAPI
python3 -m venv questionnaire-venv
source questionnaire-venv/bin/activate
```
Setup all python modules. You may see errors with wheels, ignore them:
```
cd src
pip3 install -r requirements.txt
```
Change SECRET_KEY in .questionnaire-venv.prod:
```SECRET_KEY=your_secret_key```

Deploy:
```
cd ..
sudo docker-compose -f docker-compose.prod.yml up -d --build
```
Sadly, creating superuser not allowed through docker, so you should do this manually in other terminal:
```
cd path/to/your/project
sudo docker-compose -f docker-compose.prod.yml exec python manage.py createsuperuser
```
If you need to down:
```sudo docker-compose -f docker-compose.prod.yml down -v```
## How to deploy manually
Download rep and setup virtual enviroment:
```
git clone https://github.com/Holography7/DjangoQuestionnaireAPI.git
cd DjangoQuestionnaireAPI
python3 -m venv questionnaire-venv
source questionnaire-venv/bin/activate
```
Setup all python modules. You may see errors with wheels, ignore them:
```
cd src
pip3 install -r requirements.txt
```
Change file src/questionnaire/settings.py:
```
...
SECRET_KEY = os.getenv('SECRET_KEY')
...
DEBUG = False
...
ALLOWED_HOSTS = ['example.com', ]
```
Add enviroment variable SECRET_KEY:
```export SECRET_KEY=your_secret_key```

Make migrations:
```
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic
```
Import data to DB:
```
python manage.py loaddata questiontype.json
python manage.py loaddata groups.json
```
Create superuser for your project:
```python manage.py createsuperuser```

Create gunicorn config:
```sudo nano /etc/systemd/system/gunicorn.service```

And put next code:
```
[Unit]
Description=gunicorn service
After=network.target

[Service]
User=YourUsername
Group=www-data
WorkingDirectory=/your/path/to/project
ExecStart=/your/path/to/env/bin/gunicorn --access-logfile - --workers 3 --bind unix:/your/path/to/project/questionnaire.sock questionnaire.wsgi:application

[Install]
WantedBy=multi-user.target
```
**Dont't forget change user and paths.**

Press Ctrl+S to save file and Ctrl+X to close it.

Enable and start service:
```
sudo systemctl enable gunicorn.service
sudo systemctl start gunicorn.service
sudo systemctl status gunicorn.service
```
If you get some trouble, you can see into journal:
```journalctl -u gunicorn```

If you changed something, restart service:
```
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
```
Setup Nginx:
```sudo apt install nginx```

Create custom config:
```sudo nano /etc/nginx/sites-available/questionnaire```

And put next code:
```
server {
    listen 80;
    server_name www.yourdomain.com;
    location = /favicon.ico {access_log off;log_not_found off;}

    location /static/ {
        alias /your/path/to/project/static/; # ended / is required!
    }

    location / {
         include proxy_params;
         proxy_pass http://unix:/your/path/to/project/questionnaire.sock;
    }
}
```
**Dont't forget change domain and paths.**
Create symlink to enable this file, test it and start:
```
sudo ln -s /etc/nginx/sites-available/questionnaire /etc/nginx/sites-enabled
sudo nginx -t
sudo service nginx start
```

If you need to restart or stop:
```
sudo service nginx restart
sudo service nginx stop
```
