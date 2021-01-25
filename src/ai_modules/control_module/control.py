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
import bluetooth
import ast

logging.getLogger().setLevel(logging.INFO)

current_hubs = {}
connecting = False

def connect_to_ev3(hub_address):
    try:
        ev3_conn = rpyc.classic.connect(hub_address)
        return ev3_conn
    except:
        logging.warning("No ev3 hub connected")
        return None

def connect_to_robot_inventor(hub_address):
    try:
        robot_inventor_hub = bluetooth.find_service(address=hub_address)
        port = robot_inventor_hub[2]["port"]
        host = robot_inventor_hub[2]["host"]
        robot_inventor_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        logging.warning("Connecting to: " + str(port) + ", " + str(host))
        robot_inventor_sock.connect((host, port))
        
        robot_inventor_sock.settimeout(5)
        robot_inventor_sock.send(b'\x03')
        robot_inventor_sock.send(b'import hub\x0D')
        dump = robot_inventor_sock.recv(102400)
        time.sleep(0.5)
        return robot_inventor_sock
    except:
        logging.warning("No spike hub connected")
        return None

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
    global current_hubs
    global connecting
    data = msg.payload.decode()
    logging.info("Control data: " + data)
    if data.find("Control Up") != -1:
        controlUp = False
        hub_addresses = ast.literal_eval(data[data.find(",")+1:])
        connection_success = True
        for hub in hub_addresses:
            hub_type = hub[0:hub.find(":")]
            hub_address = hub[hub.find(":")+2:]
            if hub not in current_hubs and not connecting:
                connecting = True
                connection = None
                if hub_type == "EV3":
                    ev3_connection = connect_to_ev3(hub_address)
                    ev3_motor = ev3_connection.modules['ev3dev2.motor']
                    ev3_sensor = ev3_connection.modules['ev3dev2.sensor']
                    ev3_sound = ev3_connection.modules['ev3dev2.sound']
                    connection = ["EV3", ev3_connection, ev3_motor, ev3_sensor, ev3_sound]
                elif hub_type == "Robot Inventor":
                    robot_inventor_connection = connect_to_robot_inventor(hub_address)
                    connection = ["Robot Inventor", robot_inventor_connection]
                if connection is not None:
                    current_hubs[hub] = connection
                    logging.warning("Connected to: " + hub_type + " at address: " + hub_address)
                else:
                    logging.warning("Failed Connecting to: " + hub_type + " at address: " + hub_address)
                    connection_success = False
                connecting = False
        if connection_success:
            controlUp = True
    else:
        if controlUp:
            if data.find("move") != -1:
                hub_name_begin_idx = data.find("hub") + 4
                hub_name_end_idx = data.find(" move", hub_name_begin_idx)
                motor_begin_idx = data.find("move") + 5
                motor_end_idx = data.find(" ", motor_begin_idx)
                speed_begin_idx = motor_end_idx + 1
                speed_end_idx = data.find(" ", speed_begin_idx)
                duration_begin_idx = speed_end_idx + 1
                hub_name = data[hub_name_begin_idx:hub_name_end_idx]
                motor = data[motor_begin_idx:motor_end_idx]
                speed = int(data[speed_begin_idx:speed_end_idx])
                duration = int(data[duration_begin_idx:])
                move(hub_name, motor, speed, duration)
            elif data.find("motor_speed_group") != -1:
                operation_list = data[data.find("motor_speed_group") + 18:]
                move_group(operation_list)
            elif data.find("motor_degree_group") != -1:
                operation_list = data[data.find("motor_degree_group") + 19:]
                rotate_group(operation_list)
            elif data.find("rotate") != -1:
                hub_name_begin_idx = data.find("hub") + 4
                hub_name_end_idx = data.find(" rotate", hub_name_begin_idx)
                motor_begin_idx = data.find("rotate") + 7
                motor_end_idx = data.find(" ", motor_begin_idx)
                angle_begin_idx = motor_end_idx + 1
                hub_name = data[hub_name_begin_idx:hub_name_end_idx]
                motor = data[motor_begin_idx:motor_end_idx]
                degree = int(data[angle_begin_idx:])
                setPosition(hub_name, motor, degree)
            # elif data.find("speak") != -1:
            #     sentence = data[data.find(",")+1:]
            #     speak(sentence)

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


