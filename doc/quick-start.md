# Quick Start

If your raspberry pi's WIFI connection was not already configured, it will advertise itself as a WIFI access point with the ssid "cait" after booting up to allow easy headless setup.  Make sure to connect your computer's WIFI to the SSID advertised by the raspberry pi and then go to `http://cait.local/setup` on your browser.  If you are using a windows machine to connect to the raspberry pi, you may experience problems resolving its hostname.  In this case, you can install [Bonjour](https://support.apple.com/kb/dl999?locale=en_CA) on and restart the computer.  The raspberry pi's hostname should resolve after that.
  
## Setup

You can connect to the CAIT's visual programming interface using any computer, including the Raspberry Pi 4B that hosts CAIT, on the same local WIFI.  In the web browser, go to:	

```	
http://<hostname>.local	
```	

The first time you enter this address, you will be directed to a setup page, in which you will be asked to enter a new device name (hostname), and to create an user account for future login. 	

<img src="../images/device_setup.png" width="60%">	

Next, you can test the functionality of any attached camera and audio device, to make sure you have connected the compatible ones.	

<img src="../images/testhw.png" width="60%">	

After that, you will be asked to signup for a google cloud service account for voice-related service, and upload the account file to the device. A screencast of how to create a google cloud service account and download the account file is shown below.

<img src="../images/google.png" width="60%">	

<screencast of google setup>

Finally, you need to reboot CAIT for everything to be applied.	

<img src="../images/finish.png" width="60%">	

## Using the visual programming interface

After the device is rebooted, enter the above address in browser, you can now login with your just created account. Alternatlivey, you can login with a default account to access sample programs:	

```	
username: pi	
password: raspberry	
```	

<img src="../images/login.png" width="60%">	

Once logged in, you can then create any program by drag-and-drop the basic programming blocks and Cortic AI blocks.	

<img src="../images/sample.png" width="60%">	

### Configuring smart home devices:	

We integrated homeassistant into the toolkit, so that you can connect the device with your existing smart device by entering:	

```	
http://<hostname>.local:8213	
username: ai	
password: ai	
```	

Once you configured your smart devices, you will be able to control them in CAIT's visual programming interface.	

<img src="../images/ha.png" width="60%">	

### Programming in Python with Jupyter Hub:	

We also integrated Jupyter hub and notebook support in CAIT, you can use it by entering:	

```	
http://<hostname>.local:8000	
```	

You can program with CAIT's AI functionalities in Python. Any program created in CAIT's visual programming interface can be converted to equivalen Python program and execture in here.	

<img src="../images/notebook.png" width="60%">
