""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2020

"""

import logging
import time
from socket import *
import threading
import os

from .managers.device_manager import DeviceManager
from .managers.component_manager import ComponentManager
from .managers.offloading_device_manager import OffloadingDeviceManager

logging.getLogger().setLevel(logging.INFO)

class CAITCore:
    def heartbeat_func(self):
        s = socket(AF_INET, SOCK_DGRAM)
        s.bind(('', 0))
        s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
        while True:
            self.component_manager.client_module_state.publish("cait/system_status", "CAIT UP")
            network_discovert_str = "CAIT instance:" + os.uname()[1]
            try:
                s.sendto(network_discovert_str.encode(), ('255.255.255.255', 50000))
            except:
                print("Network error, retry in 2 seconds")
            time.sleep(2)

    def __init__(self):
        self.device_manager = DeviceManager()
        self.component_manager = ComponentManager()
        self.offloading_device_manager = OffloadingDeviceManager()

        self.heartbeat_thread = threading.Thread(target=self.heartbeat_func, daemon=True)
        self.heartbeat_thread.start()

    def get_devices(self, device_type):
        if device_type == "usb":
            return self.device_manager.get_usb_devices()
        elif device_type == "video":
            return self.device_manager.get_video_devices()
        elif device_type == "audio":
            return self.device_manager.get_audio_devices()
        elif device_type == "control":
            return self.device_manager.get_control_devices()
        else:
            return []

    def is_device_active(self, device_type, device_name):
        if device_type == "usb":
            return self.device_manager.is_usb_device_active(device_name)
        elif device_type == "video":
            return self.device_manager.is_video_device_active(device_name)
        elif device_type == "audio":
            return self.device_manager.is_audio_device_active(device_name)
        elif device_type == "control":
            return self.device_manager.is_control_device_active(device_name)
        else:
            return None

    def get_offloading_devices(self):
        return self.offloading_device_manager.get_virtual_processors()

    def is_offloading_device_active(self,device_type, device_name):
        return self.offloading_device_manager.is_virtual_processor_active(device_type, device_name)

    def get_current_processor(self, processor_type):
        if processor_type == "vision":
            return self.component_manager.visionProcessor
        elif processor_type == "voice":
            return self.component_manager.voiceProcessor
        elif processor_type == "nlp":
            return self.component_manager.nlpProcessor
        else:
            return None

    def set_current_processor(self, processor_type, processor_name):
        if processor_type == "vision":
            self.component_manager.visionProcessor = processor_name
        elif processor_type == "voice":
            self.component_manager.voiceProcessor = processor_name
        elif processor_type == "nlp":
            self.component_manager.nlpProcessor = processor_name

    def get_component_state(self, component_name, state_type="Up"):
        if component_name == "vision":
            return self.component_manager.visionUp
        elif component_name == "voice":
            if state_type == "Up":
                return self.component_manager.voiceUp
            elif state_type == "Init":
                return self.component_manager.voiceInit
        elif component_name == "nlp":
            return self.component_manager.nlpUp
        elif component_name == "control":
            return self.component_manager.controlUp
        else:
            return None
    
    def set_component_state(self, component_name, value, state_type="Up"):
        if component_name == "vision":
            self.component_manager.visionUp = value
        elif component_name == "voice":
            if state_type == "Up":
                self.component_manager.voiceUp = value
            elif state_type == "Init":
                self.component_manager.voiceInit = value
        elif component_name == "nlp":
            self.component_manager.nlpUp = value
        elif component_name == "control":
            self.component_manager.controlUp = value


    def send_component_commond(self, component_name, command):
        if component_name == "vision":
            return self.component_manager.send_vision_command(command)
        elif component_name == "speak":
            return self.component_manager.send_voice_command(command, text_to_speech=True)
        elif component_name == "voice":
            return self.component_manager.send_voice_command(command)
        elif component_name == "nlp":
            return self.component_manager.send_nlp_command(command)
        elif component_name == "control":
            return self.component_manager.send_control_command(command)
        elif component_name == "system_state":
            self.component_manager.client_module_state.publish("cait/system_status", command)
            return True
        else:
            return False