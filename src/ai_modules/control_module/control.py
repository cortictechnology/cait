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
        time.sleep(1)
        robot_inventor_sock.settimeout(5)
        robot_inventor_sock.send(b'\x03')
        robot_inventor_sock.send(b'import hub\x0D')
        time.sleep(0.5)
        dump = robot_inventor_sock.recv(102400)
        time.sleep(0.5)
        logging.warning("Dump message: " + str(dump))
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
        hub_addresses = ast.literal_eval(data[data.find(",")+1:])
        connection_success = True
        for hub in hub_addresses:
            hub_type = hub[0:hub.find(":")]
            hub_address = hub[hub.find(":")+2:]
            if hub not in current_hubs and not connecting:
                controlUp = False
                connecting = True
                connection = None
                if hub_type == "EV3":
                    ev3_connection = connect_to_ev3(hub_address)
                    retry_count = 0
                    while ev3_connection is None:
                        ev3_connection = connect_to_ev3(hub_address)
                        retry_count = retry_count + 1
                        if retry_count > 3:
                            logging.warning("Exceed retry time")
                            break
                    if ev3_connection is not None:
                        ev3_motor = ev3_connection.modules['ev3dev2.motor']
                        ev3_sensor = ev3_connection.modules['ev3dev2.sensor']
                        ev3_sound = ev3_connection.modules['ev3dev2.sound']
                        connection = ["EV3", ev3_connection, ev3_motor, ev3_sensor, ev3_sound, 0]
                elif hub_type == "Robot Inventor":
                    robot_inventor_connection = connect_to_robot_inventor(hub_address)
                    retry_count = 0
                    while robot_inventor_connection is None:
                        robot_inventor_connection = connect_to_robot_inventor(hub_address)
                        retry_count = retry_count + 1
                        if retry_count > 3:
                            logging.warning("Exceed retry time")
                            break
                    if robot_inventor_connection is not None:
                        connection = ["Robot Inventor", robot_inventor_connection, 0]
                if connection is not None:
                    current_hubs[hub] = connection
                    logging.warning("Connected to: " + hub_type + " at address: " + hub_address)
                else:
                    logging.warning("Failed Connecting to: " + hub_type + " at address: " + hub_address)
                    client.publish("cait/module_states", "Control Exception: " + hub_address + " is not responding", qos=1)
                    connection_success = False
                connecting = False
        if connection_success:
            controlUp = True
    else:
        if controlUp:
            if data.find("pwm") != -1:
                hub_name_begin_idx = data.find("hub") + 4
                hub_name_end_idx = data.find(" pwm", hub_name_begin_idx)
                motor_begin_idx = data.find("pwm") + 4
                motor_end_idx = data.find(" ", motor_begin_idx)
                power_begin_idx = motor_end_idx + 1
                hub_name = data[hub_name_begin_idx:hub_name_end_idx]
                motor = data[motor_begin_idx:motor_end_idx]
                power = int(data[power_begin_idx:])
                setPower(hub_name, motor, power)
            elif data.find("power_group") != -1:
                operation_list = data[data.find("power_group") + 12:]
                setPower_group(operation_list)
            elif data.find("move") != -1:
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
                duration = float(data[duration_begin_idx:])
                move(hub_name, motor, speed, duration)
            elif data.find("motor_group") != -1:
                operation_list = data[data.find("motor_group") + 12:]
                move_group(operation_list)
            elif data.find("rotate") != -1:
                hub_name_begin_idx = data.find("hub") + 4
                hub_name_end_idx = data.find(" rotate", hub_name_begin_idx)
                motor_begin_idx = data.find("rotate") + 7
                motor_end_idx = data.find(" ", motor_begin_idx)
                angle_begin_idx = motor_end_idx + 1
                hub_name = data[hub_name_begin_idx:hub_name_end_idx]
                motor = data[motor_begin_idx:motor_end_idx]
                degree = int(data[angle_begin_idx:])
                setDegree(hub_name, motor, degree)
            elif data.find("position") != -1:
                hub_name_begin_idx = data.find("hub") + 4
                hub_name_end_idx = data.find(" position", hub_name_begin_idx)
                motor_begin_idx = data.find("position") + 9
                motor_end_idx = data.find(" ", motor_begin_idx)
                angle_begin_idx = motor_end_idx + 1
                hub_name = data[hub_name_begin_idx:hub_name_end_idx]
                motor = data[motor_begin_idx:motor_end_idx]
                position = int(data[angle_begin_idx:])
                setPosition(hub_name, motor, position)
            elif data.find("connectedHubs") != -1:
                hub_addresses = ast.literal_eval(data[data.find(",")+1:])
                connected_hubs = {}
                for hub in list(current_hubs.keys()):
                    if hub in hub_addresses:
                        connected_hubs[hub] = current_hubs[hub]
                    else:
                        current_hubs[hub][-1] = current_hubs[hub][-1] + 1
                        if current_hubs[hub][-1] < 30:
                            connected_hubs[hub] = current_hubs[hub]
                            connected_hubs[hub][-1] = 0
                current_hubs = connected_hubs

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


