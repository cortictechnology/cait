""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from rasa.nlu.model import Metadata, Interpreter
import paho.mqtt.client as mqtt
import json
import time
import logging
import threading

logging.getLogger().setLevel(logging.INFO)

interpreter = None
loading_model = False
heartbeat_thread = None
current_model = ""

def pprint(o):
    print(json.dumps(o, indent=2))

nlpUp = False

#pprint(interpreter.parse(sentence))

def connectMQTT(client):
    try:
        client.connect("127.0.0.1",1883,60)
        logging.info("Connected to broker")
        return 0
    except:
        logging.info("Broker not up yet, retrying...")
        return -1

client_response = mqtt.Client()
ret = connectMQTT(client_response)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_response)
client_response.loop_start()

def on_connect_user_msg(client, userdata, flags, rc):
    print("User message client Connected with result code "+str(rc))
    client.subscribe("cait/userMsg")

def on_message_user_msg(client, userdata, msg):
    global nlpUp
    global interpreter
    global client_response
    global loading_model
    global heartbeat_thread
    global current_model
    
    data = msg.payload.decode()
    logging.info("User Message: " + data)
    if data.find("NLP Up") != -1 and not loading_model:
        model = data[data.find(",")+1:]
        if current_model != model:
            current_model = model
            nlpUp = False
            loading_model = True
            logging.info("Loading " + model + " modle now...")
            interpreter = Interpreter.load('/nlp_module/models/' + model)
            logging.info("Done Loading nlu model!")
            nlpUp = True
            loading_model = False
            if heartbeat_thread is None:
                heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
                heartbeat_thread.start()
    else:
        logging.info("User Message: " + data)
        logging.info("Data: " + data)
        intent = interpreter.parse(data)
        intent_data = {"topic" : intent['intent']['name'], "confidence" : intent['intent']['confidence'], "entities" : intent['entities']}
        intent_data = json.dumps(intent_data)
        logging.info("Intent: " + str(intent_data))
        client_response.publish("cait/nlpResponse", intent_data, qos=0)

client_user_msg = mqtt.Client()
client_user_msg.on_connect = on_connect_user_msg
client_user_msg.on_message = on_message_user_msg
ret = connectMQTT(client_user_msg)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_user_msg)

client_heartbeat = mqtt.Client()
ret = connectMQTT(client_heartbeat)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_heartbeat)
client_heartbeat.loop_start()

def heartbeat_func():
    global nlpUp
    global client_heartbeat
    while True:
        if nlpUp:
            client_heartbeat.publish("cait/module_states", "NLP Up", qos=1)
        else:
            client_heartbeat.publish("cait/module_states", "NLP Down", qos=1)
        time.sleep(1)

def main():
    client_user_msg.loop_forever()

if __name__ == "__main__":
    main()