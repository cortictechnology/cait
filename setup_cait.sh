options=("$@")
wlanInterfaceNameDefault="wlan0"
apSsid="cait"
apPassword="caitcait"
apIp="10.0.0.1"
apCountryCode="CA"
serial=$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)

sudo apt update
sudo apt -y full-upgrade
cd setup_scripts
sudo addgroup cait
sudo usermod -a -G cait pi
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo touch /etc/docker/daemon.json
sudo bash -c 'echo "{\"experimental\": true}" > /etc/docker/daemon.json'

sudo systemctl restart docker
sudo docker pull homeassistant/home-assistant:stable
sudo docker pull cortictech/speech:0.51
sudo docker pull cortictech/nlp:0.51
sudo docker pull cortictech/vision:0.51
sudo docker pull cortictech/control:0.51
sudo docker pull cortictech/broker:0.51
sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
sudo sh -c "echo 'nameserver 8.8.8.8' >> /etc/resolv.conf"
sudo apt-get install v4l-utils -y
sudo apt-get install portaudio19-dev mplayer -y
sudo pip3 install docker-compose flask Flask-HTTPAuth flask_cors paho-mqtt gunicorn pyaudio
sudo cp -R ../src/cortic_webapp /opt
sudo cp -R ./homeassistant/ ~/
sudo apt-get install python3-pil python3-pil.imagetk -y
sudo pip3 install filelock wifi
sudo apt install whois
sudo mkdir /opt/cortic_modules
sudo cp -R ../src/cait /opt/cortic_modules
sudo cp -R ../src/ai_modules/* /opt/cortic_modules
sudo cp ../src/docker-compose.yml ~/
sudo apt-get install npm nodejs -y
sudo npm install -g configurable-http-proxy
sudo pip3 install notebook
sudo pip3 install jupyterhub
sudo cp chkpass.sh start_cait_components.sh start_jupyterhub.sh add_wifi.py scan_wifi.py enableAP.sh /opt/
sudo cp cait_webapp.service cait_jupyter.service cait_components.service /etc/systemd/system
sudo cp change_hostname.sh /usr/sbin
sudo chmod +x /usr/sbin/change_hostname.sh
sudo systemctl daemon-reload
sudo systemctl enable /etc/systemd/system/cait_*

sudo rm get-docker.sh

for i in ${!options[@]}; do

    option="${options[$i]}"

    if [ "$option" = --ap-ssid=* ]; then
        apSsid="$(echo $option | awk -F '=' '{print $2}')"
    fi

    if [[ "$option" == --ap-password=* ]]; then
	    apPassword="$(echo $option | awk -F '=' '{print $2}')"
    fi

    if [[ "$option" == --ap-country-code=* ]]; then
	    apCountryCode="$(echo $option | awk -F '=' '{print $2}')"
    fi

    if [[ "$option" == --ap-ip-address=* ]]; then
        apIp="$(echo $option | awk -F '=' '{print $2}')"
    fi

done

originalHost=$(hostname)
hostName="cait-$serial"
echo "Changing hostname to: $hostName"
sudo sed -i "s/$originalHost/$hostName/" /etc/hostname
sudo sed -i "s/$originalHost/$hostName/" /etc/hosts

sudo ./setup-network.sh --install --ap-ssid="$apSsid" --ap-password="$apPassword" --ap-country-code="$apCountryCode" --ap-ip-address="$apIp" --wifi-interface="$wlanInterfaceNameDefault"
