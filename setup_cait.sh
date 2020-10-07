options=("$@")
wlanInterfaceNameDefault="wlan0"
apSsid="cait"
apPassword="caitcait"
apIp="10.0.0.1"
apCountryCode="CA"

cd setup_scripts
sudo addgroup cait
sudo usermod -a -G cait pi
curl -fsSL get.docker.com -o get-docker.sh && sh get-docker.sh
sudo groupadd docker
sudo gpasswd -a $USER docker
sudo touch /etc/docker/daemon.json
sudo bash -c 'echo "{\"experimental\": true}" > /etc/docker/daemon.json'

sudo systemctl restart docker
sudo docker pull registry.cortic.ca/cait-stt_tts
sudo docker pull registry.cortic.ca/cait-nlp
sudo docker pull registry.cortic.ca/cait-vision
sudo docker pull registry.cortic.ca/cait-control
sudo docker pull registry.cortic.ca/cait-broker
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
sudo cp -R ../ai_modules/* /opt/cortic_modules
sudo cp ../src/docker-compose.yml ~/
sudo apt-get install npm nodejs -y
sudo npm install -g configurable-http-proxy
sudo pip3 install notebook
sudo pip3 install jupyterhub
sudo cp chkpass.sh start_cait_components.sh start_jupyterhub.sh add_wifi.py scan_wifi.py enableAP.sh /opt/
sudo cp cait_webapp.service cait_jupyter.service cait_components.service /etc/systemd/system
sudo systemctl daemon-reload
cd /etc/systemd/system
sudo systemctl enable cait_*
rm get-docker.sh

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

sudo ./setup-network.sh --install --ap-ssid="$apSsid" --ap-password="$apPassword" --ap-country-code="$apCountryCode" --ap-ip-address="$apIp" --wifi-interface="$wlanInterfaceNameDefault"
