""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""
import sys
sys.path.insert(0, '/home/pi/CAIT_CURT/curt/src')
from curt.command import CURTCommands
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
import numpy as np
import cv2
from .managers.device_manager import DeviceManager

device_manager = DeviceManager()

logging.getLogger().setLevel(logging.INFO)

CURTCommands.connect_to("0.0.0.0")

startedListen = False
startedTimer = False
startTime = None
onceFunction = []
initializedMotor = False

not_needed_domains = ["homeassistant", "persistent_notification", 
                      "system_log", "recorder", "cloud", "group", 
                      "scene", "script", "automation", "tts", "notify", 
                      "hue", "sonos", "logbook", "stream"]

COLOR = [(0, 153, 0), (234, 187, 105), (175, 119, 212), (80, 190, 168), (0, 0, 255)]

cloud_accounts = {}
account_names = []
current_nlp_model = ""

vision_mode = ""
voice_mode = "offline"

oakd_nodes = {}

vision_initialized = False
voice_initialized = False
nlp_initialized = False
control_initialized = False
smarthome_initialized = False

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJjZGFhZGYwNTM5ZDM0NGUwYWNmNmMxNzk2MTMzMTQwOCIsImlhdCI6MTU4MjI2MjgyNywiZXhwIjoxODk3NjIyODI3fQ.8eixv03gAqgx-Mw3BZQmjuewDfStdDqzdHMzqt2JXbo'
authorization = 'Bearer ' + token
headers = {
    'Authorization': authorization,
    'content-type': 'application/json',
    }

acc_list = [line.rstrip() for line in open('/opt/accounts')]
for line in acc_list:
    try:
        acc = ast.literal_eval(line)
        account_names.append(acc[0])
        cloud_accounts[acc[0]] = acc[1]
    except:
        pass

ft = cv2.freetype.createFreeType2()
ft.loadFontData(fontFileName='/home/pi/CAIT_CURT/HelveticaNeue.ttf', id=0)

stream_thread = None

def connect_mqtt(client, address):
    try:
        client.connect(address, 1883, 60)
        logging.info("Connected to broker")
        client.loop_start()
        return True
    except:
        logging.info("Broker: (" + address + ") not up yet, retrying...")
        return False

streaming_channel = "cait/output/" + os.uname()[1].lower() + "/displayFrame"
streaming_client = mqtt.Client()
ret = connect_mqtt(streaming_client, '0.0.0.0')
while ret != True:
    time.sleep(1)
    ret = connect_mqtt(treaming_client, '0.0.0.0')


def decode_image_byte(image_data):
    jpg_original = base64.b64decode(image_data)
    jpg_as_np = np.frombuffer(jpg_original, dtype=np.uint8)
    image = cv2.imdecode(jpg_as_np, flags=1)
    return image

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
    all_vision_input = CURTCommands.get_vision_input_services()
    camera_workers = []
    for vision_input in all_vision_input:
        if vision_input.name == "webcam":
            camera_workers.append(vision_input)
    return camera_workers


def get_oakd_devices():
    all_vision_input = CURTCommands.get_oakd_services()
    camera_workers = []
    for vision_input in all_vision_input:
        if vision_input.name == "oakd_pipeline":
            camera_workers.append(vision_input)
    return camera_workers


def get_audio_devices():
    voice_inputs = []
    all_voice_input_services = CURTCommands.get_voice_input_services()
    for voice_input in all_voice_input_services:
        if voice_input.name == "respeaker_input":
            voice_inputs.append(voice_input)
    return voice_inputs


def get_voice_processing_services():
    online_voice_processing = []
    all_voice_processing_services = CURTCommands.get_voice_processing_services()
    for voice_processing in all_voice_processing_services:
        if voice_processing.name == "online_voice_processing":
            online_voice_processing.append(voice_processing)
    return online_voice_processing


def get_voice_generation_services(online=True):
    online_voice_generation = []
    all_voice_generation_services = CURTCommands.get_voice_generation_services()
    for voice_generation in all_voice_generation_services:
        if online:
            if voice_generation.name == "online_voice_generation":
                online_voice_generation.append(voice_generation)
        else:
            if voice_generation.name == "offline_voice_generation":
                online_voice_generation.append(voice_generation)
    return online_voice_generation


def get_control_devices():
    control_devices = device_manager.get_control_devices()
    connected_devices = []
    for device in control_devices:
        if device['connected']:
            if device["device"] == "EV3":
                connected_devices.append(device["device"] + ": " + device['ip_addr'])
            else:
                connected_devices.append(device["device"] + ": " + device['mac_addr'])
    return control_devices


