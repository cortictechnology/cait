""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, April 2020

"""

import paho.mqtt.client as mqtt
import logging
import time
import threading
from PIL import Image, ImageTk, ImageDraw, ImageFont
import io
from io import StringIO, BytesIO
import base64
import json
import ast

logging.getLogger().setLevel(logging.INFO)

class ComponentManager:
    def on_connect_module_states(self, client, userdata, flags, rc):
        logging.info("Module states client Connected with result code "+str(rc))
        client.subscribe("cait/module_states")

    def on_message_module_states(self, client, userdata, msg):
        data = msg.payload.decode()
        #logging.info("Module state:" + data)
        if data == "Vision Up":
            self.visionUp = True
        elif data == "Vision Down":
            self.visionUp = False
        elif data == "STT Init Done":
            self.voiceInit = True
        elif data == "Voice Up":
            if self.voiceInit:
                self.voiceUp = True
        elif data.find("Voice Exception") != -1:
            self.voiceException = True
            self.voiceExceptionMsg = data[data.find(": ") + 2:]
        elif data == "Init recording":
            self.doneInitRecording = False
        elif data == "Init recording done":
            self.doneInitRecording = True
        elif data == "WAKEWORD":
            self.receivedWakeWord = True
        elif data == "Start Speaking":
            self.startSpeaking = True
        elif data == "Done Speaking":
            self.doneSpeaking = True
        elif data == "NLP Up":
            self.nlpUp = True
        elif data == "Control Up":
            self.controlUp = True
        elif data == "Control Done":
            self.doneMoving = True  
        elif data.find("Control Exception") != -1:
            self.controlException = True
            self.controlExceptionMsg = data[data.find(": ") + 2:]
        elif data == "Reset":
            logging.info("Resetting")
            self.resetVision = True
            self.resetVoice = True
            self.resetControl = True
            self.resetNLP = True
            self.resetHome = True

    def on_connect_inference(self, client, userdata, flags, rc):
        logging.info("Connected with result code "+str(rc))
        VISION_TOPIC = [("cait/inferenceResult",1)]
        client.subscribe(VISION_TOPIC)

    def on_message_inference(self, client, userdata, msg):
        message = msg.payload.decode()
        result = json.loads(message)
        if result['mode'] == "FaceRecognition":
            if result['name'] != "None":
                self.currentNames = [result['name']]
                self.largest_index = int(result['largestID'])
                #self.coordinates = [result['coordinate'][1:-1].split(', ')]
                self.coordinates = ast.literal_eval(result['coordinates'])
            else:
                self.currentNames = ["None"]
                self.largest_index = -1
                self.coordinates = []
        elif result['mode'] == "ObjectDetection":
            self.coordinates = ast.literal_eval(result['coordinates'])
            self.currentNames = ast.literal_eval(result['names'])
            self.largest_index = -1
        elif result['mode'] == "ImageClassification":
            self.currentNames = ast.literal_eval(result['names'])
            self.largest_index = -1
            self.no_bounding_box = True
            self.coordinates = []

        self.receivedInferenceResult = True
        self.resultOverlayed = False

    def updateSelfImage(self, image):
        self.currentImage = image
        encodedImage = BytesIO()
        self.currentImage.save(encodedImage, "JPEG")
        contents = base64.b64encode(encodedImage.getvalue()).decode()
        encodedImage.close()
        contents = contents.split('\n')[0]
        self.client_frame.publish("cait/displayFrame", contents, qos=0)

    def on_connect_frame(self, client, userdata, flags, rc):
        logging.info("Frame client Connected with result code "+str(rc))
        client.subscribe("cait/inferenceFrame")

    def on_message_frame(self, client, userdata, msg):
        image_data = msg.payload
        #logging.info(image_data)
        imgdata = base64.b64decode(image_data)
        image = Image.open(io.BytesIO(imgdata))
        width, height = image.size
        if image:
            self.frame_counter = self.frame_counter + 1
            timeInterval = time.time() - self.init_time
            if timeInterval >= 1:
                #logging.info("1 sec reached")
                self.fps = int(self.frame_counter/timeInterval)
                #logging.info("Result FPS: " + str(self.fps))
                self.frame_counter = 0
                self.init_time = time.time()
            #logging.info("Done check time interval")
            draw = ImageDraw.Draw(image)
            #logging.info("Ready to load font")
            font = ImageFont.truetype('/opt/cortic_modules/cait/managers/NotoSansCJKtc-Regular.ttf', int(0.05*width))
            #logging.info("done loading font")
            #logging.info("done drawing")
            if not self.resultOverlayed:
                if len(self.coordinates) > 0:
                    for i in range(len(self.coordinates)):
                        coordinate = self.coordinates[i]
                        if self.visionProcessor != "local":
                            coordinate[0] = int(coordinate[0] * width)
                            coordinate[1] = int(coordinate[1] * height)
                            coordinate[2] = int(coordinate[2] * width)
                            coordinate[3] = int(coordinate[3] * height)
                        else:
                            coordinate[0] = int(coordinate[0])
                            coordinate[1] = int(coordinate[1])
                            coordinate[2] = int(coordinate[2])
                            coordinate[3] = int(coordinate[3])
                        if self.largest_index != -1:
                            if i == self.largest_index:
                                draw.rectangle(coordinate, outline='green', width=int(0.0046875*width))
                                draw.text((coordinate[0]-1, coordinate[1]-30-1), self.currentNames[0], fill=(0,0,0), font=font)
                                draw.text((coordinate[0], coordinate[1]-30), self.currentNames[0], fill=(255,255,255), font=font)
                                
                            else:
                                draw.rectangle(coordinate, outline='red', width=int(0.0046875*width))
                        else:
                            draw.rectangle(coordinate, outline='blue', width=int(0.0046875*width))
                            draw.text((coordinate[0]+10-1, coordinate[1]+10-1), self.currentNames[i], fill=(0,0,0), font=font)
                            draw.text((coordinate[0]+10, coordinate[1]+10), self.currentNames[i], fill=(255,255,255), font=font)
                            
                    #print("Done drawing text")
                    self.resultOverlayed = True
                else:
                    if self.no_bounding_box:
                        for i in range(5):
                            text = "{:.1f}".format(self.currentNames[i][1] * 100) + "% - " + self.currentNames[i][0]
                            draw.text((9, 20*i-1), text, fill=(0,0,0), font=font)
                            draw.text((10, 20*i), text, fill=(255,255,255), font=font)
                        self.no_bounding_box = False
                    self.resultOverlayed = True

            #logging.info("updating image")
            self.updateSelfImage(image)
    
    def on_connect_stt(self, client, userdata, flags, rc):
        logging.info("Connected with result code "+str(rc))
        client.subscribe("cait/sttData")

    def on_message_stt(self, client, userdata, msg):
        data = msg.payload.decode()
        logging.info("stt Data: " + data + ", qos: " + str(msg.qos) + ", retain: " + str(msg.retain))
        self.receivedNewSTTMsg = True
        self.currentSTTMsg = data
        logging.info("Done receving stt message")

    def on_connect_nlp(self, client, userdata, flags, rc):
        logging.info("NLP client connected with result code "+str(rc))
        client.subscribe("cait/nlpResponse")

    def on_message_nlp(self, client, userdata, msg):
        data = msg.payload.decode()
        logging.info("NLP result: " + data)
        self.receivedNewNLPResponse = True
        self.currentNLPResponse = data

    def connectMQTT(self, client):
        try:
            client.connect("127.0.0.1",1883,60)
            logging.info("Connected to broker")
            return 0
        except:
            logging.info("Broker not up yet, retrying...")
            return -1

    def send_vision_command(self, command):
        self.client_module_state.publish("cait/vision_control", command)
        return True

    def send_voice_command(self, command, text_to_speech=False):
        if text_to_speech:
            self.client_stt.publish("cait/ttsInput", command)
        else:
            self.client_module_state.publish("cait/voice_control", command)
        return True

    def send_nlp_command(self, command):
        self.client_nlp.publish("cait/userMsg", command, qos=1)
        return True

    def send_control_command(self, command):
        self.client_module_state.publish("cait/motor_control", command, qos=1)
        return True

    def __init__(self):
        self.visionUp = False
        self.visionProcessor = "local"
        self.voiceProcessor = "local"
        self.nlpProcessor = "local"
        self.resultOverlayed = False
        self.object_confidence_threshold = 0.2
        self.currentNames = ["None"]
        self.coordinates = []
        self.receivedInferenceResult = False
        self.currentImage = Image.new('RGB', (400, 300))
        self.frame_counter = 0
        self.init_time = time.time()
        self.fps = 0
        self.largest_index = -1
        self.no_bounding_box = False

        self.receivedNewSTTMsg = False
        self.currentSTTMsg = ""

        self.receivedWakeWord = False
        self.startSpeaking = False
        self.doneSpeaking = False
        self.doneInitRecording = True
        self.voiceInit = False
        self.voiceUp = False
        self.voiceException = False
        self.voiceExceptionMsg = ""
        
        self.nlpUp = False
        self.receivedNewNLPResponse = False
        self.currentNLPResponse = ""

        self.controlUp = False
        self.doneMoving = True
        self.controlException = False
        self.controlExceptionMsg = ""

        self.token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjZGFhZGYwNTM5ZDM0NGUwYWNmNmMxNzk2MTMzMTQwOCIsImlhdCI6MTU4MjI2MjgyNywiZXhwIjoxODk3NjIyODI3fQ.8eixv03gAqgx-Mw3BZQmjuewDfStdDqzdHMzqt2JXbo'
        self.authorization = 'Bearer ' + self.token
        self.headers = {
            'Authorization': self.authorization,
            'content-type': 'application/json',
            }

        self.resetVision = False
        self.resetVoice = False
        self.resetControl = False
        self.resetNLP = False
        self.resetHome = False
            
        self.client_module_state = mqtt.Client()
        self.client_module_state.on_connect = self.on_connect_module_states
        self.client_module_state.on_message = self.on_message_module_states
        ret = self.connectMQTT(self.client_module_state)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client_module_state)
        self.client_module_state.loop_start()

        self.client_inference = mqtt.Client()
        self.client_inference.on_connect = self.on_connect_inference
        self.client_inference.on_message = self.on_message_inference
        ret = self.connectMQTT(self.client_inference)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client_inference)
        self.client_inference.loop_start()

        self.client_frame = mqtt.Client()
        self.client_frame.on_connect = self.on_connect_frame
        self.client_frame.on_message = self.on_message_frame
        ret = self.connectMQTT(self.client_frame)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client_frame)
        self.client_frame.loop_start()

        self.client_stt = mqtt.Client()
        self.client_stt.on_connect = self.on_connect_stt
        self.client_stt.on_message = self.on_message_stt
        ret = self.connectMQTT(self.client_stt)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client_stt)
        self.client_stt.loop_start()
        
        self.client_nlp = mqtt.Client()
        self.client_nlp.on_connect = self.on_connect_nlp
        self.client_nlp.on_message = self.on_message_nlp
        ret = self.connectMQTT(self.client_nlp)
        while ret != 0:
            time.sleep(1)
            ret = self.connectMQTT(self.client_nlp)
        self.client_nlp.loop_start()