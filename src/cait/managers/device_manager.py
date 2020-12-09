""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2020

"""

import paho.mqtt.client as mqtt
import logging
import time
import re
import os
import subprocess
import threading
import pyaudio
import spidev
from ctypes import *

logging.getLogger().setLevel(logging.INFO)

EXCLUDED_DEVICES = ['bcm2835-codec-decode (platform:bcm2835-codec):', 'bcm2835-isp (platform:bcm2835-isp):']
TESTED_CAMERAS = {'Webcam C170': [320,240], 'HD Webcam C615':[640,480], 'UVC': [320, 240], 'PiCamera':[640,480], 'C922': [640, 480], 'C310': [640, 480]}
SUPPORTED_SPEAKERS = ['bcm2835 HDMI 1', 'bcm2835 Headphones', 'USB']
SUPPORTED_MIC = ['Webcam C170', 'HD Webcam C615', 'USB', 'C922', 'C310']
SUPPORTED_CONTROL_HAT = ['BrickPi', 'Adafruit Servo HAT', "Makebot"]

ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    return
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

asound = cdll.LoadLibrary('libasound.so')
# Set error handler
asound.snd_lib_error_set_handler(c_error_handler)

class DeviceManager:
    def scan_usb_devices(self):
        device_re = re.compile("Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
        df = str(subprocess.check_output("lsusb"), 'utf-8')
        usb_devices = []
        for i in df.split('\n'):
            if i:
                info = device_re.match(i)
                if info:
                    dinfo = info.groupdict()
                    dinfo['device'] = '/dev/bus/usb/%s/%s' % (dinfo.pop('bus'), dinfo.pop('device'))
                    dinfo['time'] = time.time()
                    usb_devices.append(dinfo)
        return usb_devices

    def scan_video_devices(self):
        cmd = ["/usr/bin/v4l2-ctl", "--list-devices"]
        out, err = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()
        out, err = str(out.strip(), 'utf-8'), err.strip()
        video_devices = []
        for l in [i.split("\n\t") for i in out.split("\n\n")]:
            if l[0] not in EXCLUDED_DEVICES:
                resolution = [640, 480]
                for cam in TESTED_CAMERAS.keys():
                    if cam in l[0]:
                        resolution = TESTED_CAMERAS[cam]
                cam_index = l[1][l[1].find('/video')+6:]
                vinfo = {"device": l[0], "index": cam_index, "resolution": resolution, "time": time.time()}
                video_devices.append(vinfo)
                #logging.info(vinfo)
        picamera_present = os.popen("vcgencmd get_camera").readline()
        picamera_present = picamera_present.replace("supported=", "")
        picamera_present = picamera_present.replace("detected=", "")
        if int(picamera_present[0]) == 1 and int(picamera_present[2]) == 1:
            vinfo = {"device": 'PiCamera', "index": 99, "resolution": [640,480], "time": time.time()}
            video_devices.append(vinfo)
        return video_devices

    def scan_audio_devices(self):
        p = pyaudio.PyAudio()
        audio_devices = []
        num_aout = 0
        num_ain = 0
        for i in range(p.get_device_count()):
            dev = p.get_device_info_by_index(i)
            if dev['maxInputChannels'] > 0:
                #logging.info(dev['name'])
                for mic in SUPPORTED_MIC:
                    if mic in dev['name']:
                        ainfo = {"device": mic, "type": "Input", "index": dev['index'], "time": time.time()}
                        audio_devices.append(ainfo)                        
            else:
                for speaker in SUPPORTED_SPEAKERS:
                    if speaker in dev['name']:
                        ainfo = {"device": speaker, "type": "Output", "index": dev['index'], "time": time.time()}
                        audio_devices.append(ainfo)   
        p.terminate()
        return audio_devices

    def scan_control_devices(self):
        control_devices = []
        for hat in SUPPORTED_CONTROL_HAT:
            if hat == 'BrickPi':
                BP_SPI = spidev.SpiDev()
                BP_SPI.open(0, 1)
                BP_SPI.max_speed_hz = 500000
                BP_SPI.mode = 0b00
                BP_SPI.bits_per_word = 8
                outArray = [1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                try:
                    reply = BP_SPI.xfer2(outArray)
                    name = ""
                    if reply[3] == 0xA5 :
                        
                        for c in range(4, 24):
                            if reply[c] != 0:
                                name += chr(reply[c])
                            else:
                                break
                    if hat in name:
                        cinfo = {"device": hat, "time": time.time()}
                        control_devices.append(cinfo)
                except:
                    pass
                BP_SPI.close()
            #elif hat == 'Adafruit Servo HAT':
        return control_devices

    def update_device_list(self, current_list, new_list):
        num_new_dev = len(new_list)
        for dev in current_list:
            dev_exist = False
            for i in range(num_new_dev):
                if dev['device'] == new_list[i]['device']:
                    dev_exist = True
            if not dev_exist:
                if time.time() - dev['time'] < 5:
                    new_list.append(dev)
        return new_list

    def heartbeat_func(self):
        while True:
            self.usb_devices = self.update_device_list(self.usb_devices, self.scan_usb_devices())
            self.video_devices = self.update_device_list(self.video_devices, self.scan_video_devices())
            self.audio_devices = self.update_device_list(self.audio_devices, self.scan_audio_devices())
            self.control_devices = self.update_device_list(self.control_devices, self.scan_control_devices())
            time.sleep(5)

    def get_usb_devices(self):
        return self.usb_devices

    def is_usb_device_active(self, device_name):
        dev_active = False
        for dev in self.usb_devices:
            if dev['device'] == device_name:
                dev_active = True
        return dev_active

    def get_video_devices(self):
        return self.video_devices

    def is_video_device_active(self, device_name):
        dev_active = False
        for dev in self.video_devices:
            if dev['device'] == device_name:
                dev_active = True
        return dev_active

    def get_audio_devices(self):
        return self.audio_devices

    def is_audio_device_active(self, device_name):
        dev_active = False
        for dev in self.audio_devices:
            if dev['device'] == device_name:
                dev_active = True
        return dev_active

    def get_control_devices(self):
        return self.control_devices
    
    def is_control_device_active(self, device_name):
        dev_active = False
        for dev in self.control_devices:
            if dev['device'] == device_name:
                dev_active = True
        return dev_active
        
    def __init__(self):
        self.usb_devices = []
        self.video_devices = []
        self.audio_devices = []
        self.control_devices = []

        self.heartbeat_thread = threading.Thread(target=self.heartbeat_func, daemon=True)
        self.heartbeat_thread.start()
