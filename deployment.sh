#!/bin/bash
pip install -r requirements.txt
sudo apt-get -y nginx
sudo cp ./server_utilities/schemes_sg.service /etc/systemd/system/schemes_sg.service
sudo cp ./server_utilities/schemes_sg_nginx /etc/nginx/sites-available/schemes_sg_nginx
sudo ln -s /etc/nginx/sites-available/schemes_sg_nginx /etc/nginx/sites-schemes_sg_nginx
sudo rm /etc/nginx/sites-enabled/default
sudo service nginx reload