import sys

print(sys.argv)
wifi_name = sys.argv[1]
password = sys.argv[2]
isHidden = sys.argv[3]

if isHidden == "Y" or isHidden == "y":
        network_str = '\nnetwork={\n        ssid=\"' + wifi_name + '\"\n        scan_ssid=1\n        psk=\"' + password + '\"\n}\n'
else:
        network_str = '\nnetwork={\n        ssid=\"' + wifi_name + '\"\n        psk=\"' + password + '\"\n}\n'

with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'a') as f:
	f.write(network_str)

