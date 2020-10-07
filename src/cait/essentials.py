""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019

"""

import cait.core as core

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
    account_list = core.get_cloud_accounts()
    return {"accounts": account_list}

def get_virtual_processors(processor_type):
    virtual_processors = core.get_virtual_processors(processor_type)
    return {"virtual_processors": virtual_processors}

def get_video_devices():
    return core.get_video_devices()

def get_audio_devices():
    return core.get_audio_devices()

def test_camera(index):
    return core.test_camera(index)

def initialize_component(component_name, useOnline=True, account="default", processor="local"):
    """Initalization function for different components
    
    Arguments:
        component_name {[string]} -- name of the component to be initialized
    
    Keyword Arguments:
        useOnline {bool} -- use online service or not (default: {True})
    
    Returns:
        [bool] -- True if initialization is success, False otherwise
    """    
    if component_name == "vision":
        success, msg = core.initialize_vision(processor)
    elif component_name == "voice":
        success, msg  = core.initialize_voice(useOnline, account)
    elif component_name == "nlp":
        success, msg  = core.initialize_nlp()
    elif component_name == "control":
        success, msg  = core.initialize_control()
    elif component_name == "smart_home":
        success = True
        msg = "OK"
    return success, msg

def change_module_parameters(parameter_name, value):
    core.change_module_parameters(parameter_name, value)

def get_camera_image():
    img = core.get_camera_image()
    if img is not None:
        return img
    else:
        return None

def recognize_face():
    """Recognize the name of person from camera feed. No need to pass in camera feed explicitly at this level.
    
    Returns:
        [dict] -- key: names, values: [coordinates, confidences]
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
    
    Arguments:
        name {[string]} -- name of the person.
    
    Returns:
        [bool] -- return True if adding face is success, False otherwise.
    """    
    if name == None:
        return -1

    success = core.add_person(name)

    return success

def remove_person(name):
    """Remove a specific person from database

    Arguments:
        name {[string]} -- name of the person to remove
    """    
    if name == None:
        return -1

    success = core.remove_person(name)

    return success

def detect_objects():
    """detect the object appearing in camera feed
    
    Returns:
        [list] -- names of the objects
        [list] -- coordinates of objects
    """    
    objects = core.detect_objects()

    if objects is not None:
        names, coordinates = objects
        objects = {"names" : names, "coordinates" : coordinates}
        return objects
    else:
        return None

def listen():
    """Listen to user speech from audio feed captured by microphone.
    
    Returns:
        [string] -- the user speech generated from speech-to-text module.
    """

    text = core.listen()

    if text is not None:
        return text
    else:
        return None

def listen_for_wakeword():
    """Continuously detecting the appeareance of wakeword from the audio stream. Higher priority than the listen() function.
    
    Returns:
        [bool] -- return True if detected wakeword, False otherwise.
    """

    gotWakeWord = core.listen_for_wakeword()

    return gotWakeWord

def say(text, volume=100):
    """Speak the text through speaker at the specific volume.
    
    Arguments:
        text {[string]} -- text to be spoken.
        volume {[int]} -- 0-100.
    
    Returns:
        [bool] -- True if successfully spoken. False otherwise.
    """    
    if text == None:
        return -1

    success = core.say(text)

    return success

def analyse_text(text):
    """Analyse the user speech generated from the listen() function.
    
    Arguments:
        text {[string]} -- user speech.
    
    Returns:
        [dict] -- Contains the intention and entities from the analytics of the user speech.
    """
    if text == None:
        return -1

    topic, condifence, entities = core.analyze(text)

    intention = {"topic" : topic, "confidence" : condifence, "entities" : entities}

    return intention

def control_motor(motor_name, speed, duration):
    """Move robot forward or backward, with specific speed and for specific duration

    Arguments:
        direction {[type]} -- [description]
        speed {[type]} -- [description]
        duration {[type]} -- [description]

    Returns:
        [bool] -- True if successfully moved. False otherwise.
    """    

    success = core.control_motor(motor_name, speed, duration)

    return success

def control_motor_speed_group(operation_list):
    success = core.control_motor_speed_group(operation_list)

    return success

def rotate_motor(motor_name, angle):
    """Rotate robot to a certain angle

    Arguments:
        angle {[int]} -- Roatational angle

    Returns:
        [bool] -- True if successfully moved. False otherwise.
    """    

    success = core.rotate_motor(motor_name, angle)

    return success

def control_motor_degree_group(operation_list):
    success = core.control_motor_degree_group(operation_list)

    return success

def stop_movement():
    """[summary]

    Returns:
        [bool] -- True if successfully stopped. False otherwise.
    """   
    
    return success 

def get_devices(device_type):
    devices = core.get_devices(device_type)
    result = {"devices": devices}

    return result

def control_light(device_name, operation, parameter=None):
    result = core.control_light(device_name, operation, parameter)
    return result

def control_media_player(device_name, operation):
    result = core.control_media_player(device_name, operation)
    return result

def turn_to_person(name):
    """Rotate the robot to face a person, this is a combined usage of recognizeFace() and move() function.

    Arguments:
        name {[string]} -- name of the person that the robot should center to.

    Returns:
        [bool] -- True if successfully turned. False otherwise.
    """    
    return success

def follow_person(name):
    """Move the robot so that it constantly follows a person, this is a combined usage of recognizeFace() and move() function.

    Arguments:
        name {[string]} -- name of the person that the robot should be following.
    
    Returns:
        [bool] -- True if successfully moved. False otherwise.
    """ 
    return success

def greet_person(name, speech):
    """Greet a specific person in a specific way, this is combined usage of recognizeFace() and say() function.

    Arguments:
        name {[sring]} -- name of the person to greet, it can be an actual name, or simply Unknown.
        speech {[string]} -- words to say to the person.

    Returns:
        [bool] -- True if successfully greeted. False otherwise.
    """    
    return success

def ask_for_person_name():
    """Ask for the name of a person appearing in the camera feed, this is a combined usage of say(), listen() and analyseSpeech() function.
    
    Returns:
        [string] -- name of the person.
    """    
    return name

def get_response(text):
    """Generate robot response based on user speech input
    
    Arguments:
        text {[string]} -- Result from listen() function
    
    Returns:
        [string] -- robot response
    """    

    return respone

def control_smart_device(device_name, action):
    """Control the smart devices's state through action.
    
    Arguments:
        device_name {[string]} -- Name of the device recorded in Home assistant
        action {[string]} -- valid action state for the device, as recorded in home assistant.
    
    Returns:
        [bool] -- True if device is successfully controlled. False otherwise.
    """    
    return success
