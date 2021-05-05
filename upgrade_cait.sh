sudo systemctl stop cait_components.service 
sudo systemctl stop cait_webapp.service
sudo rm -rf /opt/cortic_webapp/
FILE=/opt/cortic_modules/voice_module/account.json
if test -f "$FILE"; then
    sudo cp /opt/cortic_modules/voice_module/account.json ./
fi
sudo cp -R /opt/cortic_modules/vision_module/database ./
sudo rm -rf /opt/cortic_modules/*
sudo cp -R src/cortic_webapp_bin /opt/
sudo mv /opt/cortic_webapp_bin/ /opt/cortic_webapp
sudo cp -R src/ai_modules_bin/* /opt/cortic_modules/
sudo cp -R src/cait_bin/ /opt/cortic_modules/
sudo mv /opt/cortic_modules/cait_bin/ /opt/cortic_modules/cait
FILE=./account.json
if test -f "$FILE"; then
    sudo mv account.json /opt/cortic_modules/voice_module
fi
sudo mv database /opt/cortic_modules/vision_module

sudo cp src/docker-compose.yml ~/
echo "Upgrade Finished, Rebooting in 10 seconds"
sleep 10
sudo reboot
