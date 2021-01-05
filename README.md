<div align="center">
    <img src="images/cait.png" width="50%">
</div>
<br>

[![Documentation](https://img.shields.io/badge/api-reference-blue.svg)](https://michaelnhw.github.io/test_page/)  [![QuickStart](https://img.shields.io/badge/doc-quick%20start-blue.svg)](https://github.com/cortictechnology/cait/blob/main/doc/quick-start.md)

## CAIT

The Cortic A.I. Toolkit, or CAIT for short, is a software package that enables makers and students to learn and experiment with A.I. algorithms on the popular Raspberry Pi 4B single board computer.  Our goal is to eliminate complicated software setup and allow people to easily integrate A.I. into their own projects.  We take a container based approach and pre-installed many state-of-the-art open source A.I. software packages/frameworks into cohesive docker containers.  We link these containers into a single system by employing the lightweight MQTT protocol. We also extended Google's Blockly visual programming language to offer a quick prototyping environment for our users.  CAIT currently has a nubmer of custom A.I. and automation blocks:

| <img src="https://github.com/cortictechnology/cait/blob/main/images/face-recognition.gif" width="100%"> | <img src="https://github.com/cortictechnology/cait/blob/main/images/image-classification.gif" width="100%"> | <img src="https://github.com/cortictechnology/cait/blob/main/images/object-detection.gif" width="100%">
|:--:|:--:|:--:|
| *Face Recognition* | *Image Classification* | *Object Detection* |
| <img src="https://github.com/cortictechnology/cait/blob/main/images/nlp.gif" width="100%"> | <img src="https://github.com/cortictechnology/cait/blob/main/images/lego-motor.gif" width="100%"> | <img src="https://github.com/cortictechnology/cait/blob/main/images/home-assistant.gif" width="100%"> |
| *Natural Language Processing* | *LEGO Motor Control* | *Smart Home Control* |

All of these custom blocks are backed by a simple Python API.  You may choose to program directly using this API for added flexibility and power.  In fact, if you already have a running project that uses the visual programming interface, you can easily convert it into Python code using our automated conversion tool.  

## Hardware

Here is a list of hardware components that we currently support.  You may choose a subset of them to suit your own projects.

* Any of Raspberry Pi 4B 2GB/4Gb/8GB models
* Micro SD card (32GB recommended)
* Logitech USB webcam (C270, C922, C615, C310 are tested)
* Mini speaker with 3.5mm audio jack 
* LEGO Mindstorms EV3 
* LEGO Mindstorms Robot Inventor
* LEGO Spike Prime
* Smart home devices such as Philips Hue, smart speakers, etc

We also support the use of Raspberry Pi's CSI camera interface.  However, if your project requires audio/speech input, it's much better to use a USB webcam as it has an integrate microphone.  The integrated mic usually offers much better audio input performance than any of the mini USB mics that we have tested.

## How do I try it

Before you start, make sure there is at least 32GB of free space on your SD card.  

```
$ git clone https://github.com/cortictechnology/cait.git
$ cd cait
$ ./setup_cait.sh --ap-ssid=<ssid_name> --ap-password=<ap_password> --ap-country-code=<country_code> --ap-ip-address=<desired_ap_ip> --wifi-interface=<wifi_interface_name>
```

You can provide custom values for the access point name, password, desired ip address, and the wifi ssid name. If no parameters are given, the default values are: 

```
<ssid_name>: "cait" 
<ap_password> : "caitcait" 
<country_code>: "CA" 
<desired_ap_ip>: "10.0.0.1" 
<wifi_interface_name>: "wlan0"
```

After the setup process is completed, the device's hostname is changed to cait-<device_serial_number>.  You can find the exact hostname by looking at the last line of the setup script output.  It should say: "Hostname is changed to: <hostname>", with the new hostname highlighted in <span style="color:red">red</span> as shown below.  Of course, you can always use the `raspi-config` utility to change the hostname to whatever you like.

<img src="images/hostname.png" width="80%">

The above setup script configures the raspberry pi to operate in access point mode if it cannot connect to any WIFI hotspot.  This can be very useful if the raspberry pi is brought to a new location where the WIFI has not been configured.  In this case, you can easily configure it to use the new WIFI headlessly by connecting your computer to the raspberry pi's access point, and then visit `http://<hostname>.local/setup`.  If there is a problem resolving the hostname, you can also go to `http://<ap-ip-address>/setup` instead.

Next, Please follow our [Quick Start](https://github.com/cortictechnology/cait/wiki/1.0-Quick-Start) wiki page to get started.

## How to contribute

We welcome contributions from all our users.  You can contribute by requesting features or reporting bugs under "Issues".  You can also submit proposed code updates through pull requests to our "dev" branch.

## Upcoming new project

While working on CAIT, we ran into a lot of computational constraints.  Even though the quad core Raspberry Pi 4B CPU is quite powerful, it is still sometime not fast enough to run multiple deep learning inferences.  We kept wishing that there is an easy way for us to offload some of the computation to another nearby idle device without having to deal the complexity of distributed programs.  After spending some time researching the available open-source technology, we decided to implement something that suits our needs.  

The result is the upcoming CURT project, or the big brother to CAIT if you will.  The goal of CURT is to enable our users to create distributed A.I. applications with minimal effort and minimal computational overhead.  We also want to minimize the amount of effort spent in configuring each device and allow different hardware devices to work together seamlessly.  CURT can be used as a backend for CAIT to offer more flexibility and gives users the ability to write programs for difference devices to cooperate to accomplish a common goal.

The CURT project is progressing very nicely.  We are planning to release it in the first half of 2021.  Stay tuned.

## License

[GPLv3 License](LICENSE)
