""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

import rpyc
import logging
import paho.mqtt.client as mqtt
import time
import json
import threading
import serial

logging.getLogger().setLevel(logging.INFO)

ev3_conn = None
ev3_motor = None
ev3_sound = None

spike_conn = None

current_hub = None

def connect_to_ev3(hub_address):
    global ev3_conn
    global ev3_motor
    global ev3_sound
    global current_hub
    try:
        ev3_conn = rpyc.classic.connect(hub_address)
        ev3_motor = ev3_conn.modules['ev3dev2.motor']
        ev3_sound = ev3_conn.modules['ev3dev2.sound']
        current_hub = "ev3"
        return True
    except:
        logging.warning("No ev3 hub connected")
        return False

def connect_to_spike(hub_address):
    global spike_conn
    global current_hub
    try:
        spike_conn = serial.Serial(hub_address, 115200)
        spike_conn.write(b'\x03')
        spike_conn.write(b'import hub\x0D')
        current_hub = "spike"
        time.sleep(0.5)
        return True
    except:
        logging.warning("No spike hub connected")
        return False

currentRotation = 0
controlUp = False

def connectMQTT(client):
    try:
        client.connect("127.0.0.1",1883,60)
        logging.info("Connected to broker")
        return 0
    except:
        logging.info("Broker not up yet, retrying...")
        return -1

def on_connect_control(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("cait/motor_control")

def on_message_control(client, userdata, msg):
    global currentRotation
    global controlUp
    data = msg.payload.decode()
    logging.info("Control data: " + data)
    if data.find("Control Up") != -1:

        if not controlUp:
            hub_address = data[data.find(",")+1:]
            logging.info("Hub address: " + hub_address)
            if hub_address.find("ev3") != -1:
                ret = connect_to_ev3(hub_address)
            else:
                ret = connect_to_spike(hub_address)
            while not ret:
                if hub_address.find("ev3") != -1:
                    ret = connect_to_ev3(hub_address)
                else:
                    ret = connect_to_spike(hub_address)
                logging.info("Hub not ready, retrying to connect...")
                time.sleep(5)
            logging.info("Successfully connected to Control Hub")
            controlUp = True
    else:
        if controlUp:
            if data.find("move") != -1:
                motor_begin_idx = data.find("move") + 5
                motor_end_idx = data.find(" ", motor_begin_idx)
                speed_begin_idx = motor_end_idx + 1
                speed_end_idx = data.find(" ", speed_begin_idx)
                duration_begin_idx = speed_end_idx + 1
                motor = data[motor_begin_idx:motor_end_idx]
                speed = int(data[speed_begin_idx:speed_end_idx])
                duration = int(data[duration_begin_idx:])
                move(motor, speed, duration)
            elif data.find("motor_speed_group") != -1:
                operation_list = data[data.find("motor_speed_group") + 18:]
                move_group(operation_list)
            elif data.find("motor_degree_group") != -1:
                operation_list = data[data.find("motor_degree_group") + 19:]
                rotate_group(operation_list)
            elif data.find("rotate") != -1:
                motor_begin_idx = data.find("rotate") + 7
                motor_end_idx = data.find(" ", motor_begin_idx)
                angle_begin_idx = motor_end_idx + 1
                motor = data[motor_begin_idx:motor_end_idx]
                degree = int(data[angle_begin_idx:])
                setPosition(motor, degree)
            elif data.find("speak") != -1:
                sentence = data[data.find(",")+1:]
                speak(sentence)

client_control = mqtt.Client()
client_control.on_connect = on_connect_control
client_control.on_message = on_message_control
ret = connectMQTT(client_control)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_control)

client_heartbeat = mqtt.Client()
ret = connectMQTT(client_heartbeat)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_heartbeat)
client_heartbeat.loop_start()


def translate_motor_name(motor_name):
    global ev3_motor
    global current_hub
    motor = None
    if motor_name == "motor_A":
        if current_hub == "ev3":
            motor = ev3_motor.OUTPUT_A
        elif current_hub == "spike":
            motor = "A"
    elif motor_name == "motor_B":
        if current_hub == "ev3":
            motor = ev3_motor.OUTPUT_B
        elif current_hub == "spike":
            motor = "B"
    elif motor_name == "motor_C":
        if current_hub == "ev3":
            motor = ev3_motor.OUTPUT_C
        elif current_hub == "spike":
            motor = "C"
    elif motor_name == "motor_D":
        if current_hub == "ev3":
            motor = ev3_motor.OUTPUT_D
        elif current_hub == "spike":
            motor = "D"
    return motor

