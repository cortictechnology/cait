""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""

import paho.mqtt.client as mqtt
import logging
import time
import json
import os
import sys
import ast
import requests
import base64
import threading
import socket
import random

from .cait_core import CAITCore

logging.getLogger().setLevel(logging.WARNING)

caitCore = CAITCore()

startedListen = False
startedTimer = False
startTime = None
onceFunction = []
initializedMotor = False

#### Constants for PID controller ####
KP = 0.75
KD = 0
KI = 0.000001
#### Variables for PID Errors ########
previous_steering_error = 0
previous_2_steering_error = 0
sum_of_steering_errors = 0

responses = {}

not_needed_domains = ["homeassistant", "persistent_notification", 
                      "system_log", "recorder", "cloud", "group", 
                      "scene", "script", "automation", "tts", "notify", 
                      "hue", "sonos", "logbook", "stream"]

cloud_accounts = {}
account_names = []
audio_output_device = "speaker"
current_nlp_model = ""

acc_list = [line.rstrip() for line in open('/opt/accounts')]
for line in acc_list:
    try:
        acc = ast.literal_eval(line)
        account_names.append(acc[0])
        cloud_accounts[acc[0]] = acc[1]
    except:
        pass


def load_responses(path):
    global responses
    for filename in os.listdir(path):
        script = path + "/" + filename
        with open(script, 'r') as f:
            line = f.readline()
            while line.find("##") == -1:
                line = line.readline()
            line = line.rstrip()
            response_topic = line[line.find(":")+1:]
            responses[response_topic] = []
            line = f.readline()
            while line:
                if line.find("##") != -1:
                    line = line.rstrip()
                    response_topic = line[line.find(":")+1:]
                    responses[response_topic] = []
                    line = f.readline()
                elif line.find("-") != -1:
                    line = line.rstrip()
                    responses[response_topic].append(line[line.find("-")+2:])
                    line = f.readline()
                else:
                    line = f.readline()


def get_video_devices():
    return caitCore.get_devices("video")


def get_audio_devices():
    return caitCore.get_devices("audio")


def get_control_devices():
    return caitCore.get_devices("control")


def test_camera(index):
    available_video_devices = caitCore.get_devices("video")
    current_video_device = None
    for dev in available_video_devices:
        if dev['index'] == index:
            current_video_device = dev
    current_video_device["processor"] = "local"
    msg = json.dumps(current_video_device)
    result = caitCore.send_component_commond("vision", "VisionUp " + msg)
    return result


def initialize_vision(processor="local"):
    available_video_devices = caitCore.get_devices("video")
    if len(available_video_devices) == 0:
        return False, "No video device is detected, or connected device is not supported"
    else:
        current_video_device = available_video_devices[0]
    current_vision_processor = caitCore.get_current_processor("vision")
    if processor == "local":
        caitCore.set_current_processor("vision", "local")
    else:
        caitCore.set_current_processor("vision", processor)
    if current_vision_processor != caitCore.get_current_processor("vision"):
        vision_wait = 0
        while caitCore.get_component_state("vision", "Up"):
            if vision_wait <= 100:
                result = caitCore.send_component_commond("vision", "VisionDown")
                if result == False:
                    logging.info("Init Vision: Error occurred")
                    return result, "MQTT Error"
                logging.info("Init Vision: Waiting for Vision to go down")
                vision_wait = vision_wait + 1
                time.sleep(1)
            else:
                logging.info("Init Vision Error: Vision module not responding, please check the module status")
                return False, "Timeout"
    vision_wait = 0
    while not caitCore.get_component_state("vision", "Up"):
        if vision_wait <= 100:
            current_video_device["processor"] = caitCore.get_current_processor("vision")
            msg = json.dumps(current_video_device)
            result = caitCore.send_component_commond("vision", "VisionUp " + msg)
            if result == False:
                logging.info("Init Vision: Error occurred")
                return result, "MQTT Error"
            logging.info("Init Vision: Waiting for Vision to go up")
            vision_wait = vision_wait + 1
            time.sleep(1)
        else:
            logging.info("Init Vision Error: Vision module not responding, please check the module status")
            return False, "Timout"
    return True, "OK"


