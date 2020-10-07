""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2020

"""

import paho.mqtt.client as mqtt
import logging
import time
import threading

logging.getLogger().setLevel(logging.INFO)

class OffloadingDeviceManager:
    def on_connect(self, client, userdata, flags, rc):
        logging.info("Offloading Device Manager connected with result code "+str(rc))
        client.subscribe("cait/offloading_device_states")
    
    def on_message(self, client, userdata, msg):
        data = msg.payload.decode()
        if data.find("Offloading") != -1:
            processor_type = data[data.find("Offloading")+11:data.find(" ")]
            processor_name = data[data.find("DeviceName")+11:]
            if processor_type in self.virtualProcessors.keys():
                existing_processors = self.virtualProcessors[processor_type]
                processor_exist = False
                for processor in existing_processors:
                    if processor['processor_name'] == processor_name:
                        processor_exist = True
                        processor['time'] = time.time()
                        break
                if not processor_exist:
                    processor_info = {"processor_name": processor_name, "time": time.time()}
                    self.virtualProcessors[processor_type].append(processor_info)
            else:
                processor_info = {"processor_name": processor_name, "time": time.time()}
                self.virtualProcessors[processor_type] = [processor_info]      
        
    def connectMQTT(self, client):
        try:
            client.connect("127.0.0.1",1883,60)
            return 0
        except:
            logging.info("Broker not up yet, retrying...")
            return -1
    
    def heartbeat_func(self):
        while True:
            current_time = time.time()
            for processor_type in self.virtualProcessors:
                updated_processor_list = []
                for processor in self.virtualProcessors[processor_type]:
                    if current_time - processor['time'] < 5:
                        updated_processor_list.append(processor)
                self.virtualProcessors[processor_type] = updated_processor_list
            time.sleep(3)

    def get_virtual_processors(self):
        return self.virtualProcessors

    def is_virtual_processor_active(self, processor_type, processor_name):
        processor_active = True
        for processors in self.virtualProcessors[processor_type]:
            if processors["processor_name"] == processor_name:
                processor_active = True
        return processor_active

    def __init__(self):
        self.virtualProcessors = {}

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        ret = self.connectMQTT(self.client)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client)
        self.client.loop_start()

        self.heartbeat_thread = threading.Thread(target=self.heartbeat_func, daemon=True)
        self.heartbeat_thread.start()