def setPosition(motor_name, position):
    global current_hub
    global ev3_motor
    global spike_conn
    logging.info("Rotating motor now")
    motor = translate_motor_name(motor_name)
    if current_hub == "ev3":
        this_motor = ev3_motor.Motor(motor)
        this_motor.on_for_degrees(100, position)
    elif current_hub == "spike":
        speed = 100
        if position < 0:
            speed = -100
        degree = abs(position)
        msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_for_degrees(' + str(degree).encode('utf-8') + b', ' + str(speed).encode('utf-8') + b')\x0D'
        spike_conn.write(msg_individual)
        time.sleep(0.1)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating")

def rotate_group(operation_list):
    global current_hub
    global ev3_motor
    global spike_conn
    operation_list = json.loads(operation_list)['operation_list']
    largest_angle = 0
    for operation in operation_list:
        motor = translate_motor_name(operation['motor_name'])
        angle = int(operation['angle'])
        if abs(angle) > largest_angle:
            largest_angle = abs(angle)
        if current_hub == "ev3":
            this_motor = ev3_motor.Motor(motor)
            this_motor.on_for_degrees(100, angle, block=False)
        elif current_hub == "spike":
            speed = 100
            if angle< 0:
                speed = -100
            degree = abs(angle)
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_for_degrees(' + str(degree).encode('utf-8') + b', ' + str(speed).encode('utf-8') + b')\x0D'
            spike_conn.write(msg_individual)
    if largest_angle <= 400:
        time.sleep(0.5)
    elif largest_angle <= 800:
        time.sleep(0.9)
    elif largest_angle <= 1200:
        time.sleep(1.5)
    else:
        time.sleep(2)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating group")

def move(motor_name, speed=1, duration=0):
    global current_hub
    global ev3_motor
    global spike_conn
    motor = translate_motor_name(motor_name)
    if motor is not None:
        logging.info("Moving motor: " + motor_name)
        if current_hub == "ev3":
            this_motor = ev3_motor.Motor(motor)
            this_motor.on(speed)
        elif current_hub == "spike":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(speed).encode('utf-8') + b', 100)\x0D'
            spike_conn.write(msg_individual)
        start_time = time.time()
        while time.time() - start_time <= duration:
            time.sleep(0.03)
        if current_hub == "ev3":
            this_motor.stop()
            this_motor.reset()
        elif current_hub == "spike":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.brake()\x0D'
            spike_conn.write(msg_individual)
        time.sleep(0.03)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done moving")

def move_group(operation_list):
    global current_hub
    global ev3_motor
    global spike_conn
    operation_list = json.loads(operation_list)['operation_list']
    motor_list = []
    duration_list = []
    largest_duration = 0
    for operation in operation_list:
        motor = translate_motor_name(operation['motor_name'])
        motor_list.append(motor)
        speed = int(operation['speed'])
        duration = int(operation['duration'])
        if duration > largest_duration:
            largest_duration = duration
        duration_list.append(duration)
        if current_hub == "ev3":
            this_motor = ev3_motor.Motor(motor)
            this_motor.on(speed, block=False)
        elif current_hub == "spike":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(speed).encode('utf-8') + b', 100)\x0D'
            spike_conn.write(msg_individual)
    start_time = time.time()
    while time.time() - start_time < largest_duration:
        remaining_duration_list = []
        for i in range(0,len(duration_list)):
            if time.time() - start_time >= duration_list[i]:
                if current_hub == "ev3":
                    this_motor = ev3_motor.Motor(motor_list[i])
                    this_motor.stop()
                elif current_hub == "spike":
                    msg_individual = b'hub.port.' + motor_list[i].encode('utf-8') + b'.motor.brake()\x0D'
                    spike_conn.write(msg_individual)
            else:
                remaining_duration_list.append(duration_list[i])
        duration_list = remaining_duration_list
        time.sleep(0.1)
    for m in range(0, len(motor_list)):
        if current_hub == "ev3":
            this_motor = ev3_motor.Motor(motor_list[m])
            this_motor.stop()
        elif current_hub == "spike":
            msg_individual = b'hub.port.' + motor_list[m].encode('utf-8') + b'.motor.brake()\x0D'
            spike_conn.write(msg_individual)
    time.sleep(0.03)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done moving group")

def play_sound(sound_obj):
    if current_hub == "ev3":
        speaker = ev3_sound.Sound()
        speaker.play(sound_obj)

def speak(sentence):
    if current_hub == "ev3":
        client_control.publish("cait/module_states", "Start Speaking", qos=1)
        speaker = ev3_sound.Sound()
        speaker.speak(sentence)
        client_control.publish("cait/module_states", "Done Speaking", qos=1)

def heartbeat_func():
    global controlUp
    global client_heartbeat
    while True:
        if controlUp:
            client_heartbeat.publish("cait/module_states", "Control Up", qos=1)
        else:
            client_heartbeat.publish("cait/module_states", "Control Down", qos=1)
        time.sleep(1)

def main():
    heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
    heartbeat_thread.start()
    client_control.loop_forever()

if __name__ == "__main__":
    main()
