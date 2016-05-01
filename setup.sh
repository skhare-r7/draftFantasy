#!/bin/bash
apt-get update
apt-get install python-pip
apt-get install emacs
timedatectl set-timezone America/Toronto
apt-get install apache2
apt-get install php5 libapache2-mod
apt-get install php5-sqlite

/etc/init.d/apache2 restart

pip install python-telegram-bot
apt-get install zlib1g-dev libxml2-dev libxslt-dev python-dev
pip install lxml

