options=("$@")
wlanInterfaceNameDefault="wlan0"
apSsid="cait"
apPassword="caitcait"
apIp="10.0.0.1"
apCountryCode="CA"
serial=$(cat /proc/cpuinfo | grep Serial | cut -d ' ' -f 2)

# Using an older wifi firmware due to a known issue for rpt8 firmware: https://github.com/raspberrypi/firmware/issues/1463
wget http://archive.raspberrypi.org/debian/pool/main/f/firmware-nonfree/firmware-brcm80211_20190114-1+rpt10_all.deb
sudo dpkg --purge firmware-brcm80211
sudo dpkg --install firmware-brcm80211_20190114-1+rpt10_all.deb
sudo apt-mark hold firmware-brcm80211
rm firmware-brcm80211_20190114-1+rpt10_all.deb

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
sudo mkdir ~/cait_workspace
sudo cp ../samples/block_samples/* ~/cait_workspace
sudo systemctl restart docker
sudo docker pull homeassistant/home-assistant:stable
sudo docker pull cortictech/speech:0.52
sudo docker pull cortictech/nlp:0.52
sudo docker pull cortictech/vision:0.52
sudo docker pull cortictech/control:0.52
sudo docker pull cortictech/broker:0.51
sudo sh -c "echo 'dtparam=spi=on' >> /boot/config.txt"
# Need to add nameserver for later apt-get install, otherwise, there is chance for it to not able reolve domain
sudo sh -c "echo 'nameserver 8.8.8.8' >> /etc/resolv.conf"
sudo apt-get install v4l-utils -y
sudo apt-get install portaudio19-dev mplayer graphviz libbluetooth-dev bluez-tools -y
sudo pip3 install docker-compose flask Flask-HTTPAuth flask-login flask_cors paho-mqtt gunicorn pyaudio lolviz cython pybluez
sudo apt-get install npm nodejs -y
npm install --save-dev javascript-obfuscator
sudo npm link javascript-obfuscator
cd ../utils
bash compile_scripts.sh
cd ../setup_scripts
sudo cp -R ../src/cortic_webapp_bin /opt
sudo mv /opt/cortic_webapp_bin /opt/cortic_webapp
sudo cp -R ./homeassistant/ ~/
sudo apt-get install python3-pil python3-pil.imagetk -y
sudo pip3 install filelock wifi
sudo apt install whois
sudo mkdir /opt/cortic_modules
sudo cp -R ../src/cait_bin /opt/cortic_modules
sudo mv /opt/cortic_modules/cait_bin /opt/cortic_modules/cait
sudo cp -R ../src/ai_modules_bin/* /opt/cortic_modules
sudo mkdir /opt/cortic_modules/vision_module/database
sudo cp ../src/docker-compose.yml ~/
sudo touch /opt/accounts
sudo npm install -g configurable-http-proxy
sudo pip3 install notebook
sudo pip3 install jupyterhub
sudo cp chkpass.sh start_cait_components.sh start_jupyterhub.sh add_wifi.py scan_wifi.py monitor_wifi.py /opt/
sudo cp cait_webapp.service cait_jupyter.service cait_components.service cait_wifi.service bt-agent.service bt-network.service /etc/systemd/system
sudo cp pan0.netdev pan0.network /etc/systemd/network
sudo cp change_hostname.sh /usr/sbin
sudo chmod +x /usr/sbin/change_hostname.sh
sudo systemctl daemon-reload
sudo systemctl enable systemd-networkd
sudo systemctl enable bt-agent
sudo systemctl enable bt-network
sudo systemctl enable /etc/systemd/system/cait_*
sudo rm get-docker.sh
sudo bash -c 'echo "denyinterfaces pan0" >> /etc/dhcpcd.conf'

for i in ${!options[@]}; do

    option="${options[$i]}"

    if [[ "$option" == --ap-ssid=* ]]; then
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

sudo /usr/sbin/change_hostname.sh "$hostName"

sudo ./setup-network.sh --install --ap-ssid="$apSsid" --ap-password="$apPassword" --ap-country-code="$apCountryCode" --ap-ip-address="$apIp" --wifi-interface="$wlanInterfaceNameDefault"