def test_camera(index):
#     available_video_devices = caitCore.get_devices("video")
#     current_video_device = None
#     for dev in available_video_devices:
#         logging.warning(str(dev))
#         if int(dev['index']) == index:
#             current_video_device = dev
#     current_video_device["processor"] = "local"
#     msg = json.dumps(current_video_device)
#     result = caitCore.send_component_commond("vision", "VisionUp " + msg)
#     return result
    pass


def initialize_vision(processor="local", mode=[]):
    global oakd_nodes
    global vision_initialized
    global stream_thread
    if vision_initialized:
        vision_initialized = False
        if stream_thread is not None:
            stream_thread.join()
    if processor == "oakd":
        available_video_devices = get_oakd_devices()
    else:
        available_video_devices = get_video_devices()
    if len(available_video_devices) == 0:
        return False, "No video device is detected, or connected device is not supported"
    else:
        current_video_device = available_video_devices[0]
    if processor == "oakd":
        for node in mode:
            if node[0] == "add_rgb_cam_node":
                oakd_nodes['rgb_frame'] = node[1]
            elif node[0] == "add_rgb_cam_preview_node":
                oakd_nodes['rgb_frame'] = node[1]
            elif node[0] == "add_stereo_frame_node":
                oakd_nodes['stereo_frame'] = node[1]
            elif node[0] == "add_spatial_mobilenetSSD_node":
                oakd_nodes['rgb_passthrough_frame'] = node[1] + "_preview"
                if node[-1] == "Face Detection":
                    oakd_nodes['face_detection'] = node[1] + "_detections"
                else:
                    oakd_nodes['object_detection'] = node[1] + "_detections"
            elif node[0] == "add_nn_node":
                if node[-1] == "Face Landmarks":
                    oakd_nodes['face_landmarks'] = node[1]
                elif node[-1] == "Face Features":
                    oakd_nodes['face_features'] = node[1]
                elif node[-1] == "Face Emotions":
                    oakd_nodes['face_emotions'] = node[1]
            
        CURTCommands.config_worker(current_video_device, mode)
    else:
        CURTCommands.config_worker(current_video_device, {"camera_index": 0, 
                                                          "capture_width": 640, 
                                                          "capture_height": 480})
    time.sleep(10)
    vision_initialized = True
    stream_thread = threading.Thread(target=streaming_func, daemon=True)
    stream_thread.start()
    return True, "OK"
    

def deactivate_vision():
    global vision_initialized
    global vision_mode
    # result = caitCore.send_component_commond("vision", "VisionDown")
    # result = caitCore.send_component_commond("vision", "ResetMode")
    # if result == False:
    #     logging.info("Deactivate Vision: Error occurred")
    # return result
    vision_initialized = False
    vision_mode = ""
    return True


def get_cloud_accounts():
    #print("+++++++++++++++++++++", cloud_accounts)
    return account_names


def get_nlp_models():
    model_list = []
    # for model in os.listdir('/opt/cortic_modules/nlp_module/models'):
    #     if os.path.isdir('/opt/cortic_modules/nlp_module/models/' + model):
    #         model_list.append(model)
    return model_list


def initialize_voice(mode="online", account="default", language="english"):
    global voice_initialized
    global voice_mode
    if language == "english":
        processing_language = "en-UK"
        generation_language = "en"
        generation_accents = "ca"
    elif language == "french":
        processing_language = "fr-FR"
        generation_language = "fr"
        generation_accents = ""
    elif language == "chinese":
        processing_language = "zh-CN"
        generation_language = "zh"
        generation_accents = ""
    voice_input_workers = get_audio_devices()
    voice_processing_workers = get_voice_processing_services()
    if mode == "online":
        voice_mode = "online"
        voice_generation_workers = get_voice_generation_services(online=True)
    else:
        voice_mode = "offline"
        voice_generation_workers = get_voice_generation_services(online=False)
    if len(voice_input_workers) == 0:
        return False, "No audio deveice is detected, or connected device is not supported"
    if len(voice_processing_workers) == 0:
        return False, "No voice processing service is detected, or connected device is not supported"
    if len(voice_generation_workers) == 0:
        return False, "No voice generation is detected, or connected device is not supported"
    CURTCommands.config_worker(voice_input_workers[0], {'audio_in_index': 0})
    time.sleep(0.5)
    CURTCommands.start_voice_recording(voice_input_workers[0])
    account_file = cloud_accounts[account]
    with open("/home/pi/CAIT_CURT/" + account_file) as f:
        account_info = json.load(f)
    CURTCommands.config_worker(voice_processing_workers[0], {'account_crediential': account_info,
                                                             'language': processing_language,
                                                             'sample_rate': 16000,
                                                             'channel_count': 4})
    if mode == "online":
        CURTCommands.config_worker(voice_generation_workers[0], {'language': generation_language,
                                                                'accents': generation_accents})
    time.sleep(1)
    voice_initialized = True
    return True, "OK"