def deactivate_vision():
    result = caitCore.send_component_commond("vision", "VisionDown")
    if result == False:
        logging.info("Deactivate Vision: Error occurred")
        return result


def get_cloud_accounts():
    #print("+++++++++++++++++++++", cloud_accounts)
    return account_names


def get_nlp_models():
    model_list = []
    for model in os.listdir('/opt/cortic_modules/nlp_module/models'):
        if os.path.isdir('/opt/cortic_modules/nlp_module/models/' + model):
            model_list.append(model)
    return model_list


def initialize_voice(useOnline=False, account="default", language="english"):
    global startedListen
    startedListen = False
    init_wait = 0
    voice_wait = 0
    caitCore.set_component_state("voice", False, state_type="Up")
    caitCore.set_component_state("voice", False, state_type="Init")
    available_audio_devices = caitCore.get_devices("audio")
    num_ain = 0
    num_aout = 0
    ain_devices = []
    for  adev in available_audio_devices:
        if adev["type"] == "Input":
            num_ain = num_ain + 1
            ain_devices.append(adev)
        else:
            num_aout = num_aout + 1
        
        logging.info("Aout: " + str(num_aout))
    if num_ain == 0:
        return False, "No microphone is detected, or connected device is not supported"
    # if num_aout == 0:
    #     return False, "No speaker is detected, or connected device is not supported"
    
    current_ain_device = ain_devices[0]
    #print("--------------------", cloud_accounts)
    while not caitCore.get_component_state("voice", "Init"):
        if init_wait <= 100:
            logging.info("Init Voice: Waiting voice init")
            if not useOnline:
                msg = json.dumps(current_ain_device)
                result = caitCore.send_component_commond("voice", "Offline " + msg)
                if result == False:
                    logging.info("Init Voice: Error occurred")
                    return result, "MQTT Error"
            else:
                #print("******************", cloud_accounts)
                account_json = cloud_accounts[account]
                current_ain_device["account"] = account_json
                current_ain_device["language"] = language
                msg = json.dumps(current_ain_device)
                result = caitCore.send_component_commond("voice", "Online " + msg)
                if result == False:
                    logging.info("Init Voice: Error occurred")
                    return result, "MQTT Error"
            init_wait = init_wait + 1
            time.sleep(1)
        else:
            logging.info("Init Voice Error: Voice module not responding, please check the module status")
            return False,  "Timout"
    while not caitCore.get_component_state("voice", "Up"):
        if voice_wait <= 100:
            logging.info("Init Voice: Waiting voice up")
            voice_wait = voice_wait + 1
            time.sleep(1)
        else:
            logging.info("Init Voice Error: Voice module not responding, please check the module status")
            return False,  "Timout"
    return True, "OK"


def initialize_nlp(mode="english_default"):
    global current_nlp_model
    nlp_wait = 0
    if current_nlp_model != mode:
        caitCore.set_component_state("nlp", False)
        current_nlp_model = mode
    while not caitCore.get_component_state("nlp", "Up"):
        if nlp_wait <= 1000:
            result = caitCore.send_component_commond("nlp", "NLP Up," + mode)
            if result == False:
                logging.info("Init NLP: Error occurred")
                return result
            logging.info("Init NLP: Waiting for NLP up")
            nlp_wait = nlp_wait + 1
            time.sleep(1)
        else:
            logging.info("Init NLP Error: NLP module not responding, please check the module status")
            return False
    
    return True, "OK"


def deactivate_nlp():
    caitCore.send_component_commond("nlp", "Down")


def initialize_control(mode):
    control_wait = 0
    available_control_devices = caitCore.get_devices("control")
    if len(available_control_devices) == 0:
        return False, "No control device is detected, or connected device is not supported"
    while not caitCore.get_component_state("control", "Up"):
        if control_wait <= 100:
            if mode == "ev3":
                hub_address = socket.gethostbyname('ev3dev.local')
                result = caitCore.send_component_commond("control", "Control Up," + hub_address)
            elif mode == "spike":
                hub_address = "/dev/ttyACM0"
                result = caitCore.send_component_commond("control", "Control Up," + hub_address)
            if result == False:
                logging.info("Init Control: Error occurred")
                return result, "MQTT Error"
            logging.info("Init Control: Waiting for control up")
            control_wait = control_wait + 1
            time.sleep(1)
        else:
            logging.info("Init Control Error: Control module not responding, please check the module status")
            return False,  "Timout"
    return True, "OK"


