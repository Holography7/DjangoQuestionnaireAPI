Test readme.
How to deploy with docker:
python3 -m venv questionnaire/venv
cd src
pip3 install -r requirements.txt
cd..
sudo docker-compose -f docker-compose.prod.yml up -d --build
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata questiontype.json
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py loaddata groups.json
sudo docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --no-input --clear
Down:
sudo docker-compose -f docker-compose.prod.yml down -v