def deactivate_voice():
    global voice_initialized
    # result = caitCore.send_component_commond("voice", "VoiceDown")
    # if result == False:
    #     logging.info("Deactivate Voice: Error occurred")
    # return result
    voice_initialized = False
    return True


def initialize_nlp(mode="english_default"):
    # global current_nlp_model
    # nlp_wait = 0
    # if current_nlp_model != mode:
    #     caitCore.set_component_state("nlp", False)
    #     current_nlp_model = mode
    # while not caitCore.get_component_state("nlp", "Up"):
    #     if nlp_wait <= 200:
    #         result = caitCore.send_component_commond("nlp", "NLP Up," + mode)
    #         if result == False:
    #             logging.info("Init NLP: Error occurred")
    #             return result
    #         logging.info("Init NLP: Waiting for NLP up")
    #         nlp_wait = nlp_wait + 1
    #         time.sleep(1)
    #     else:
    #         logging.info("Init NLP Error: NLP module not responding, please check the module status")
    #         return False
    
    return True, "OK"


def deactivate_nlp():
    #caitCore.send_component_commond("nlp", "Down")
    return True


def initialize_control(hub_address):
    global control_initialized
    available_control_devices = get_control_devices()
    spike_control = None
    all_control_services = CURTCommands.get_control_services()
    for control in all_control_services:
        if control.name == "spike_control":
            spike_control = control
    if spike_control is None:
        return False, "No control service available"
    address = hub_address[hub_address.find(": ")+2:-2]
    CURTCommands.config_worker(spike_control, {"hub_address": address})
    time.sleep(3)
    control_initialized = True
    return True, "OK"


def deactivate_control():
    global control_initialized
    # result = caitCore.send_component_commond("control", "Control Down")
    # if result == False:
    #     logging.info("Deactivate Control: Error occurred")
    #     return result
    control_initialized = False
    return True


def reset_modules():
    global vision_initialized
    global voice_initialized
    global nlp_initialized
    global control_initialized
    global smarthome_initialized
    global vision_mode
    global stream_thread
    # result = caitCore.send_component_commond("module_states", "Reset")
    # if result == False:
    #     logging.info("Reset Modules: Error occurred")
    #     return result
    vision_initialized = False
    voice_initialized = False
    nlp_initialized = False
    control_initialized = False
    smarthome_initialized = False
    vision_mode = ""
    if stream_thread is not None:
        stream_thread.join()
    return True


def change_module_parameters(parameter_name, value):
    # global audio_output_device
    # #print("name: ", parameter_name, ", value: ", value)
    # if parameter_name == "face recognition confidence":
    #     result = caitCore.send_component_commond("vision", "set recognition confidence:" + str(value))
    #     if result == False:
    #         logging.info("Change Vision params: Error occurred")
    # elif parameter_name == "face detection confidence":
    #     result = caitCore.send_component_commond("vision", "set face detection confidence:" + str(value))
    #     if result == False:
    #         logging.info("Change Vision params: Error occurred")
    # elif parameter_name == "object detection confidence":
    #     result = caitCore.send_component_commond("vision", "set object detection confidence:" + str(value))
    #     if result == False:
    #         logging.info("Change Vision params: Error occurred")
    # elif parameter_name == "audio output device":
    #     audio_output_device = value
    # time.sleep(0.1)
    pass


