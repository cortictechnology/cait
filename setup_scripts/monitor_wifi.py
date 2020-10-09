import socket
import time
import os
import logging

logging.getLogger().setLevel(logging.INFO)

def is_internet_connected(host="8.8.8.8", port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False

all_disconnect_count = 0
first_internet_up = False
first_internet_up_time = time.time()

while True:
  stat = os.system('service hostapd status')
  if is_internet_connected():
    if not first_internet_up:
      first_internet_up = True
      first_internet_up_time = time.time()
    if stat == 0:
      if (time.time() - first_internet_up_time) > 120:
        logging.info("WIFI + AP on")
        os.system("mplayer /opt/cortic_modules/voice_module/apOff.mp3")
        os.system("sudo systemctl mask hostapd.service")
        os.system("sudo systemctl stop hostapd.service")
        #os.system("reboot")
    else:
      logging.info("Only WIFI on")
    all_disconnect_count = 0
  else:
    if stat != 0:
      if all_disconnect_count == 3:
          logging.info("WIFI + AP off")
          all_disconnect_count = 0
          os.system("mplayer /opt/cortic_modules/voice_module/apOn.mp3")
          os.system("sudo systemctl unmask hostapd.service")
          os.system("reboot")
      all_disconnect_count = all_disconnect_count + 1
    else:
      logging.info("Only WIFI off")

  time.sleep(10)