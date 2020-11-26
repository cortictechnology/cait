""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

import time
import paho.mqtt.client as mqtt
import logging
import json
import cv2
from PIL import Image
import io
import base64
import threading
from threading import Thread
import re
import os
from picamera.array import PiRGBArray
from picamera import PiCamera

logging.getLogger().setLevel(logging.INFO)

inferenceMode = []

video_idx = -1
video_width = 0
video_height = 0
inferenceProcessor = "local"
remoteProcessorConnected = False
visionUp = False
addPerson = False
addPersonName = ''
removePerson = False
removePersonName = ''
face_recognition_confidence = 0.7

class WebcamVideoStream:
    def __init__(self, src=0, cap_width=640, cap_height=480):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, cap_width)
        self.stream.set(4, cap_height)
        self.grabbed, self.frame = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False

    def start(self):
        # start the thread to read frames from the video stream
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True

with open('/vision_module/modes.json') as json_file:
        data = json.load(json_file)
        for item in data['InferenceMode']:
            inferenceMode.append(item)

currentInferenceMode = ""

inferencers = []

def connectMQTT(client):
    try:
        client.connect("127.0.0.1",1883,60)
        logging.info("Connected to broker")
        return 0
    except:
        logging.info("Broker not up yet, retrying...")
        return -1

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cait/vision_control")
    client.publish("cait/module_states", "Vision Connected", qos=1)

def on_message(client, userdata, msg):
    global visionUp
    global video_idx
    global video_width
    global video_height
    global inferenceProcessor
    global currentInferenceMode
    global remoteProcessorConnected
    global addPerson
    global removePerson
    global addPersonName
    global removePersonName
    global face_recognition_confidence
    data = msg.payload.decode()
    logging.info("Vision Control: " + data)
    if data.find("VisionUp") != -1 and not visionUp:
        video_device = json.loads(data[data.find(" ")+1:])
        video_idx = int(video_device["index"])
        video_width = int(video_device["resolution"][0])
        video_height = int(video_device["resolution"][1])
        processor = video_device["processor"]
        logging.info("Using Processor: " + processor)
        inferenceProcessor = processor
        visionUp = True
    elif data == "VisionDown" and visionUp:
        visionUp = False
        remoteProcessorConnected = False
    elif data == "Remote Processor Connected":
        remoteProcessorConnected = True
    elif data.find("Add Person") != -1:
        addPerson = True
        addPersonName = data[data.find(":")+1:]
    elif data.find("Remove Person") != -1:
        removePerson = True
        removePersonName = data[data.find(":")+1:]
    elif data.find("set face confidence") != -1:
        face_recognition_confidence = float(data[data.find(":")+1:])
    elif data == "ResetMode":
        currentInferenceMode = ""
    elif data in inferenceMode:
        if currentInferenceMode != data:
            currentInferenceMode = data

client_heartbeat = mqtt.Client()
ret = connectMQTT(client_heartbeat)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_heartbeat)
client_heartbeat.loop_start()

client_inference = mqtt.Client()
client_inference.on_connect = on_connect
client_inference.on_message = on_message
ret = connectMQTT(client_inference)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_inference)
client_inference.loop_start()

def heartbeat_func():
    global visionUp
    global client_heartbeat
    global inferenceProcessor
    global remoteProcessorConnected
    while True:
        if visionUp:
            if inferenceProcessor != "local":
                if remoteProcessorConnected:
                    client_heartbeat.publish("cait/module_states", "Vision Up", qos=1)
            else:
                client_heartbeat.publish("cait/module_states", "Vision Up", qos=1)
        else:
            client_heartbeat.publish("cait/module_states", "Vision Down", qos=1)
        time.sleep(1)