def deactivate_control():
    result = caitCore.send_component_commond("control", "Control Down")
    if result == False:
        logging.info("Deactivate Control: Error occurred")
        return result


def change_module_parameters(parameter_name, value):
    global audio_output_device
    #print("name: ", parameter_name, ", value: ", value)
    if parameter_name == "face recognition confidence":
        result = caitCore.send_component_commond("vision", "set face confidence:" + str(value))
        if result == False:
            logging.info("Change Vision params: Error occurred")
    elif parameter_name == "audio output device":
        audio_output_device = value
    time.sleep(0.1)


def get_camera_image():
    pass


def change_vision_mode(mode):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return
    #print("Send change mode to:", mode)
    result = caitCore.send_component_commond("vision", mode)
    if result == False:
        logging.info("Change Vision Mode: Error occurred")
    caitCore.component_manager.receivedInferenceResult = False


def recognize_face():
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("FaceRecognition")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    if caitCore.component_manager.currentNames[0] != "None":
        #caitCore.newPersonAppear = False
        return caitCore.component_manager.currentNames[0]
    else:
        return "None"


def add_person(name):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("FaceRecognition")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    result = caitCore.send_component_commond("vision", "Add Person:"+name)
    if result == False:
        logging.info("Add Person: Error occurred")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    caitCore.component_manager.currentNames[0] = name
    return True


def remove_person(name):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("FaceRecognition")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    result = caitCore.send_component_commond("vision", "Remove Person:"+name)
    if result == False:
        logging.info("Remove Person: Error occurred")
    print("Removing:", name)
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    caitCore.component_manager.currentNames[0] = "Unknown"
    return True


def get_person_face_location(name):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    if name == caitCore.component_manager.currentNames[0]:
        caitCore.component_manager.receivedInferenceResult = False
        if len(caitCore.component_manager.coordinates) > 0:
            return caitCore.component_manager.coordinates[0]
        else:
            return []
    else:
        caitCore.component_manager.receivedInferenceResult = False
        return []


def identify_image():
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("ObjectClassification")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    if caitCore.component_manager.currentNames[0] != "None":
        caitCore.component_manager.receivedInferenceResult = False
        return caitCore.component_manager.currentNames[0]


def detect_objects():
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("ObjectDetection")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.005)
    if caitCore.component_manager.currentNames[0] != "None":
        caitCore.component_manager.receivedInferenceResult = False
        coordinates = caitCore.component_manager.coordinates
        names = caitCore.component_manager.currentNames
        if caitCore.get_current_processor("vision") != "local":
            width, height = caitCore.component_manager.currentImage.size
            for i in range(len(coordinates)):
                coordinate = coordinates[i]
                coordinate[0] = int(coordinate[0] * width)
                coordinate[1] = int(coordinate[1] * height)
                coordinate[2] = int(coordinate[2] * width)
                coordinate[3] = int(coordinate[3] * height)
        return names, coordinates


def classify_image():
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("ImageClassification")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.005)
    if caitCore.component_manager.currentNames[0] != "None":
        caitCore.component_manager.receivedInferenceResult = False
        names = caitCore.component_manager.currentNames
        return names


def wait_for_person(target):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    while caitCore.component_manager.currentNames[0] != target:
        time.sleep(0.03)
    print("Target appeared")


def execute_while_person_present(target, func, params=None):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    while caitCore.component_manager.currentNames[0] == target:
        if params:
            func(*params)
        else:
            func()
        time.sleep(0.03)
    print("target Left")


def get_person_name_from_speech(entities):
    if not caitCore.get_component_state("voice", "Up"):
        logging.info("Please call initialize_voice() function before using the voice module")
        return None
    name = "my friend"
    for entity in entities:
        if entity['entity'] == 'person':
            name = entity['value']
    return name


