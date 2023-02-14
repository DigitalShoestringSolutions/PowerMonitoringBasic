echo "Starting Setup Script"
echo "---------------------"
echo "Setting Up Logging"
echo "---------------------"
sudo apt-get install rsyslog logrotate -y

sudo install -d -m 775 -o root -g adm /var/log/containers

sudo cp setup_files/syslog.conf /etc/rsyslog.d/40-docker.conf
sudo systemctl restart rsyslog

sudo cp setup_files/logrotate /etc/logrotate.d/docker

echo "---------------------"
echo "Setup Script Complete"
echo "---------------------"

sleep 3
