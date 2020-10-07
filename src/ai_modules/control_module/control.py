""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

import brickpi3
import logging
import paho.mqtt.client as mqtt
import time
import json
import threading

logging.getLogger().setLevel(logging.INFO)

connected_control_board = ""

try:
    BP = brickpi3.BrickPi3()
    connected_control_board = "brickpi3"
except:
    print("No brickpi connected")

if connected_control_board == "brickpi3":
    BP.reset_all()

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
    if data == "Control Up" and not controlUp:
        controlUp = True
    elif data == "Init":
        init()
    elif data == "reset":
        BP.reset_all()
    elif data.find("move") != -1:
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

def init():
    if connected_control_board == "brickpi3":
        BP.reset_all()
        BP.offset_motor_encoder(BP.PORT_A, BP.get_motor_encoder(BP.PORT_A))
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_B))
        BP.offset_motor_encoder(BP.PORT_C, BP.get_motor_encoder(BP.PORT_C))
        BP.offset_motor_encoder(BP.PORT_B, BP.get_motor_encoder(BP.PORT_D))
        time.sleep(0.1)
    print("Done Initiialization")

def translate_motor_name(motor_name):
    motor = None
    if connected_control_board == "brickpi3":
        if motor_name == "motor_A":
            motor = BP.PORT_A
        elif motor_name == "motor_B":
            motor = BP.PORT_B
        elif motor_name == "motor_C":
            motor = BP.PORT_C
        elif motor_name == "motor_D":
            motor = BP.PORT_D

    return motor

def setPosition(motor_name, position):
    logging.info("Rotating motor now")
    motor = translate_motor_name(motor_name)
    if connected_control_board == "brickpi3":
        BP.set_motor_position(motor, position)
        BP.offset_motor_encoder(motor, BP.get_motor_encoder(motor))
        if abs(position) <= 400:
            time.sleep(0.5)
        elif abs(position) <= 800:
            time.sleep(0.9)
        elif abs(position) <= 1200:
            time.sleep(1.5)
        else:
            time.sleep(2)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating")

def rotate_group(operation_list):
    operation_list = json.loads(operation_list)['operation_list']
    largest_angle = 0
    for operation in operation_list:
        motor = translate_motor_name(operation['motor_name'])
        angle = int(operation['angle'])
        if abs(angle) > largest_angle:
            largest_angle = abs(angle)
        if connected_control_board == "brickpi3":
            BP.set_motor_position(motor, angle)
            BP.offset_motor_encoder(motor, BP.get_motor_encoder(motor))
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
    motor = translate_motor_name(motor_name)
    if motor is not None:
        logging.info("Moving motor: " + motor_name)
        if connected_control_board == "brickpi3":
            BP.set_motor_power(motor, speed)
        start_time = time.time()
        while time.time() - start_time <= duration:
            time.sleep(0.03)
        if connected_control_board == "brickpi3":
            BP.set_motor_power(motor, 0)
            BP.offset_motor_encoder(motor, BP.get_motor_encoder(motor))
        time.sleep(0.03)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done moving")

def move_group(operation_list):
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
        if connected_control_board == "brickpi3":
            BP.set_motor_power(motor, speed)
    start_time = time.time()
    while time.time() - start_time < largest_duration:
        for i in range(0,len(duration_list)):
            if time.time() - start_time >= duration_list[i]:
                if connected_control_board == "brickpi3":
                    BP.set_motor_power(motor_list[i], 0)
    for m in range(0, len(motor_list)):
        BP.set_motor_power(motor_list[m], 0)
    time.sleep(0.03)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done moving group")

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