def get_camera_image(from_network_passthrough=False, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    worker = get_oakd_devices()[0]
    rgb_frame_handler = None
    frame = None
    if from_network_passthrough:
        if 'rgb_passthrough_frame' in oakd_nodes:
            rgb_frame_handler = CURTCommands.oakd_get_rgb_frame(oakd_nodes['rgb_passthrough_frame'])
        else:
            logging.warning("No passthrough node in the pipeline")
    else:
        if 'rgb_frame' in oakd_nodes:
            rgb_frame_handler = CURTCommands.oakd_get_rgb_frame(oakd_nodes['rgb_frame'])
        else:
            logging.warning("No rgb camera preview node in the pipeline")
    if rgb_frame_handler is not None:
        frame = CURTCommands.get_result(rgb_frame_handler, for_streaming)['dataValue']['data']
        if not isinstance(frame ,str):
            frame = None
    return frame


def change_vision_mode(mode):
    global vision_mode
    # if not caitCore.get_component_state("vision", "Up"):
    #     logging.info("Please call initialize_vision() function before using the vision module")
    #     return
    # #print("Send change mode to:", mode)
    # result = caitCore.send_component_commond("vision", "mode:" + mode)
    # if result == False:
    #     logging.info("Change Vision Mode: Error occurred")
    # caitCore.component_manager.receivedInferenceResult = False
    vision_mode = mode
    pass


def detect_face(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info("Please call initialize_vision() function before using the vision module")
        return None
    change_vision_mode("face_detection")
    worker = get_oakd_devices()[0]
    if 'rgb_passthrough_frame' in oakd_nodes and 'face_detection' in oakd_nodes:
        spatial_face_detection_handler = CURTCommands.oakd_spatial_face_detection("face_spatial_detections")
        faces = CURTCommands.get_result(spatial_face_detection_handler, for_streaming)['dataValue']['data']
        if not isinstance(faces, list):
            faces = []
        return faces


def recognize_face(from_network_passthrough=True, for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info("Please call initialize_vision() function before using the vision module")
        return None, []
    change_vision_mode("face_recognition")
    worker = get_oakd_devices()[0]
    rgb_frame_handler = None
    if from_network_passthrough:
        if 'rgb_passthrough_frame' in oakd_nodes:
            rgb_frame_handler = CURTCommands.oakd_get_rgb_frame(oakd_nodes['rgb_passthrough_frame'])
        else:
            logging.warning("No passthrough node in the pipeline")
    else:
        if 'rgb_frame' in oakd_nodes:
            rgb_frame_handler = CURTCommands.oakd_get_rgb_frame(oakd_nodes['rgb_frame'])
        else:
            logging.warning("No rgb camera preview node in the pipeline")
    spatial_face_detection_handler = None
    if 'rgb_passthrough_frame' in oakd_nodes and 'face_detection' in oakd_nodes:
        spatial_face_detection_handler = CURTCommands.oakd_spatial_face_detection("face_spatial_detections")
    if rgb_frame_handler is not None and spatial_face_detection_handler is not None:
        if 'face_landmarks' in oakd_nodes and 'face_features' in oakd_nodes:

            face_recognition_handler = CURTCommands.oakd_face_recognition(oakd_nodes["face_features"], 
                                                                          oakd_nodes["face_landmarks"], 
                                                                          rgb_frame_handler, 
                                                                          spatial_face_detection_handler)
            identities = CURTCommands.get_result(face_recognition_handler, for_streaming)['dataValue']['data']
            person = ""
            largest_area = 0
            largest_bbox = None
            people = {}
            rgb_frame = identities['frame']
            for name in identities:
                if name != "frame":
                    detection = identities[name]
                    people[name] = detection
                    x1 = int(detection[0])
                    y1 = int(detection[1])
                    x2 = int(detection[2])
                    y2 = int(detection[3])
                    area = (x2-x1) * (y2-y1)
                    if area > largest_area:
                        largest_area = area
                        person = name
                        largest_bbox = [x1, y1, x2, y2]
            if not for_streaming:
                return person, largest_bbox
            else:
                return people, rgb_frame
        else:
            return "None", []
    else:
        return "None", []


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


def detect_objects():
    # if not caitCore.get_component_state("vision", "Up"):
    #     logging.info("Please call initialize_vision() function before using the vision module")
    #     return None
    # change_vision_mode("ObjectDetection")
    # while not caitCore.component_manager.receivedInferenceResult:
    #     time.sleep(0.005)
    # if caitCore.component_manager.currentNames[0] != "None":
    #     caitCore.component_manager.receivedInferenceResult = False
    #     coordinates = caitCore.component_manager.coordinates
    #     names = caitCore.component_manager.currentNames
    #     if caitCore.get_current_processor("vision") != "local":
    #         width, height = caitCore.component_manager.currentImage.size
    #         for i in range(len(coordinates)):
    #             coordinate = coordinates[i]
    #             coordinate[0] = int(coordinate[0] * width)
    #             coordinate[1] = int(coordinate[1] * height)
    #             coordinate[2] = int(coordinate[2] * width)
    #             coordinate[3] = int(coordinate[3] * height)
    #     return names, coordinates
    # else:
    #     return "", []
    return "", []


def classify_image():
    # if not caitCore.get_component_state("vision", "Up"):
    #     logging.info("Please call initialize_vision() function before using the vision module")
    #     return None
    # change_vision_mode("ImageClassification")
    # while not caitCore.component_manager.receivedInferenceResult:
    #     time.sleep(0.005)
    # if caitCore.component_manager.currentNames[0] != "None":
    #     caitCore.component_manager.receivedInferenceResult = False
    #     names = caitCore.component_manager.currentNames
    #     return names
    return []


def say(message_topic, entities=[]):
    global voice_mode
    message = message_topic
    if not voice_initialized:
        logging.info("Please call initialize_voice() function before using the vision module")
        return False
    voice_input_worker = get_audio_devices()[0]
    if voice_mode == "online":
        voice_generation_worker = get_voice_generation_services(online=True)[0]
    else:
        voice_generation_worker = get_voice_generation_services(online=False)[0]
    logging.info("say: " + message)
    CURTCommands.pause_recording(voice_input_worker)
    online_voice_generation_handler = CURTCommands.send_task(voice_generation_worker, message)
    generation_status = CURTCommands.get_result(online_voice_generation_handler)
    CURTCommands.resume_recording(voice_input_worker)
    return True


def listen():
    
    return True, ""


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


def control_motor(hub_name, motor_name, speed, duration):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "hub " + hub_name + " move " + motor_name + " " + str(speed) + " " + str(duration)
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"

def set_motor_position(hub_name, motor_name, position):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "hub " + hub_name + " position " + motor_name + " " + str(position)
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"

def set_motor_power(hub_name, motor_name, power):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "hub " + hub_name + " pwm " + motor_name + " " + str(power)
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"


def set_motor_power_group(operation_list):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "power_group " + operation_list
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor Power Group: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"


def control_motor_group(operation_list):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "motor_group " + operation_list
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Control Motor Speed Group: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"


def rotate_motor(hub_name, motor_name, angle):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info("Please call initialize_control() function before using Control module")
        return False, "Not initialized"
    command = "hub " + hub_name + " rotate " + motor_name + " " + str(angle)
    #logging.info("Robot command:"+ str(command))
    result = caitCore.send_component_commond("control", command)
    if result == False:
        logging.info("Rotate Motor: Error occurred")
    while not caitCore.component_manager.doneMoving:
        if caitCore.component_manager.controlException:
            caitCore.component_manager.controlException = False
            logging.warning("Hub disconnected")
            return False, caitCore.component_manager.controlExceptionMsg
        time.sleep(0.03)
    return True, "OK"


def get_devices(device_type):
    url = "http://0.0.0.0:8123/api/states"
    response = requests.request('GET', url, headers=headers)
    response_data = response.json()

    device_names = []

    for state in response_data:
        if state['entity_id'].find(device_type+".") != -1:
            detail_url = "http://0.0.0.0:8123/api/states/" + state['entity_id']
            detail_response = requests.request('GET', detail_url, headers=headers).json()
            if (detail_response['state'] != "unavailable"):
                name = state['entity_id'][state['entity_id'].find(".")+1:]
                device_names.append(name)
    return device_names


def control_light(device_name, operation, parameter=None):
    if operation == "turn_on" or operation == "turn_off" or operation == "toggle":
        url = "http://0.0.0.0:8123/api/services/light/" + operation
        data = {"entity_id": device_name}
    else:
        if operation == "color_name":
            url = "http://0.0.0.0:8123/api/services/light/turn_on"
            data = {"entity_id": device_name, "color_name": parameter}
        elif operation == "brightness_pct":
            url = "http://0.0.0.0:8123/api/services/light/turn_on"
            data = {"entity_id": device_name, "brightness_pct": int(parameter)}
    response = requests.request('POST', url, headers=headers, data=json.dumps(data))
    return response.json()


def control_media_player(device_name, operation):
    url = "http://0.0.0.0:8123/api/services/media_player/" + operation
    data = {"entity_id": device_name}
    response = requests.request('POST', url, headers=headers, data=json.dumps(data))
    return response.json()


def draw_disconnected_rect(img, pt1, pt2, color, thickness):
        width = pt2[0] - pt1[0]
        height = pt2[1] - pt1[1]
        cv2.line(img, pt1, (pt1[0] + width // 4, pt1[1]), color, thickness)
        cv2.line(img, pt1, (pt1[0], pt1[1] + height // 4), color, thickness)
        cv2.line(img, (pt2[0] - width // 4, pt1[1]), (pt2[0], pt1[1]), color, thickness)
        cv2.line(img, (pt2[0], pt1[1]), (pt2[0], pt1[1] + height // 4), color, thickness)
        cv2.line(img, (pt1[0], pt2[1]), (pt1[0] + width // 4, pt2[1]), color, thickness)
        cv2.line(img, (pt1[0], pt2[1] - height // 4), (pt1[0], pt2[1]), color, thickness)
        cv2.line(img, pt2, (pt2[0] - width // 4, pt2[1]), color, thickness)
        cv2.line(img, (pt2[0], pt2[1] - height // 4), pt2, color, thickness)


def streaming_func():
    global streaming_client
    global streaming_channel
    global vision_initialized
    global vision_mode
    while True:
        if vision_initialized:
            img = None
            if vision_mode != 'face_recognition':
                img = get_camera_image(from_network_passthrough=True, for_streaming=True)
                if img is not None:
                    img = decode_image_byte(img)
                    img = cv2.resize(img, (455, 256))
                    if vision_mode == "face_detection":
                        faces = detect_face(for_streaming=True)
                        for bbox in faces:
                            x1 = int(bbox[0] * img.shape[1])
                            y1 = int(bbox[1] * img.shape[0])
                            x2 = int(bbox[2] * img.shape[1])
                            y2 = int(bbox[3] * img.shape[0])
                            x_center = int(x1 + (x2 - x1) / 2)
                            if len(bbox) == 5:
                                face_distance = bbox[4]
                                z_text = f"Distance: {int(face_distance)} mm"
                                textSize = ft.getTextSize(z_text, fontHeight=14, thickness=-1)[0]
                                cv2.rectangle(img, (x_center - textSize[0] // 2 - 5, y1 - 5), (x_center - textSize[0] // 2 + textSize[0] + 10, y1 - 22), COLOR[0], -1)
                                ft.putText(img=img, text=z_text, org=(x_center - textSize[0] // 2, y1 - 8), fontHeight=14, color=(255, 255, 255), thickness=-1, line_type=cv2.LINE_AA, bottomLeftOrigin=True)
                            cv2.rectangle(img, (x1, y1), (x2, y2), COLOR[0], cv2.FONT_HERSHEY_SIMPLEX)
            else:
                people, rgb_frame = recognize_face(from_network_passthrough=True, for_streaming=True)
                img = decode_image_byte(rgb_frame)
                img = cv2.resize(img, (455, 256))
                for name in people:
                    detection = people[name]
                    x1 = int(detection[0])
                    y1 = int(detection[1])
                    x2 = int(detection[2])
                    y2 = int(detection[3])
                    x_center = int(x1 + (x2 - x1) / 2)
                    color = COLOR[2]
                    if name != "Unknown":
                        color = COLOR[1]
                    name_text = "Name: " + name
                    textSize = ft.getTextSize(name_text, fontHeight=14, thickness=-1)[0]
                    if len(detection) == 5:
                        face_distance = detection[4]
                        z_text = f"Distance: {int(face_distance)} mm"
                        textSize = ft.getTextSize(z_text, fontHeight=14, thickness=-1)[0]
                        cv2.rectangle(img, (x_center - textSize[0] // 2 - 5, y1 - 5), (x_center - textSize[0] // 2 + textSize[0] + 10, y1 - 22), color, -1)
                        ft.putText(img=img, text=z_text, org=(x_center - textSize[0] // 2, y1 - 8), fontHeight=14, color=(255, 255, 255), thickness=-1, line_type=cv2.LINE_AA, bottomLeftOrigin=True)
                    if name != "Unknown":
                        draw_disconnected_rect(img, (x1, y1), (x2, y2), color, 1)
                        cv2.rectangle(img, (x_center - textSize[0] // 2 - 5, y1 - 22), (x_center - textSize[0] // 2 + textSize[0] + 10, y1 - 39), color, -1)
                        ft.putText(img=img, text=name_text , org=(x_center - textSize[0] // 2, y1 - 25), fontHeight=14, color=(255, 255, 255), thickness=-1, line_type=cv2.LINE_AA, bottomLeftOrigin=True)
                    else:
                        cv2.rectangle(img, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
            _, buffer = cv2.imencode('.jpg', img, encode_param)
            imgByteArr = base64.b64encode(buffer)
            streaming_client.publish(streaming_channel, imgByteArr)
        else:
            print("Stream thread exiting")
            break


if __name__ == "__main__":
    pass
