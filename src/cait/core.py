""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""
import sys
import signal

sys.path.insert(0, "/home/pi/CAIT_CURT/curt/src")
from curt.command import CURTCommands
import paho.mqtt.client as mqtt
import logging
import time
import json
import os
import socket
import sys
import ast
import requests
import base64
import threading
import numpy as np
import cv2
from .managers.device_manager import DeviceManager
from .PID import PID
from .core_data import *
from .utils import (
    connect_mqtt,
    decode_image_byte,
    draw_face_detection,
    draw_face_recognition,
    draw_object_detection,
    draw_face_emotions,
    draw_facemesh,
    draw_body_landmarks,
    draw_hand_landmarks,
)

full_domain_name = socket.getfqdn()

device_manager = DeviceManager()

logging.getLogger().setLevel(logging.WARNING)

broker_address = CURTCommands.initialize()

streaming_channel = "cait/output/" + os.uname()[1].lower() + "/displayFrame"
streaming_client = mqtt.Client()
ret = connect_mqtt(streaming_client, broker_address)
while ret != True:
    time.sleep(1)
    ret = connect_mqtt(streaming_client, broker_address)


def get_video_devices():
    all_vision_input = CURTCommands.get_vision_input_services()
    camera_workers = []
    for vision_input in all_vision_input:
        if vision_input.name == "webcam" or vision_input.name == "picam_input":
            camera_workers.append(vision_input)
    return camera_workers


def get_audio_devices():
    voice_inputs = []
    all_voice_input_services = CURTCommands.get_voice_input_services()
    for voice_input in all_voice_input_services:
        if voice_input.name == "live_input":
            voice_inputs.append(voice_input)
    return voice_inputs


def get_respeaker_services():
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


def get_rasa_intent_services():
    nlp_intents = []
    all_nlp_intent_services = CURTCommands.get_nlp_intent_services()
    for nlp_intent in all_nlp_intent_services:
        if nlp_intent.name == "rasa_intent_classifier":
            nlp_intents.append(nlp_intent)
    return nlp_intents


def get_control_devices():
    control_devices = device_manager.get_control_devices()
    connected_devices = []
    for device in control_devices:
        if device["connected"]:
            if device["device"] == "EV3":
                connected_devices.append(device["device"] + ": " + device["ip_addr"])
            else:
                connected_devices.append(device["device"] + ": " + device["mac_addr"])
    return control_devices


def get_control_services():
    spike_control = []
    all_control_services = CURTCommands.get_control_services()
    for control in all_control_services:
        if control.name == "spike_control":
            spike_control.append(control)
    return spike_control


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
    global drawing_modes
    global preview_width
    global preview_height
    if vision_initialized:
        vision_initialized = False
        if stream_thread is not None:
            stream_thread.join()
    current_video_device = None
    if processor == "oakd":
        # available_video_devices = CURTCommands.get_oakd_services("oakd_pipeline")
        current_video_device = CURTCommands.get_worker(
            full_domain_name + "/vision/oakd_service/oakd_pipeline"
        )
    else:
        available_video_devices = get_video_devices()
        if len(available_video_devices) != 0:
            current_video_device = available_video_devices[0]
    if current_video_device is None:
        return (
            False,
            "No video device is detected, or connected device is not supported",
        )

    if processor == "oakd":
        for node in mode:
            if node[0] == "add_rgb_cam_node":
                preview_width = node[1]
                preview_height = node[2]

        CURTCommands.config_worker(current_video_device, mode)
    else:
        # Selecting a VGA resolution, future work should provide a list of selected resolution
        CURTCommands.config_worker(
            current_video_device,
            {"camera_index": 0, "capture_width": 640, "capture_height": 480},
        )
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": False,
        "Face Recognition": False,
        "Face Emotions": False,
        "Face Mesh": False,
        "Object Detection": False,
        "Hand Landmarks": False,
        "Pose Landmarks": False,
    }
    time.sleep(10)
    vision_initialized = True
    stream_thread = threading.Thread(target=streaming_func, daemon=True)
    stream_thread.start()
    logging.info("***********Streaming preview thread started***********")
    return True, "OK"