def is_robot_inventor_port_error(byte_msg, port_name):
    msg = byte_msg.decode("utf-8") 
    logging.warning("Return Msg: " + msg)
    logging.warning(byte_msg)
    if msg.find("port." + port_name) != -1 and msg.find("AttributeError") != -1 and msg.find("NoneType") != -1:
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


def setDegree(hub_name, motor_name, position):
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
            if is_robot_inventor_port_error(rec, motor):
                client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                return
        except:
            logging.warning("Time out occured, Hub disconnected")
            client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
            del current_hubs[hub_name]
            return
        time.sleep(1)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating")

def setPower(hub_name, motor_name, power):
    global current_hubs
    hub = current_hubs[hub_name]
    hub_type = hub[0]
    motor = translate_motor_name(hub, motor_name)
    if motor is not None:
        logging.info("Moving motor: " + motor_name)
        if hub_type == "EV3":
            try:
                this_motor = hub[2].Motor(motor)
                this_motor.on(power)
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected or motor port not working", qos=1)
                del current_hubs[hub_name]
                return
        elif hub_type == "Robot Inventor":
            if power == 0:
                msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.brake()\x0D'
            else:
                msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(power).encode('utf-8') + b', 100)\x0D'
            try:
                hub[1].send(msg_individual)
                rec = hub[1].recv(102400)
                if is_robot_inventor_port_error(rec, motor):
                    client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                    return
            except:
                logging.warning("Time out occured, Hub disconnected")
                client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
                del current_hubs[hub_name]
                return
        time.sleep(0.01)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("PWM set done")

def setPosition(hub_name, motor_name, position):
    global current_hubs
    logging.info("Setting motor position now")
    hub = current_hubs[hub_name]
    hub_type = hub[0]
    motor = translate_motor_name(hub, motor_name)
    if hub_type == "EV3":
        try:
            this_motor = hub[2].Motor(motor)
            this_motor.on_to_position(100, position)
        except:
            logging.warning("Time out occured, Hub disconnected")
            client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected motor port not working", qos=1)
            del current_hubs[hub_name]
            return
    elif hub_type == "Robot Inventor":
        msg_0 = b'motor = hub.port.' + motor.encode('utf-8') + b'.motor\x0D'
        msg_1 = b'abs_pos = motor.get()[2]\x0D'
        msg_2 = b'if abs_pos > 180: abs_pos = abs_pos - 360\x0D\x0D'
        msg_3 = b'motor.preset(abs_pos)\x0D'
        msg_4 = b'motor.run_to_position(' + str(position).encode('utf-8') + b', 100)\x0D'
        try:
            hub[1].send(msg_0)
            time.sleep(0.003)
            hub[1].send(msg_1)
            time.sleep(0.003)
            hub[1].send(msg_2)
            time.sleep(0.003)
            hub[1].send(msg_3)
            time.sleep(0.003)
            hub[1].send(msg_4)
            time.sleep(0.003)
            rec = hub[1].recv(102400)
            logging.warning(rec)
            if is_robot_inventor_port_error(rec, motor):
                client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                return
        except:
            logging.warning("Time out occured, Hub disconnected")
            client_control.publish("cait/module_states", "Control Exception: " + hub_name + " Disconnected", qos=1)
            del current_hubs[hub_name]
            return
        time.sleep(1)
    client_control.publish("cait/module_states", "Control Done", qos=1)
    logging.info("Done rotating")

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
                if is_robot_inventor_port_error(rec, motor):
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
                if is_robot_inventor_port_error(rec, motor):
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
    largest_angle = 0
    all_motor_moved = True
    for operation in operation_list:
        hub = current_hubs[operation['hub_name']]
        hub_name_list.append(operation['hub_name'])
        hub_type = hub[0]
        hub_list.append(hub)
        motor = translate_motor_name(hub, operation['motor_name'])
        if 'speed' in operation:
            motor_list.append(motor)
            speed = int(operation['speed'])
            duration = float(operation['duration'])
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
                    if is_robot_inventor_port_error(rec, motor):
                        client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                        break
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                    del current_hubs[operation['hub_name']]
                    del hub_name_list[-1]
                    del hub_list[-1]
                    del motor_list[-1]
                    all_motor_moved = False
                    break
        elif 'angle' in operation:
            motor_list.append(motor)
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
                    del hub_name_list[-1]
                    del hub_list[-1]
                    del motor_list[-1]
                    all_motor_moved = False
                    break
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
                    if is_robot_inventor_port_error(rec, motor):
                        client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                        break
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                    del current_hubs[operation['hub_name']]
                    del hub_name_list[-1]
                    del hub_list[-1]
                    del motor_list[-1]
                    all_motor_moved = False
                    break
        elif 'power' in operation:
            power = int(operation['power'])
            if hub_type == "EV3":
                try:
                    this_motor = hub[2].Motor(motor)
                    this_motor.on(power, block=False)
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected motor port not working", qos=1)
                    del current_hubs[operation['hub_name']]
                    all_motor_moved = False
                    break
            elif hub_type == "Robot Inventor":
                if power == 0:
                    msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.brake()\x0D'
                else:
                    msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(power).encode('utf-8') + b', 100)\x0D'
                try:
                    hub[1].send(msg_individual)
                    rec = hub[1].recv(102400)
                    logging.warning(rec)
                    if is_robot_inventor_port_error(rec, motor):
                        client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                        break
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                    del current_hubs[operation['hub_name']]
                    all_motor_moved = False
                    break
        elif 'position' in operation:
            position = int(operation['position'])
            if abs(position) > largest_angle:
                    largest_angle = abs(position)
            if hub_type == "EV3":
                try:
                    this_motor = hub[2].Motor(motor)
                    this_motor.on_to_position(100, position)
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected motor port not working", qos=1)
                    del current_hubs[operation['hub_name']]
                    all_motor_moved = False
                    break
            elif hub_type == "Robot Inventor":
                msg_0 = b'motor = hub.port.' + motor.encode('utf-8') + b'.motor\x0D'
                msg_1 = b'abs_pos = motor.get()[2]\x0D'
                msg_2 = b'if abs_pos > 180: abs_pos = abs_pos - 360\x0D\x0D'
                msg_3 = b'motor.preset(abs_pos)\x0D'
                msg_4 = b'motor.run_to_position(' + str(position).encode('utf-8') + b', 100)\x0D'
                try:
                    hub[1].send(msg_0)
                    time.sleep(0.003)
                    hub[1].send(msg_1)
                    time.sleep(0.003)
                    hub[1].send(msg_2)
                    time.sleep(0.003)
                    hub[1].send(msg_3)
                    time.sleep(0.003)
                    hub[1].send(msg_4)
                    time.sleep(0.003)
                    rec = hub[1].recv(102400)
                    logging.warning(rec)
                    if is_robot_inventor_port_error(rec, motor):
                        client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
                        break
                except:
                    logging.warning("Time out occured, Hub disconnected")
                    client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
                    del current_hubs[operation['hub_name']]
                    all_motor_moved = False
                    break
    if largest_angle > 800:
        if largest_duration < 2:
            largest_duration = 2
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
                        if is_robot_inventor_port_error(rec, motor_list[i]):
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
                if is_robot_inventor_port_error(rec, motor_list[m]):
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

