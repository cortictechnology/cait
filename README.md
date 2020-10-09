<div align="center">
    <img src="images/cait.png" width="60%">
</div>

**`Documentation`** |
------------------- |
[![Documentation](https://img.shields.io/badge/api-reference-blue.svg)](https://www.tensorflow.org/api_docs/) |


CAIT is a software package to provide a no-code interface to create AI applications 

## How do I try it

Download the prebuilt raspbian image: 

Use any image writing tool to clone the image to a sd card, e.g. dd, pi imager.

## Install from source

```
$ git clone https://github.com/cortictechnology/cait.git
$ cd cait
$ bash setup_cait.sh --ap-ssid=<ssid_name> --ap-password=<ap_password> --ap-country-code=<country_code> --ap-ip-address=<desired_ap_ip> --wifi-interface=<wifi_interface_name>
```

The above setup script starts the raspberry pi in both access point mode and station mode.  The user can provide custom values for the access point name, password, desired ip address, and the wifi ssid name. If no parameters are given, the default values are: <br/>
```
<ssid_name>: "cait" 
<ap_password> : "caitcait" 
<country_code>: "CA" 
<desired_ap_ip>: "10.0.0.1" 
<wifi_interface_name>: "wlan0"
```

After the above setup is finished, the device's hostname is changed to cait-<device_serial_number>, you can find the exact hostname during the script's process, in the line: "Changing hostname to:" with the new hostname highlighted in red.

### Screenshot of highlighted hostname

## Quick start

### Using the visual programming interface:

In browser, go to: 
```
http://<hostname>.local
```

The first time you enter this address, you will be directed to a setup page, in which you will be asked to enter a new device name (hostname), and to create an user account for future login. 

### Screenshot of device setup page

Next, you can test the functionality of any attached camera and audio device, to make sure you have connected the compatible ones.

### Screenshot of hardware page

After that, you will be asked to signup for a google cloud service account for voice-related service, and upload the account file to the device.

### Screenshot of google account page

Finally, you need to reboot CAIT for everything to be applied.

### Screenshot of finish page.

After the device is rebooted, enter the above address in browser, you can now login with your just created account. Alternatlivey, you can login with a default account to access sample programs:

```
username: pi
password: raspberry
```

### Screenshot of login page

Once logged in, you can then create any program by drag-and-drop the basic programming blocks and Cortic AI blocks.

### Screenshot of a sample program

### Configuring smart home devices:

We integrated homeassistant into the toolkit, so that you can connect the device with your existing smart device by entering:
 
```
http://<hostname>.local:8213
username: ai
password: ai
```

Once you configured your smart devices, you will be able to control them in CAIT's visual programming interface.

### Screenshot of homeassistant config page

### Programming in Python with Jupyter Hub:

We also integrated Jupyter hub and notebook support in CAIT, you can use it by entering:

```
http://<hostname>.local:8000
```

You can program with CAIT's AI functionalities in Python. Any program created in CAIT's visual programming interface can be converted to equivalen Python program and execture in here.

### Screenshot of jupyter notebook

## How to contribute

## Known Issues

 1. https://github.com/raspberrypi/firmware/issues/1463

## License
[MIT License](LICENSE)