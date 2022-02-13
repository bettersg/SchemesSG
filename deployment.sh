#!/bin/bash
sudo apt update
sudo apt install -y python3-pip
sudo -H pip install -r requirements.txt
sudo apt-get install -y nginx uwsgi uwsgi-plugin-python3 python3-certbot-nginx
sudo python3 -m nltk.downloader punkt
python3 -m nltk.downloader punkt
sudo cp -R /home/flask/nltk_data/tokenizers /usr/nltk_data/
sudo cp ./server_utilities/schemes_sg.service /etc/systemd/system/schemes_sg.service
sudo cp ./server_utilities/schemes_sg_nginx /etc/nginx/sites-available/schemes_sg_nginx
sudo ln -s /etc/nginx/sites-available/schemes_sg_nginx /etc/nginx/sites-enabled/schemes_sg_nginx
sudo rm /etc/nginx/sites-enabled/default
sudo chown www-data:www-data -R ./
 sudo chown www-data:www-data -R /var/www/
sudo systemctl start schemes_sg
sudo service nginx reload