# def setPower_group(operation_list):
#     global current_hubs
#     operation_list = json.loads(operation_list)['operation_list']
#     hub_name_list = []
#     hub_list = []
#     motor_list = []
#     all_motor_moved = True
#     for operation in operation_list:
#         hub = current_hubs[operation['hub_name']]
#         hub_name_list.append(operation['hub_name'])
#         hub_type = hub[0]
#         hub_list.append(hub)
#         motor = translate_motor_name(hub, operation['motor_name'])
#         motor_list.append(motor)
#         power = int(operation['power'])
#         if hub_type == "EV3":
#             try:
#                 this_motor = hub[2].Motor(motor)
#                 this_motor.on(power, block=False)
#             except:
#                 logging.warning("Time out occured, Hub disconnected")
#                 client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected motor port not working", qos=1)
#                 del current_hubs[operation['hub_name']]
#                 all_motor_moved = False
#                 break
#         elif hub_type == "Robot Inventor":
#             if power == 0:
#                 msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.brake()\x0D'
#             else:
#                 msg_individual = b'hub.port.' + motor.encode('utf-8') + b'.motor.run_at_speed(' + str(power).encode('utf-8') + b', 100)\x0D'
#             try:
#                 hub[1].send(msg_individual)
#                 rec = hub[1].recv(102400)
#                 logging.warning(rec)
#                 if is_robot_inventor_port_error(rec, motor):
#                     client_control.publish("cait/module_states", "Control Exception: port " + motor + " can not be controlled, please check your setup", qos=1)
#                     break
#             except:
#                 logging.warning("Time out occured, Hub disconnected")
#                 client_control.publish("cait/module_states", "Control Exception: " + operation['hub_name'] + " Disconnected", qos=1)
#                 del current_hubs[operation['hub_name']]
#                 all_motor_moved = False
#                 break
#     time.sleep(0.03)
#     if all_motor_moved:
#         client_control.publish("cait/module_states", "Control Done", qos=1)
#         logging.info("Done setPower group")