def deactivate_vision():
    global vision_initialized
    global vision_mode
    vision_initialized = False
    vision_mode = []
    return True


def get_cloud_accounts():
    return account_names


def get_nlp_models():
    model_list = []
    for model in os.listdir("/home/pi/CAIT_CURT/curt/src/models/modules/nlp"):
        if os.path.isdir("/home/pi/CAIT_CURT/curt/src/models/modules/nlp/" + model):
            model_list.append(model)
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
    voice_generation_worker = None
    voice_processing_worker = None
    voice_input_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
    voice_processing_worker = get_voice_processing_services()
    if mode == "online":
        voice_mode = "online"
        voice_processing_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/speech_to_text_service/online_voice_processing"
        )
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_mode = "offline"
        voice_processing_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/speech_to_text_service/offline_voice_processing"
        )
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    if voice_input_worker is None:
        return (
            False,
            "No audio deveice is detected, or connected device is not supported",
        )
    if voice_processing_worker is None:
        return (
            False,
            "No voice processing service is detected, or connected device is not supported",
        )
    if voice_generation_worker is None:
        return (
            False,
            "No voice generation is detected, or connected device is not supported",
        )
    CURTCommands.config_worker(voice_input_worker, {"audio_in_index": 0})
    time.sleep(0.5)
    CURTCommands.request(voice_input_worker, params=["start"])
    # CURTCommands.start_voice_recording(voice_input_worker)
    if mode == "online":
        account_file = cloud_accounts[account]
        with open("/home/pi/CAIT_CURT/" + account_file) as f:
            account_info = json.load(f)
        CURTCommands.config_worker(
            voice_processing_worker,
            {
                "account_crediential": account_info,
                "language": processing_language,
                "sample_rate": 16000,
                "channel_count": 4,
            },
        )
        CURTCommands.config_worker(
            voice_generation_worker,
            {"language": generation_language, "accents": generation_accents},
        )
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
    global nlp_initialized
    global current_nlp_model
    rasa_intent_workers = get_rasa_intent_services()
    CURTCommands.config_worker(rasa_intent_workers[0], {"model": mode})
    if current_nlp_model != mode:
        current_nlp_model = mode
        time.sleep(40)
    else:
        time.sleep(1)
    nlp_initialized = True
    return True, "OK"


def deactivate_nlp():
    # caitCore.send_component_commond("nlp", "Down")
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
    address = hub_address[hub_address.find(": ") + 2 : -2]
    CURTCommands.config_worker(spike_control, {"hub_address": address})
    time.sleep(5)
    control_initialized = True
    CURTCommands.display_image(spike_control, "Happy")
    return True, "OK"


def deactivate_control():
    global control_initialized
    global pid_controller
    # result = caitCore.send_component_commond("control", "Control Down")
    # if result == False:
    #     logging.info("Deactivate Control: Error occurred")
    #     return result
    control_initialized = False
    pid_controller = None
    return True


def initialize_pid(kp, ki, kd):
    global pid_controller
    if pid_controller is None:
        print("Initializing PID controller")
        print(kp, ki, kd)
        print("***********PID************")
        pid_controller = PID(kP=kp, kI=ki, kD=kd)
        pid_controller.initialize()
    return True, "OK"


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


