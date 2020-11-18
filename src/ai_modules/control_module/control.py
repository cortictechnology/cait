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

logging.getLogger().setLevel(logging.INFO)

ev3_conn = None
ev3_motor = None

def connect_to_ev3(hub_address):
    global ev3_conn
    global ev3_motor
    try:
        ev3_conn = rpyc.classic.connect(hub_address)
        ev3_motor = ev3_conn.modules['ev3dev2.motor']
        return True
    except:
        print("No ev3 hub connected")
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
            ret = connect_to_ev3(hub_address)
            while not ret:
                ret = connect_to_ev3(hub_address)
                logging.info("EV3 Hub not ready, retrying to connect...")
                time.sleep(5)
            logging.info("Successfully connected to EV3 Hub")
            controlUp = True
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


def translate_motor_name(motor_name):
    global ev3_motor
    motor = None
    if motor_name == "motor_A":
        motor = ev3_motor.OUTPUT_A
    elif motor_name == "motor_B":
        motor = ev3_motor.OUTPUT_B
    elif motor_name == "motor_C":
        motor = ev3_motor.OUTPUT_C
    elif motor_name == "motor_D":
        motor = ev3_motor.OUTPUT_D
    return motor

def setPosition(motor_name, position):
    logging.info("Rotating motor now")
    motor = translate_motor_name(motor_name)
    this_motor = ev3_motor.Motor(motor)
    this_motor.on_for_degrees(100, position)
    # if connected_control_board == "brickpi3":
    #     BP.set_motor_position(motor, position)
    #     BP.offset_motor_encoder(motor, BP.get_motor_encoder(motor))
    #     if abs(position) <= 400:
    #         time.sleep(0.5)
    #     elif abs(position) <= 800:
    #         time.sleep(0.9)
    #     elif abs(position) <= 1200:
    #         time.sleep(1.5)
    #     else:
    #         time.sleep(2)
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
        this_motor = ev3_motor.Motor(motor)
        this_motor.on_for_degrees(100, angle. block=False)
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
    global ev3_motor
    motor = translate_motor_name(motor_name)
    if motor is not None:
        logging.info("Moving motor: " + motor_name)
        this_motor = ev3_motor.Motor(motor)
        this_motor.on(speed)
        start_time = time.time()
        while time.time() - start_time <= duration:
            time.sleep(0.03)
        this_motor.stop()
        this_motor.reset()
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
        this_motor = ev3_motor.Motor(motor)
        this_motor.on(speed, block=False)
    start_time = time.time()
    while time.time() - start_time < largest_duration:
        for i in range(0,len(duration_list)):
            if time.time() - start_time >= duration_list[i]:
                this_motor = ev3_motor.Motor(motor_list[i])
                this_motor.stop()
    for m in range(0, len(motor_list)):
        this_motor = ev3_motor.Motor(motor_list[m])
        this_motor.stop()
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