def is_robot_inventor_port_error(byte_msg):
    msg = byte_msg.decode("utf-8") 
    logging.warning("Return Msg: " + msg)
    logging.warning(byte_msg)
    if msg.find("port") != -1 and msg.find("AttributeError") != -1 and msg.find("NoneType") != -1:
        logging.warning("port error occurred")
        return True
    else:
        logging.warning("port loaction: " + str(msg.find("port")))
        logging.warning("attribute loaction: " + str(msg.find("AttributeError")))
        logging.warning("none loaction: " + str(msg.find("NoneType")))
        return False


def translate_motor_name(hub, motor_name):
    motor = None
    hub_type = hub[0]
    if motor_name == "motor_A":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_A
        elif hub_type == "Robot Inventor":
            motor = "A"
    elif motor_name == "motor_B":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_B
        elif hub_type == "Robot Inventor":
            motor = "B"
    elif motor_name == "motor_C":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_C
        elif hub_type == "Robot Inventor":
            motor = "C"
    elif motor_name == "motor_D":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_D
        elif hub_type == "Robot Inventor":
            motor = "D"
    elif motor_name == "motor_E":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_D
        elif hub_type == "Robot Inventor":
            motor = "E"
    elif motor_name == "motor_F":
        if hub_type == "EV3":
            motor = hub[2].OUTPUT_D
        elif hub_type == "Robot Inventor":
            motor = "F"
    return motor

def setPosition(hub_name, motor_name, position):
    global current_hubs
    logging.info("Rotating motor now")
    hub = current_hubs[hub_name]
    hub_type = hub[0]
    motor = translate_motor_name(hub, motor_name)
    if hub_type == "EV3":
        try:
            this_motor = hub[2].Motor(motor)
            this_motor.on_for_degrees(100, position)
        except:
            logging.warning("Time out occured, Hub disconnected")
            client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected motor port not working", qos=1)
            del current_hubs[hub_name]
            return
    elif hub_type == "Robot Inventor":
        speed = 100
        if position < 0:
            speed = -100
        degree = abs(position)
        msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_for_degrees(' + str(degree).encode('utf-8') + b', ' + str(speed).encode('utf-8') + b')\x0D'
        try:
            hub[1].send(msg_individual)
            rec = hub[1].recv(102400)
            logging.warning(rec)
            if is_robot_inventor_port_error(rec):
                client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                return
        except:
            logging.warning("Time out occured, Hub disconnected")
            client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
            del current_hubs[hub_name]
            return
        time.sleep(0.1)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating")

def rotate_group(operation_list):
    global current_hubs
    operation_list = json.loads(operation_list)['operation_list']
    largest_angle = 0
    for operation in operation_list:
        hub = current_hubs[operation['hub_name']]
        hub_type = hub[0]
        motor = translate_motor_name(hub, operation['motor_name'])
        angle = int(operation['angle'])
        if abs(angle) > largest_angle:
            largest_angle = abs(angle)
        if hub_type == "EV3":
            try:
                this_motor = hub[2].Motor(motor)
                this_motor.on_for_degrees(100, angle, block=False)
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected motor port not working", qos=1)
                del current_hubs[operation['hub_name']]
                return
        elif hub_type == "Robot Inventor":
            speed = 100
            if angle< 0:
                speed = -100
            degree = abs(angle)
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_for_degrees(' + str(degree).encode('utf-8') + b', ' + str(speed).encode('utf-8') + b')\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                logging.warning(rec)
                if is_robot_inventor_port_error(rec):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                    return
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                del current_hubs[operation['hub_name']]
                return
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

def move(hub_name, motor_name, speed=1, duration=0):
    global current_hubs
    hub = current_hubs[hub_name]
    hub_type = hub[0]
    motor = translate_motor_name(hub, motor_name)
    if motor is not None:
        logging.info("Moving motor: " + motor_name)
        if hub_type == "EV3":
            try:
                this_motor = hub[2].Motor(motor)
                this_motor.on(speed)
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected or motor port not working", qos=1)
                del current_hubs[hub_name]
                return
        elif hub_type == "Robot Inventor":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(speed).encode('utf-8') + b', 100)\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                if is_robot_inventor_port_error(rec):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                    return
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
                del current_hubs[hub_name]
                return
        start_time = time.time()
        while time.time() - start_time <= duration:
            time.sleep(0.03)
        if hub_type == "EV3":
            try:
                this_motor.stop()
                this_motor.reset()
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected motor port not working", qos=1)
                del current_hubs[hub_name]
                return
        elif hub_type == "Robot Inventor":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.brake()\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                logging.warning(rec)
                if is_robot_inventor_port_error(rec):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                    return
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
                del current_hubs[hub_name]
                return
        time.sleep(0.03)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done moving")