# init_time = time()
# frame_counter = 0
def main():    
    global video_idx
    global video_height
    global video_width
    global inferenceProcessor
    global remoteProcessorConnected
    global inferencers
    global addPerson
    global removePerson
    global addPersonName
    global removePersonName
    global visionUp
    global face_recognition_confidence

    heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
    heartbeat_thread.start()

    #im = cv2.imread('/vision_module/test.jpg')
    time.sleep(0.1)
    while(True):
        if visionUp:
            try:
                os.system("rmmod uvcvideo")
                os.system("modprobe uvcvideo quirks=128 nodrop=1 timeout=6000")
            except:
                pass
            logging.info("Starting camera")
            if video_idx == 99:
                camera = PiCamera()
                camera.resolution = (video_width, video_height)
                camera.framerate = 30
                rawCapture = PiRGBArray(camera, size=(video_width, video_height))
            else:
                camera = cv2.VideoCapture(video_idx)
                camera.set(3,video_width)
                camera.set(4, video_height)
            processor = re.sub(r'[^\w]', '', inferenceProcessor)
            if processor != "local":
                remoteHandshakeMsg = inferenceProcessor + ":" + "cait/remoteInferenceResult/" + processor
                logging.info("Handshake Msg: " + remoteHandshakeMsg)
                while not remoteProcessorConnected:
                    client_inference.publish("cait/offloadResponse", remoteHandshakeMsg, qos=1)
                    logging.info("Published handshakMsg ")
                    time.sleep(1)
            inferencers = []
            for mode in inferenceMode:
                inferenceModule = __import__(mode)
                inferenceClass = getattr(inferenceModule, mode)
                inferencer = inferenceClass(processor)
                inferencers.append(inferencer)
            #logging.info("Camera opened? " + str(camera.isOpened()))
            num_failed_reading_image = 0
            while(camera.isOpened() and visionUp):
            #while visionUp:
            #for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                #if not visionUp:
                    #break
                #img = frame.array
                _, img = camera.read()
                if img is not None:
                    #img_ = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) 
                    #logging.info("Raw frame colour coversion Time: " + str(time.time() - start_time))
                    #start_time = time.time()
                    #im_pil = Image.fromarray(img_)
                    #imgByteArr = io.BytesIO()
                    #im_pil.save(imgByteArr, format='JPEG')
                    #imgByteArr = imgByteArr.getvalue()
                    #start_time = time.time()
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    _, buffer = cv2.imencode('.jpg', img, encode_param)
                    #logging.info("imencode time: " + str(time.time() - start_time))
                    #start_time = time.time()
                    imgByteArr = base64.b64encode(buffer)
                    #imgByteArr = imgByteArr.split('\n')[0]
                    #logging.info("base64 encode time: " + str(time.time() - start_time))
                    #client_inference.publish("cait/rawFrame", imgByteArr, qos=0)
                    #logging.info("Raw frame jpegTime: " + str(time.time() - start_time))
                    if currentInferenceMode != "":
                        model = inferencers[inferenceMode.index(currentInferenceMode)]
                        if currentInferenceMode == "FaceRecognition" and addPerson and addPersonName != '':
                            result = model.add_person(addPersonName, img)
                            addPerson = False
                            addPersonName = ''
                        if currentInferenceMode == "FaceRecognition" and removePersonName != '':
                            _ = model.remove_person(removePersonName)
                            removePerson = False
                            removePersonName = ''
                        if currentInferenceMode == "FaceRecognition":
                            result = model.run(img, face_recognition_confidence)
                        else:
                            result = model.run(img)
                        client_inference.publish("cait/inferenceResult", result, qos=0)
                        client_inference.publish("cait/inferenceFrame", imgByteArr, qos=0)
                    else:
                        client_inference.publish("cait/inferenceFrame", imgByteArr, qos=0)
                    #logging.info("Frame Processing FPS: " + str(1.0/(time.time() - start_time)))
                else:
                    num_failed_reading_image = num_failed_reading_image + 1
                    if num_failed_reading_image > 10:
                        visionUp = False
                        break
                #rawCapture.truncate(0)
            if camera.isOpened:
               camera.release()
               logging.info("Released Camera")
            #camera.close()
        time.sleep(0.1)

if __name__ == '__main__':
  main()
