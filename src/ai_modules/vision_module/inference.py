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
visionReady = False
addPerson = False
addPersonName = ''
removePerson = False
removePersonName = ''
face_recognition_confidence = 0.7
face_detection_confidence = 0.7
object_detection_confidence = 0.5

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
    global face_detection_confidence
    global object_detection_confidence
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
    elif data.find("set recognition confidence") != -1:
        face_recognition_confidence = float(data[data.find(":")+1:])
    elif data.find("set face detection confidence") != -1:
        face_detection_confidence = float(data[data.find(":")+1:])
    elif data.find("set object detection confidence")!= -1:
        object_detection_confidence = float(data[data.find(":")+1:])
    elif data == "ResetMode":
        currentInferenceMode = ""
    elif data.find("mode:") != -1:
        mode = data[data.find(":")+1:]
        if mode in inferenceMode:
            if currentInferenceMode != mode:
                currentInferenceMode = mode

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
    global visionReady
    global client_heartbeat
    global inferenceProcessor
    global remoteProcessorConnected
    while True:
        if visionUp:
            if inferenceProcessor != "local":
                if remoteProcessorConnected and visionReady:
                    client_heartbeat.publish("cait/module_states", "Vision Up", qos=1)
            else:
                if visionReady:
                    client_heartbeat.publish("cait/module_states", "Vision Up", qos=1)
        else:
            client_heartbeat.publish("cait/module_states", "Vision Down", qos=1)
        time.sleep(1)

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
    global visionReady
    global face_recognition_confidence
    global face_detection_confidence
    global object_detection_confidence

    heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
    heartbeat_thread.start()

    time.sleep(0.1)
    while(True):
        if visionUp:
            try:
                os.system("rmmod uvcvideo")
                os.system("modprobe uvcvideo quirks=128 nodrop=1 timeout=6000")
            except:
                pass
            logging.info("Starting camera")
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
            inferencers[inferenceMode.index("FaceDetection")].detection_threshold = face_detection_confidence
            inferencers[inferenceMode.index("FaceRecognition")].generate_database("/vision_module/database", inferencers[inferenceMode.index("FaceDetection")])
            num_failed_reading_image = 0
            while(camera.isOpened() and visionUp):
                _, img = camera.read()
                if img is not None:
                    visionReady = True
                    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 50]
                    _, buffer = cv2.imencode('.jpg', img, encode_param)

                    imgByteArr = base64.b64encode(buffer)

                    if currentInferenceMode != "":
                        model = inferencers[inferenceMode.index(currentInferenceMode)]
                        if currentInferenceMode == "FaceRecognition" and addPerson and addPersonName != '':
                            face_detection_model = inferencers[inferenceMode.index("FaceDetection")]
                            face_detection_model.detection_threshold = face_detection_confidence
                            detected_faces, largest_face_index = face_detection_model.detect_faces(img)
                            result = model.add_person(addPersonName, img, detected_faces, largest_face_index)
                            addPerson = False
                            addPersonName = ''
                        if currentInferenceMode == "FaceRecognition" and removePersonName != '':
                            _ = model.remove_person(removePersonName)
                            removePerson = False
                            removePersonName = ''
                        if currentInferenceMode == "FaceRecognition":
                            face_detection_model = inferencers[inferenceMode.index("FaceDetection")]
                            face_detection_model.detection_threshold = face_detection_confidence
                            detected_faces, largest_face_index = face_detection_model.detect_faces(img)
                            result = model.run(img, detected_faces, largest_face_index, face_recognition_confidence)
                        else:
                            if currentInferenceMode == "FaceDetection":
                                result = model.run(img, face_detection_confidence)
                            else:
                                result = model.run(img, object_detection_confidence)
                        client_inference.publish("cait/inferenceResult", result, qos=0)
                        client_inference.publish("cait/inferenceFrame", imgByteArr, qos=0)
                    else:
                        client_inference.publish("cait/inferenceFrame", imgByteArr, qos=0)
                else:
                    num_failed_reading_image = num_failed_reading_image + 1
                    if num_failed_reading_image > 10:
                        visionUp = False
                        visionReady = False
                        break
            if camera.isOpened:
               camera.release()
               logging.info("Released Camera")
        time.sleep(0.1)

if __name__ == '__main__':
  main()