def move_group(operation_list):
    global current_hubs
    operation_list = json.loads(operation_list)['operation_list']
    hub_name_list = []
    hub_list = []
    motor_list = []
    duration_list = []
    largest_duration = 0
    all_motor_moved = True
    for operation in operation_list:
        hub = current_hubs[operation['hub_name']]
        hub_name_list.append(operation['hub_name'])
        hub_type = hub[0]
        hub_list.append(hub)
        motor = translate_motor_name(hub, operation['motor_name'])
        motor_list.append(motor)
        speed = int(operation['speed'])
        duration = int(operation['duration'])
        if duration > largest_duration:
            largest_duration = duration
        duration_list.append(duration)
        if hub_type == "EV3":
            try:
                this_motor = hub[2].Motor(motor)
                this_motor.on(speed, block=False)
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected motor port not working", qos=1)
                del current_hubs[operation['hub_name']]
                del hub_name_list[-1]
                del hub_list[-1]
                del motor_list[-1]
                del duration_list[-1]
                all_motor_moved = False
                break
        elif hub_type == "Robot Inventor":
            msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(speed).encode('utf-8') + b', 100)\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                logging.warning(rec)
                if is_robot_inventor_port_error(rec):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                    break
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                del current_hubs[operation['hub_name']]
                del hub_name_list[-1]
                del hub_list[-1]
                del motor_list[-1]
                del duration_list[-1]
                all_motor_moved = False
                break
    start_time = time.time()
    while time.time() - start_time < largest_duration:
        remaining_duration_list = []
        for i in range(0,len(duration_list)):
            if time.time() - start_time >= duration_list[i]:
                hub = hub_list[i]
                hub_type = hub[0]
                if hub_type == "EV3":
                    try:
                        this_motor = hub[2].Motor(motor_list[i])
                        this_motor.stop()
                    except:
                        logging.warning("Time out occured, Hub disconnected")
                        client_control.publish("cait/module_states", "Control Exception: " + hub_name_list[i] + " Disconnected motor port not working", qos=1)
                        del current_hubs[hub_name_list[i]]
                        all_motor_moved = False
                elif hub_type == "Robot Inventor":
                    msg_individual = b'hub.port.' + motor_list[i].encode('utf-8') + b'.motor.brake()\x0D'
                    try:
                        hub[1].send(msg_individual)
                        rec = hub[1].recv(102400)
                        logging.warning(rec)
                        if is_robot_inventor_port_error(rec):
                            client_control.publish("cait/module_states", "Control Exception: port " + motor_list[i] + " can not be controlled, please check your setup", qos=1)
                            all_motor_moved = False
                    except:
                        logging.warning("Time out occured, Hub disconnected")
                        client_control.publish("cait/module_states", "Control Exception: " + hub_name_list[i] + " Disconnected", qos=1)
                        del current_hubs[hub_name_list[i]]
                        all_motor_moved = False
            else:
                remaining_duration_list.append(duration_list[i])
        duration_list = remaining_duration_list
        time.sleep(0.1)
    for m in range(0, len(motor_list)):
        hub = hub_list[m]
        hub_type = hub[0]
        if hub_type == "EV3":
            try:
                this_motor = hub[2].Motor(motor_list[m])
                this_motor.stop()
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name_list[m] + " Disconnected motor port not working", qos=1)
                del current_hubs[hub_name_list[m]]
                all_motor_moved = False
        elif hub_type == "Robot Inventor":
            msg_individual = b'hub.port.' + motor_list[m].encode('utf-8') + b'.motor.brake()\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                logging.warning(rec)
                if is_robot_inventor_port_error(rec):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor_list[m] + " can not be controlled, please check your setup", qos=1)
                    all_motor_moved = False
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name_list[m] + " Disconnected", qos=1)
                del current_hubs[hub_name_list[m]]
                all_motor_moved = False
    time.sleep(0.03)
    if all_motor_moved:
        client_control.publish("cait/module_states", "Control Done", qos=1)
        logging.info("Done moving group")

# def play_sound(sound_obj):
#     if current_hub == "ev3":
#         speaker = ev3_sound.Sound()
#         speaker.play(sound_obj)

# def speak(sentence):
#     if current_hub == "ev3":
#         client_control.publish("cait/module_states", "Start Speaking", qos=1)
#         speaker = ev3_sound.Sound()
#         speaker.speak(sentence)
#         client_control.publish("cait/module_states", "Done Speaking", qos=1)

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