def say(message_topic, entities=[]):
    global responses
    global audio_output_device
    message = message_topic
    if audio_output_device != "speaker" and audio_output_device != "ev3":
        return
    if audio_output_device == "speaker":
        if not caitCore.get_component_state("voice", "Up"):
            logging.info("Please call initialize_voice() function before using the voice module")
            return
    elif audio_output_device == "ev3":
        if not caitCore.get_component_state("control", "Up"):
            logging.info("Please call initialize_control() function before using the control module")
            return
    logging.info("say: " + message)
    while not caitCore.component_manager.doneInitRecording:
        #print("Waiting for doneInitRecording")
        time.sleep(0.03)
    while not caitCore.component_manager.startSpeaking:
        if audio_output_device == "speaker":
            result = caitCore.send_component_commond("speak", message)
        elif audio_output_device == "ev3":
            message = "speak," + message
            result = caitCore.send_component_commond("control", message)
        if result == False:
            logging.info("Say: Error occurred")
        time.sleep(0.5)
    caitCore.component_manager.startSpeaking = False
    while not caitCore.component_manager.doneSpeaking:
        time.sleep(0.03)
    caitCore.component_manager.doneSpeaking = False
    return True


def listen():
    global startedListen
    caitCore.component_manager.resetVoice = False
    if not caitCore.get_component_state("voice", "Up"):
        logging.info("Please call initialize_voice() function before using the voice module")
        return
    if not startedListen:
        result = caitCore.send_component_commond("voice", "Start Listen")
        if result == False:
            logging.info("Listen: Error occurred")
        startedListen = True
    start_time = time.time()
    while not caitCore.component_manager.receivedNewSTTMsg:
        #print("Listen sleeping")
        time.sleep(0.03)
        if time.time() - start_time > 50:
            caitCore.component_manager.receivedNewSTTMsg = False
            startedListen = False
            return ""
        if caitCore.component_manager.resetVoice:
            caitCore.component_manager.receivedNewSTTMsg = False
            startedListen = False
            caitCore.component_manager.resetVoice = False
            return ""
    caitCore.component_manager.receivedNewSTTMsg = False
    startedListen = False
    return caitCore.component_manager.currentSTTMsg


def listen_for_wakeword():
    global startedListen
    if not caitCore.get_component_state("voice", "Up"):
        logging.info("Please call initialize_voice() function before using the voice module")
        return
    if not startedListen:
        result = caitCore.send_component_commond("voice", "Start Listen Wakeword")
        if result == False:
            logging.info("Listen Wakeword: Error occurred")
        startedListen = True
    if not caitCore.component_manager.receivedWakeWord:
        return False
    else:
        caitCore.component_manager.receivedWakeWord = False
        startedListen = False
        return True


def analyze(user_message):
    if not caitCore.get_component_state("nlp", "Up"):
        logging.info("Please call initialize_nlp() function before using NLP module")
        return
    print("User Msg:", user_message)
    result = caitCore.send_component_commond("nlp", user_message)
    if result == False:
        logging.info("Analyze: Error occurred")
    while not caitCore.component_manager.receivedNewNLPResponse:
        time.sleep(0.03)
    caitCore.component_manager.receivedNewNLPResponse = False
    nlp_response = json.loads(caitCore.component_manager.currentNLPResponse)
    topic = nlp_response['topic']
    condifence = nlp_response['confidence']
    extracted_entities = nlp_response['entities']
    entities = []
    for entity in extracted_entities:
        entity_entry = {"entity_name" : entity["entity"], "entity_value" : entity["value"]}
        entry_is_uniqued = True
        for e in entities:
            if entity_entry["entity_name"] == e["entity_name"] and entity_entry["entity_value"] == e["entity_value"]:
                entry_is_uniqued = False
        if entry_is_uniqued:
            entities.append(entity_entry)
    return topic, condifence, entities


def control_motor(motor_name, speed, duration):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    command = "move " + motor_name + " " + str(speed) + " " + str(duration)
    logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        time.sleep(0.03)
    return True


def control_motor_speed_group(operation_list):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    command = "motor_speed_group " + operation_list
    logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor Speed Group: Error occurred")
    while not caitCore.component_manager.doneMoving:
        time.sleep(0.03)
    return True


def rotate_motor(motor_name, angle):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    command = "rotate " + motor_name + " " + str(angle)
    logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Rotate Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        time.sleep(0.03)
    return True


