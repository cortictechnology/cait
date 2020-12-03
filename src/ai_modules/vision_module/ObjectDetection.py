""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from object_detection import ObjectLib
import paho.mqtt.client as mqtt
import logging
import time
import cv2
import io
from PIL import Image
import json
import ast

init_time = time.time()
frame_counter = 0
fps = 0

logging.getLogger().setLevel(logging.INFO)

class ObjectDetection:
    def connectMQTT(self, client):
        try:
            client.connect("127.0.0.1",1883,60)
            logging.info("Connected to broker")
            return 0
        except:
            logging.info("Broker not up yet, retrying...")
            return -1

    def on_connect(self, client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        client.subscribe(self.remoteInferenceChannel)
        logging.info("Subscribed to: " + self.remoteInferenceChannel)

    def on_message(self, client, userdata, msg):
        self.remoteInferenceResult = msg.payload.decode()
        #logging.info("Received result")
        
    def __init__(self, inferenceProcessor="local"):
        self.inferenceProcessor= inferenceProcessor
        self.remoteInferenceChannel = "cait/remoteInferenceResult/" + self.inferenceProcessor
        self.remoteInferenceResult = None
        if self.inferenceProcessor=="local":
            #self.object_detector = ObjectDetector("/vision_module/mbv3_ssdlite.param.bin", "/vision_module/mbv3_ssdlite.bin")
            self.object_detector = ObjectLib()
            #logging.info("Loaded object detector model")
        else:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            ret = self.connectMQTT(self.client)
            while ret != 0:
                time.sleep(1)
                ret = self.connectMQTT(self.client)
            self.client.loop_start()
            #logging.info("Connected to virtual processor")

    def run(self, image):
        global fps
        coordinates = []
        names = ['None']
        result = '{ "mode" : "ObjectDetection", "coordinates": "' + str(coordinates) + '", "names": "' + str(names) + '" }'
        if self.inferenceProcessor=="local":
            objects = self.object_detector.detect_objects(image)    
            if len(objects) == 0:
                return result
            else:
                coordinates = []
                names = []
                for obj in objects:
                    if obj['prob'] > 0.3:
                        coordinates.append([obj['x0'], obj['y0'], obj['x1'], obj['y1']])
                        names.append(obj['name'])
                result = '{ "mode" : "ObjectDetection", "coordinates": "' + str(coordinates) + '", "names": "' + str(names) + '" }'
                return result
        else:
            if self.remoteInferenceResult is not None:
                return self.remoteInferenceResult
            else:
                return result