def get_camera_image(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    rgb_frame_handler = None
    frame = None
    if worker is not None:
        rgb_frame_handler = CURTCommands.request(worker, params=["get_rgb_frame"])
    else:
        logging.warning("No rgb camera worker found.")
    if rgb_frame_handler is not None:
        frame = CURTCommands.get_result(rgb_frame_handler, for_streaming)["dataValue"][
            "data"
        ]
        if not isinstance(frame, str):
            frame = None
    return frame


def get_stereo_image(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_stereo_camera_input"
    )
    stereo_frame_handler = None
    frame = None
    if worker is not None:
        stereo_frame_handler = CURTCommands.request(worker, params=["get_stereo_frame"])
    else:
        logging.warning("No stereo camera worker fonund.")
    if stereo_frame_handler is not None:
        frame = CURTCommands.get_result(stereo_frame_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if not isinstance(frame, str):
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
    vision_mode.append(mode)


def enable_drawing_mode(mode):
    global drawing_modes
    # print("********************")
    # print("Mode:", mode)
    drawing_modes[mode] = True


def detect_face(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_detection")
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    faces = []
    if worker is not None:
        spatial_face_detection_handler = CURTCommands.request(
            worker, params=["get_spatial_face_detections"]
        )
        faces = CURTCommands.get_result(spatial_face_detection_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if not isinstance(faces, list):
            faces = []
    for face in faces:
        face[0] = int(face[0] * preview_width)
        face[1] = int(face[1] * preview_height)
        face[2] = int(face[2] * preview_width)
        face[3] = int(face[3] * preview_height)
        if face[0] < 0:
            face[0] = 0
        if face[1] < 0:
            face[1] = 0
        if face[2] >= preview_width:
            face[2] = preview_width - 1
        if face[3] >= preview_height:
            face[3] = preview_height - 1
    return faces


def recognize_face(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None, []
    change_vision_mode("face_recognition")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    face_recognition_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_recognition"
    )
    rgb_frame_handler = None
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera preview node in the pipeline")
    spatial_face_detection_handler = None
    if face_detection_worker is not None:
        spatial_face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["get_spatial_face_detections"]
        )
    people = "None"
    coordinates = []
    if rgb_frame_handler is not None and spatial_face_detection_handler is not None:
        face_recognition_handler = CURTCommands.request(
            face_recognition_worker,
            params=[
                rgb_frame_handler,
                spatial_face_detection_handler,
                "recognize_face",
            ],
        )
        identities = CURTCommands.get_result(face_recognition_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if identities is not None:
            person = ""
            largest_area = 0
            largest_bbox = None
            people = {}
            # rgb_frame = identities["frame"]
            for name in identities:
                if name != "frame":
                    detection = identities[name]
                    people[name] = detection
                    x1 = int(detection[0])
                    y1 = int(detection[1])
                    x2 = int(detection[2])
                    y2 = int(detection[3])
                    area = (x2 - x1) * (y2 - y1)
                    if area > largest_area:
                        largest_area = area
                        person = name
                        largest_bbox = [x1, y1, x2, y2]
            if not for_streaming:
                people = person
                coordinates = largest_bbox

    return people, coordinates


def add_person(name):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("FaceRecognition")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    result = caitCore.send_component_commond("vision", "Add Person:" + name)
    if result == False:
        logging.info("Add Person: Error occurred")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    caitCore.component_manager.currentNames[0] = name
    return True


def remove_person(name):
    if not caitCore.get_component_state("vision", "Up"):
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("FaceRecognition")
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    result = caitCore.send_component_commond("vision", "Remove Person:" + name)
    if result == False:
        logging.info("Remove Person: Error occurred")
    print("Removing:", name)
    while not caitCore.component_manager.receivedInferenceResult:
        time.sleep(0.03)
    caitCore.component_manager.currentNames[0] = "Unknown"
    return True


def detect_objects(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("object_detection")
    worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_object_detection"
    )
    coordinates = []
    names = []
    objects = []
    if worker is not None:
        spatial_object_detection_handler = CURTCommands.request(
            worker, params=["get_spatial_object_detections"]
        )
        objects = CURTCommands.get_result(
            spatial_object_detection_handler, for_streaming
        )["dataValue"]["data"]
        if not isinstance(objects, list):
            objects = []
    for object in objects:
        object[0] = int(object[0] * preview_width)
        object[1] = int(object[1] * preview_height)
        object[2] = int(object[2] * preview_width)
        object[3] = int(object[3] * preview_height)

        if object[0] < 0:
            object[0] = 0
        if object[1] < 0:
            object[1] = 0
        if object[2] >= preview_width:
            object[2] = preview_width - 1
        if object[3] >= preview_height:
            object[3] = preview_height - 1

        coordinates.append(
            [
                object[0],
                object[1],
                object[2],
                object[3],
                object[4],
                object[5],
                object[6],
            ]
        )
        if not for_streaming:
            names.append(object_labels[object[-1]])
        else:
            names.append(object[-1])
    return names, coordinates


def face_emotions_estimation(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("face_emotions")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    face_emotions_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_emotions"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera preview node in the pipeline")
    spatial_face_detection_handler = None
    if face_detection_worker is not None:
        spatial_face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["get_spatial_face_detections"]
        )
    emotions = []
    if rgb_frame_handler is not None and spatial_face_detection_handler is not None:
        face_emotions_handler = CURTCommands.request(
            face_emotions_worker,
            params=[rgb_frame_handler, spatial_face_detection_handler],
        )
        emotions = CURTCommands.get_result(face_emotions_handler, for_streaming)[
            "dataValue"
        ]["data"]
        if not for_streaming:
            for emotion in emotions:
                raw_emtotions = emotion[0]
                emo = {}
                emo["neutral"] = raw_emtotions[0]
                emo["happy"] = raw_emtotions[1]
                emo["sad"] = raw_emtotions[2]
                emo["surprise"] = raw_emtotions[3]
                emo["anger"] = raw_emtotions[4]
                emotion[0] = emo
    return emotions


def facemesh_estimation(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("facemesh")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    face_detection_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_face_detection"
    )
    facemesh_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_facemesh"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera preview node in the pipeline")
    spatial_face_detection_handler = None
    if face_detection_worker is not None:
        spatial_face_detection_handler = CURTCommands.request(
            face_detection_worker, params=["get_spatial_face_detections"]
        )
    facemeshes = []
    if rgb_frame_handler is not None and spatial_face_detection_handler is not None:
        facemesh_handler = CURTCommands.request(
            facemesh_worker, params=[rgb_frame_handler, spatial_face_detection_handler]
        )
        facemeshes = CURTCommands.get_result(facemesh_handler, for_streaming)[
            "dataValue"
        ]["data"]
    return facemeshes


def get_hand_landmarks(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("hand_landmarks")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    hand_landmarks_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_hand_landmarks"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera worker found.")
    hand_landmarks_coordinates = []
    hand_bboxes = []
    handnesses = []
    if rgb_frame_handler is not None:
        hand_landmarks_handler = CURTCommands.request(
            hand_landmarks_worker,
            params=[rgb_frame_handler],
        )
        hand_ladmarks = CURTCommands.get_result(hand_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
        for landmarks in hand_ladmarks:
            hand_landmarks_coordinates.append(landmarks[0])
            hand_bboxes.append(landmarks[1])
            handnesses.append(landmarks[2])
    return hand_landmarks_coordinates, hand_bboxes, handnesses


def get_body_landmarks(for_streaming=False):
    global oakd_nodes
    global vision_initialized
    if not vision_initialized:
        logging.info(
            "Please call initialize_vision() function before using the vision module"
        )
        return None
    change_vision_mode("body_landmarks")
    camera_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_rgb_camera_input"
    )
    body_landmarks_worker = CURTCommands.get_worker(
        full_domain_name + "/vision/oakd_service/oakd_pose_estimation"
    )
    if camera_worker is not None:
        rgb_frame_handler = CURTCommands.request(
            camera_worker, params=["get_rgb_frame"]
        )
    else:
        logging.warning("No rgb camera worker found.")
    body_ladmarks = []
    if rgb_frame_handler is not None:
        body_landmarks_handler = CURTCommands.request(
            body_landmarks_worker,
            params=[rgb_frame_handler],
        )
        body_ladmarks = CURTCommands.get_result(body_landmarks_handler, for_streaming)[
            "dataValue"
        ]["data"]
    return body_ladmarks


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
        logging.info(
            "Please call initialize_voice() function before using the vision module"
        )
        return False
    voice_input_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
    if voice_mode == "online":
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    logging.info("say: " + message)
    CURTCommands.request(voice_input_worker, params=["pause"])
    voice_generation_handler = CURTCommands.request(
        voice_generation_worker, params=[message]
    )
    generation_status = CURTCommands.get_result(voice_generation_handler)
    CURTCommands.request(voice_input_worker, params=["resume"])
    return True


def listen():
    global voice_mode
    voice_input_worker = CURTCommands.get_worker(
        full_domain_name + "/voice/voice_input_service/respeaker_input"
    )
    if voice_mode == "online":
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/online_voice_generation"
        )
    else:
        voice_generation_worker = CURTCommands.get_worker(
            full_domain_name + "/voice/text_to_speech_service/offline_voice_generation"
        )
    CURTCommands.request(voice_input_worker, params=["pause"])
    voice_generation_handler = CURTCommands.request(
        voice_generation_worker, params=["notification_tone"]
    )
    generation_status = CURTCommands.get_result(voice_generation_handler)
    time.sleep(0.1)
    CURTCommands.request(voice_input_worker, params=["resume"])
    time.sleep(0.05)
    speech = ""
    while speech == "":
        voice_handler = CURTCommands.request(voice_input_worker, params=["get"])
        voice_processing_worker = None
        if voice_mode == "online":
            voice_processing_worker = CURTCommands.get_worker(
                full_domain_name
                + "/voice/speech_to_text_service/online_voice_processing"
            )
        else:
            voice_processing_worker = CURTCommands.get_worker(
                full_domain_name
                + "/voice/speech_to_text_service/offline_voice_processing"
            )
        voice_processing_handler = CURTCommands.request(
            voice_processing_worker, params=[voice_handler]
        )
        speech_result = CURTCommands.get_result(voice_processing_handler)
        if speech_result is not None:
            speech = speech_result["dataValue"]["data"]
            if speech is None:
                speech = ""
    return True, speech


def analyze(user_message):
    if not nlp_initialized:
        logging.info(
            "Please call initialize_nlp() function before using the vision module"
        )
        return "", "", ""
    rasa_intent_worker = get_rasa_intent_services()[0]

    nlp_intent_handler = CURTCommands.send_task(rasa_intent_worker, user_message)
    nlp_intent = CURTCommands.get_result(nlp_intent_handler)["dataValue"]["data"]
    nlp_response = json.loads(nlp_intent)
    topic = nlp_response["topic"]
    condifence = nlp_response["confidence"]
    extracted_entities = nlp_response["entities"]
    entities = []
    for entity in extracted_entities:
        entity_entry = {
            "entity_name": entity["entity"],
            "entity_value": entity["value"],
        }
        entry_is_uniqued = True
        for e in entities:
            if (
                entity_entry["entity_name"] == e["entity_name"]
                and entity_entry["entity_value"] == e["entity_value"]
            ):
                entry_is_uniqued = False
        if entry_is_uniqued:
            entities.append(entity_entry)
    return topic, condifence, entities


def control_motor(hub_name, motor_name, speed, duration):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motor = motor_name[-1]
    CURTCommands.set_motor_speed(worker, motor, int(speed))
    start_time = time.monotonic()
    while (time.monotonic() - start_time) < float(duration):
        time.sleep(0.01)
    CURTCommands.brake_motor(worker, motor)
    return True, "OK"


def set_motor_position(hub_name, motor_name, position):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motor = motor_name[-1]
    CURTCommands.rotate_motor_to_position(worker, motor, int(position), 70)
    time.sleep(1)
    return True, "OK"


def set_motor_power(hub_name, motor_name, power):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motor = motor_name[-1]
    CURTCommands.set_motor_speed(worker, motor, int(power))
    time.sleep(0.1)
    return True, "OK"


def rotate_motor(hub_name, motor_name, angle):
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motor = motor_name[-1]
    speed = 70
    if int(angle) < 0:
        speed = -70
    CURTCommands.rotate_motor_for_degrees(worker, motor, int(angle), speed)
    time.sleep(0.1)
    return True, "OK"


def set_motor_power_group(operation_list):
    caitCore.component_manager.doneMoving = False
    if not caitCore.get_component_state("control", "Up"):
        logging.info(
            "Please call initialize_control() function before using Control module"
        )
        return False, "Not initialized"
    command = "power_group " + operation_list
    # logging.info("Robot command:"+ str(command))
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
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motor_list = []
    duration_list = []
    largest_duration = 0
    largest_angle = 0
    op_list = json.loads(operation_list)["operation_list"]
    for operation in op_list:
        motor_name = operation["motor_name"]
        motor = motor_name[-1]
        if "speed" in operation:
            motor_list.append(motor)
            speed = int(operation["speed"])
            duration = float(operation["duration"])
            if duration > largest_duration:
                largest_duration = duration
            duration_list.append(duration)
            CURTCommands.set_motor_speed(worker, motor, int(speed))
        elif "angle" in operation:
            motor_list.append(motor)
            angle = int(operation["angle"])
            if abs(angle) > largest_angle:
                largest_angle = abs(angle)
            speed = 70
            if int(angle) < 0:
                speed = -70
            CURTCommands.rotate_motor_for_degrees(worker, motor, int(angle), speed)
        elif "position" in operation:
            position = int(operation["position"])
            if abs(position) > largest_angle:
                largest_angle = abs(position)
            CURTCommands.rotate_motor_to_position(worker, motor, int(position), 70)
        elif "power" in operation:
            power = int(operation["power"])
            if power != 0:
                control_params = {
                    "control_type": "motor",
                    "operation": {
                        "motor_arrangement": "individual",
                        "motor": motor,
                        "motion": "speed",
                        "speed": int(power),
                    },
                }
                CURTCommands.request(worker, params=[control_params])
            else:
                control_params = {
                    "control_type": "motor",
                    "operation": {
                        "motor_arrangement": "individual",
                        "motor": motor,
                        "motion": "brake",
                    },
                }
                CURTCommands.request(worker, params=[control_params])
            # CURTCommands.brake_motor(worker, motor)
    if largest_angle > 800:
        if largest_duration < 2:
            largest_duration = 2
    else:
        largest_duration = 1.2
    start_time = time.monotonic()
    while time.monotonic() - start_time < largest_duration:
        remaining_duration_list = []
        for i in range(0, len(duration_list)):
            if time.monotonic() - start_time >= duration_list[i]:
                CURTCommands.brake_motor(worker, motor_list[i])
            else:
                remaining_duration_list.append(duration_list[i])
        duration_list = remaining_duration_list
        time.sleep(0.1)
    for m in range(0, len(motor_list)):
        CURTCommands.brake_motor(worker, motor_list[m])
    time.sleep(0.003)
    return True, "OK"


def stop_all_motors():
    global oakd_nodes
    global control_initialized
    if not control_initialized:
        logging.info(
            "Please call initialize_control() function before using the vision module"
        )
        return False, "Not initialized"
    worker = get_control_services()[0]
    motors = ["A", "B", "C", "D", "E", "F"]
    for motor in motors:
        control_params = {
            "control_type": "motor",
            "operation": {
                "motor_arrangement": "individual",
                "motor": motor,
                "motion": "brake",
            },
        }
        CURTCommands.request(worker, params=[control_params])


def update_pid(error):
    global pid_controller
    if pid_controller is not None:
        return int(pid_controller.update(error))
    else:
        return 0


def get_devices(device_type):
    url = "http://0.0.0.0:8123/api/states"
    response = requests.request("GET", url, headers=headers)
    response_data = response.json()

    device_names = []

    for state in response_data:
        if state["entity_id"].find(device_type + ".") != -1:
            detail_url = "http://0.0.0.0:8123/api/states/" + state["entity_id"]
            detail_response = requests.request(
                "GET", detail_url, headers=headers
            ).json()
            if detail_response["state"] != "unavailable":
                name = state["entity_id"][state["entity_id"].find(".") + 1 :]
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
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()


def control_media_player(device_name, operation):
    url = "http://0.0.0.0:8123/api/services/media_player/" + operation
    data = {"entity_id": device_name}
    response = requests.request("POST", url, headers=headers, data=json.dumps(data))
    return response.json()


def streaming_func():
    global streaming_client
    global streaming_channel
    global vision_initialized
    global vision_mode
    global drawing_modes
    while True:
        if vision_initialized:
            img = None
            if drawing_modes["Depth Mode"]:
                img = get_stereo_image(for_streaming=True)
            else:
                img = get_camera_image(for_streaming=True)
            if img is not None:
                img = decode_image_byte(img)
                if "face_detection" in vision_mode:
                    if drawing_modes["Face Detection"]:
                        faces = detect_face(for_streaming=True)
                        img = draw_face_detection(img, faces)
                if "face_recognition" in vision_mode:
                    if drawing_modes["Face Recognition"]:
                        people, _ = recognize_face(for_streaming=True)
                        img = draw_face_recognition(img, people)
                if "object_detection" in vision_mode:
                    if drawing_modes["Object Detection"]:
                        names, coordinates = detect_objects(for_streaming=True)
                        img = draw_object_detection(img, names, coordinates)
                if "face_emotions" in vision_mode:
                    if drawing_modes["Face Emotions"]:
                        emotions = face_emotions_estimation(for_streaming=True)
                        img = draw_face_emotions(img, emotions)
                if "facemesh" in vision_mode:
                    if drawing_modes["Face Mesh"]:
                        facemeshes = facemesh_estimation(for_streaming=True)
                        img = draw_facemesh(img, facemeshes)
                if "body_landmarks" in vision_mode:
                    if drawing_modes["Pose Landmarks"]:
                        body_landmarks_coordinates = get_body_landmarks(
                            for_streaming=True
                        )
                        img = draw_body_landmarks(img, body_landmarks_coordinates)
                if "hand_landmarks" in vision_mode:
                    if drawing_modes["Hand Landmarks"]:
                        (
                            hand_landmarks_coordinates,
                            hand_bboxes,
                            handnesses,
                        ) = get_hand_landmarks(for_streaming=True)
                        img = draw_hand_landmarks(img, hand_landmarks_coordinates)
                encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 70]
                _, buffer = cv2.imencode(".jpg", img, encode_param)
                imgByteArr = base64.b64encode(buffer)
                streaming_client.publish(streaming_channel, imgByteArr)
        else:
            print("Stream thread exiting")
            break


def reset_modules():
    global vision_initialized
    global voice_initialized
    global nlp_initialized
    global control_initialized
    global smarthome_initialized
    global vision_mode
    global stream_thread
    global pid_controller
    global drawing_modes
    # result = caitCore.send_component_commond("module_states", "Reset")
    # if result == False:
    #     logging.info("Reset Modules: Error occurred")
    #     return result
    vision_initialized = False
    voice_initialized = False
    nlp_initialized = False
    if control_initialized:
        stop_all_motors()
    control_initialized = False
    smarthome_initialized = False
    vision_mode = []
    pid_controller = None
    if stream_thread is not None:
        stream_thread.join()
    drawing_modes = {
        "Depth Mode": False,
        "Face Detection": False,
        "Face Recognition": False,
        "Face Emotions": False,
        "Face Mesh": False,
        "Object Detection": False,
        "Hand Landmarks": False,
        "Pose Landmarks": False,
    }
    return True


if __name__ == "__main__":
    pass