def control_motor_degree_group(operation_list):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    command = "motor_degree_group " + operation_list
    logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Rotate Motor Degree Group: Error occurred")
    while not caitCore.component_manager.doneMoving:
        time.sleep(0.03)
    return True

# Deprecated Function
def rotate_to_face(coordinate):
    global previous_steering_error
    global previous_2_steering_error
    global sum_of_steering_errors
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    if coordinate == []:
        print("No face in scene")
    else:
        screenMiddle = 352/2
        fov = 78
        maxMotorAngle = (fov/180) * 360
        middlePoint = int(int(coordinate[0]) + (int(coordinate[2]) - int(coordinate[0]))/2)
        middleOffset = middlePoint - screenMiddle
        steering_error = middleOffset / screenMiddle
        d_steering_error = 1.5 * steering_error - 2 * previous_steering_error + 0.5 * previous_2_steering_error
        previous_2_steering_error = previous_steering_error
        previous_steering_error = steering_error
        sum_of_steering_errors = sum_of_steering_errors + steering_error
        rotational_adjustment = KP * steering_error + KD * d_steering_error + KI * sum_of_steering_errors
        rotatePortion = max(min(rotational_adjustment, 1), -1)
        rotatePosition = int(maxMotorAngle * rotatePortion)
        result = caitCore.send_component_commond("control", str(rotatePosition))
        if result == False:
            logging.info("Rotate To Face: Error occurred")
        print("Command robot to rotate to:", rotatePosition)

# Deprecated Function
def stop_face_tracking():
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return
    result = caitCore.send_component_commond("control", "Init")
    if result == False:
        logging.info("Stop face tracking: Error occurred")


# Deprecated Function
def run_every_x_sec(sec, func, params=None):
    global startedTimer
    global startTime
    if not startedTimer:
        if params:
            func(*params)
        else:
            func()
        startTime = time.time()
        startedTimer = True
    else:
        if time.time() - startTime >= sec:
            if params:
                func(*params)
            else:
                func()
            startTime = time.time()
        #else:
        #    print(time.time() - startTime)

# Deprecated Function
def run_after_x_sec(sec, func, params=None):
    global startedTimer
    global startTime
    if not startedTimer:
        startTime = time.time()
        startedTimer = True
    else:
        if time.time() - startTime >= sec:
            if params:
                func(*params)
            else:
                func()


# Deprecated Function
def run_once(func, id, params=None):
    global onceFunction
    notRunBefore = True
    for function in onceFunction:
        if list(function.keys())[0] == func and function[func] == id:
            notRunBefore = False
    if notRunBefore:
        if params:
            func(*params)
        else:
            func()
        onceFunction.append({func : id})


def get_devices(device_type):
    url = "http://localhost:8123/api/states"
    response = requests.request('GET', url, headers=caitCore.component_manager.headers)
    response_data = response.json()

    device_names = []

    for state in response_data:
        if state['entity_id'].find(device_type+".") != -1:
            detail_url = "http://localhost:8123/api/states/" + state['entity_id']
            detail_response = requests.request('GET', detail_url, headers=caitCore.component_manager.headers).json()
            if (detail_response['state'] != "unavailable"):
                name = state['entity_id'][state['entity_id'].find(".")+1:]
                device_names.append(name)
    return device_names


def control_light(device_name, operation, parameter=None):
    if operation == "turn_on" or operation == "turn_off" or operation == "toggle":
        url = "http://localhost:8123/api/services/light/" + operation
        data = {"entity_id": device_name}
    else:
        if operation == "color_name":
            url = "http://localhost:8123/api/services/light/turn_on"
            data = {"entity_id": device_name, "color_name": parameter}
        elif operation == "brightness_pct":
            url = "http://localhost:8123/api/services/light/turn_on"
            data = {"entity_id": device_name, "brightness_pct": int(parameter)}
    response = requests.request('POST', url, headers=caitCore.component_manager.headers, data=json.dumps(data))
    return response.json()


def control_media_player(device_name, operation):
    url = "http://localhost:8123/api/services/media_player/" + operation
    data = {"entity_id": device_name}
    response = requests.request('POST', url, headers=caitCore.component_manager.headers, data=json.dumps(data))
    return response.json()


if __name__ == "__main__":
    pass
