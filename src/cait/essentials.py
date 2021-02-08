""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""

import cait.core as core
import time
import logging

logging.getLogger().setLevel(logging.INFO)

"""
Assumptions:
    1. Single USB webcam (supported ones)
    2. 3.5mm audio jack speaker
    3. Microphone integrated with webcam
    4. Default one database for people. person name is folder name.
    5. Faces and objects are tracked implicitly
    6. Need to teach list and dictionary knowledge
    7. return None if error occurred, otherwise empty return is normal if nothing detected
"""

def get_cloud_accounts():
    """Get a list of google cloud servie account

    Returns:
        account_list (list): List of google cloud servie account
    """ 
    account_list = core.get_cloud_accounts()
    return {"accounts": account_list}

def get_nlp_models():
    model_list = core.get_nlp_models()
    return {"models": model_list}


def get_video_devices():
    """Get a list of connected camera device

    Returns:
        video_device_list (list): List of camera device
    """ 
    return core.get_video_devices()

def get_audio_devices():
    """Get a list of connected audio device

    Returns:
        (list): List of audio device
    """  
    return core.get_audio_devices()


def get_control_devices():
    """Get a list of connected control device

    Returns:
        (list): List of control device
    """  
    return core.get_control_devices()


def test_camera(index):
    """Open the camera device with specific index, test for its connetion

    Parameters:
        index (int): index of the camera device
    
    Returns:
        (bool): True if success, False otherwise
    """    
    return core.test_camera(index)

def initialize_component(component_name, mode="online", account="default", processor="local", language="english"):
    """Initalization function for different components
    
    Parameters:
        component_name (string): name of the component to be initialized
    
    Keyword Parameters:
        useOnline {bool}: use online service or not (default: {True})
    
    Returns:
        (bool): True if initialization is success, False otherwise
    """    
    if component_name == "vision":
        success, msg = core.initialize_vision(processor, account)
    elif component_name == "voice":
        if mode == "online":
            mode = True
        else:
            mode = False
        success, msg  = core.initialize_voice(mode, account, language)
    elif component_name == "nlp":
        success, msg  = core.initialize_nlp(mode)
    elif component_name == "control":
        success, msg  = core.initialize_control(mode)
    elif component_name == "smart_home":
        success = True
        msg = "OK"
    return success, msg


def deactivate_vision():
    """Deactivate the vision component

    Returns:
        (Bool): True if deactivate successfullt, False otherwise
    """  
    return core.deactivate_vision()


def deactivate_voice():
    """Deactivate the voice component

    Returns:
        (Bool): True if deactivate successfullt, False otherwise
    """  
    return core.deactivate_voice()


def reset_modules():
    """Reset all module states

    Returns:
        (Bool): True if reset successfullt, False otherwise
    """  
    return core.reset_modules()


def change_module_parameters(parameter_name, value):
    """Generic function for setting ai module parameters
    Parameters:
        parameter_name (string): name of prarmeter
        value {float}: value of parameter
    
    """    
    core.change_module_parameters(parameter_name, value)


def sleep(time_value):
    """Wrapper function for the time.sleep() function
    Parameters:
        time_value {int}: sleep time in second
    
    """  
    time.sleep(time_value)
    return True

def get_camera_image():
    """Development test function, retrieve one camera image
    
    Returns:
        (mat): cv2 image
    """
    img = core.get_camera_image()
    if img is not None:
        return img
    else:
        return None

def recognize_face():
    """Recognize the name of person from camera feed. No need to pass in camera feed explicitly at this level.
    
    Returns:
        (dict): key: names, values: (coordinates, confidences)
    """    

    name = core.recognize_face()
    #print("NAME*************", name)
    coordinate = core.get_person_face_location(name)

    if name is not None and coordinate is not None:
        people = {"name" : name, "coordinate" : coordinate}
        return people
    else:
        return None

def add_person(name=None):
    """Add a new person into face database, associate the name with the person's face image captured from camera feed.
    
    Parameters:
        name (string): name of the person.
    
    Returns:
        (bool): return True if adding face is success, False otherwise.
    """    
    if name == None:
        return -1

    success = core.add_person(name)

    return success

def remove_person(name):
    """Remove a specific person from database

    Parameters:
        name (string): name of the person to remove
    """    
    if name == None:
        return -1

    success = core.remove_person(name)

    return success

def detect_objects():
    """detect the object appearing in camera feed
    
    Returns:
        (list): names of the objects
        (list): coordinates of objects
    """    
    objects = core.detect_objects()

    if objects is not None:
        names, coordinates = objects
        objects = {"names" : names, "coordinates" : coordinates}
        return objects
    else:
        return None

def classify_image():
    """Classify the current camera feed into an image label
    
    Returns:
        (list): top 5 possible image types
    """    
    names = core.classify_image()

    if names is not None:
        names = {"names" : names}
        return names
    else:
        return None

def listen():
    """Listen to user speech from audio feed captured by microphone.
    
    Returns:
        (string): the user speech generated from speech-to-text module.
    """

    success, text = core.listen()

    return success, text

