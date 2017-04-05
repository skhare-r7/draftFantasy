#!/bin/bash
apt-get update
apt-get install python-pip
apt-get install emacs
timedatectl set-timezone America/Toronto

apt-get install apache2
apt-get install php7.0 libapache2-mod-php7.0 php7.0-sqlite

apt-get install unzip
wget https://bitbucket.org/phpliteadmin/public/downloads/phpLiteAdmin_v1-9-7-1.zip
#edit admin.php to point to db folder, and place in /var/www/html/

/etc/init.d/apache2 restart

pip install python-telegram-bot
apt-get install zlib1g-dev libxml2-dev libxslt-dev python-dev
pip install lxml prettytable python-dateutils

