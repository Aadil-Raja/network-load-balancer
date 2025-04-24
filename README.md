sudo apt update
sudo apt install nginx -y
sudo nginx -c $(pwd)/nginx.conf
sudo nginx -s reload
sudo nginx -s stop

sudo apt update
sudo apt install haproxy -y
sudo haproxy -f $(pwd)/haproxy.cfg
sudo haproxy -c -f $(pwd)/haproxy.cfg
sudo systemctl stop haproxy