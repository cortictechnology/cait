import socket
import time
import os

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


while True:
  stat = os.system('service hostapd status')
  if is_internet_connected():
    if stat == 0:
      print("WIFI + AP on")
      #os.system("sudo systemctl mask hostapd.service")
      #os.system("reboot")
    else:
      print("Only WIFI on")
  else:
    if stat != 0:
      print("WIFI + AP off")
      #os.system("sudo systemctl unmask hostapd.service")
      #os.system("reboot")
    else:
      print("Only WIFI off")

  time.sleep(10)