def listen_for_wakeword():
    """Continuously detecting the appeareance of wakeword from the audio stream. Higher priority than the listen() function.
    
    Returns:
        (bool): return True if detected wakeword, False otherwise.
    """

    gotWakeWord = core.listen_for_wakeword()

    return gotWakeWord

def say(text):
    """Speak the text through speaker at the specific volume.
    
    Parameters:
        text (string): text to be spoken.
        volume (int): 0-100.
    
    Returns:
        (bool): True if successfully spoken. False otherwise.
    """    
    if text == None:
        return -1

    success = core.say(text)

    return success

def analyse_text(text):
    """Analyse the user speech generated from the listen() function.
    
    Parameters:
        text (string): user speech.
    
    Returns:
        (dict): Contains the intention and entities from the analytics of the user speech.
    """
    if text == None:
        return -1

    topic, condifence, entities = core.analyze(text)

    intention = {"topic" : topic, "confidence" : condifence, "entities" : entities}

    return intention

def control_motor(hub_name, motor_name, speed, duration):
    """Move robot forward or backward, with specific speed and for specific duration

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        speed (int): 0-100
        duration (int): 0 - inf

    Returns:
        (bool): True if successfully moved. False otherwise.
    """    

    success, msg = core.control_motor(hub_name, motor_name, speed, duration)

    return success, msg

def control_motor_group(operation_list):
    """Move a group of motors together

    Parameters:
        operation_list (list): A list of operation in string, refer to code generated from the visual programming interface

    Returns:
        (bool): True if successfully moved. False otherwise.
    """ 

    success, msg = core.control_motor_group(operation_list)

    return success, msg

def rotate_motor(hub_name, motor_name, angle):
    """Rotate robot to a certain angle

    Parameters:
        motor_name (string): Name of motor to control, currently, only support "motor_A", "motor_B", "motor_C", "motor_D" corresponding to BrickPi ports
        angle (int): Roatational angle

    Returns:
        (bool): True if successfully moved. False otherwise.
    """    

    success, msg = core.rotate_motor(hub_name, motor_name, angle)

    return success, msg


def get_devices(device_type):
    """Get a list of smart devices in the local network

    Returns:
        (list): List of smart devices in the local network
    """ 
    devices = core.get_devices(device_type)
    result = {"devices": devices}

    return result

def control_light(device_name, operation, parameter=None):
    """Control the operation of a smart light device.

    Parameters:
        device_name (string): name of smart light device.
        operation (string): operation, currently supporting "turn_on",  "turn_off", "toggle", "color_name", "brightness_pct".
        parameter {}: any parameter for the operation.
 
    Returns:
        (bool): True if successfully sent command to homeassistant. False otherwise.
    """ 
    result = core.control_light(device_name, operation, parameter)
    return result

def control_media_player(device_name, operation):
    """Control the operation of a smart media player.

    Parameters:
        device_name (string): name of smart media player.
        operation (string): operation, currently supporting "media_play",  "media_pause", "volume_up", "volume_down".
 
    Returns:
        (bool): True if successfully sent command to homeassistant. False otherwise.
    """ 
    result = core.control_media_player(device_name, operation)
    return result

def turn_to_person(name):
    """Rotate the robot to face a person, this is a combined usage of recognizeFace() and move() function. Not implemented.

    Parameters:
        name (string): name of the person that the robot should center to.

    Returns:
        (bool): True if successfully turned. False otherwise.
    """    
    success = True
    return success

def follow_person(name):
    """Move the robot so that it constantly follows a person, this is a combined usage of recognizeFace() and move() function. Not implemented.

    Parameters:
        name (string): name of the person that the robot should be following.
    
    Returns:
        (bool): True if successfully moved. False otherwise.
    """ 
    success = True
    return success

def greet_person(name, speech):
    """Greet a specific person in a specific way, this is combined usage of recognizeFace() and say() function. Not implemented.

    Parameters:
        name (sring): name of the person to greet, it can be an actual name, or simply Unknown.
        speech (string): words to say to the person.

    Returns:
        (bool): True if successfully greeted. False otherwise.
    """    
    success = True
    return success

def ask_for_person_name():
    """Ask for the name of a person appearing in the camera feed, this is a combined usage of say(), listen() and analyseSpeech() function. Not implemented.
    
    Returns:
        (string): name of the person.
    """    
    name = ""
    return name

def get_response(text):
    """Generate robot response based on user speech input. Not implemented.
    
    Parameters:
        text (string): Result from listen() function
    
    Returns:
        (string): robot response
    """    
    respone = ""
    return respone

def control_smart_device(device_name, action):
    """Control the smart devices's state through action. Not implemented.
    
    Parameters:
        device_name (string): Name of the device recorded in Home assistant
        action (string): valid action state for the device, as recorded in home assistant.
    
    Returns:
        (bool): True if device is successfully controlled. False otherwise.
    """    
    success = True
    return success
