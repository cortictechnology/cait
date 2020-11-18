from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet, UserUtteranceReverted

import paho.mqtt.client as mqtt
import logging
from time import sleep

def connectMQTT(client):
    try:
        client.connect("127.0.0.1",1883,60000)
        logging.warning("Connected to broker")
        return 0
    except:
        logging.warning("Broker not up yet, retrying...")
        return -1

client = mqtt.Client()
ret = connectMQTT(client)
while ret != 0:
    sleep(1)
    ret = connectMQTT(client)

class ActionAddUserName(Action):
    def name(self) -> Text:
        return "action_add_user_name"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message['entities']
        getName = "noget"
        name = "Friend"
        if entities != []:
            for entity in entities:
                if entity.get('entity') == 'PERSON':
                    name = entity.get('value')
                    getName = "get"
        return [SlotSet('name_input', getName), SlotSet("PERSON", name)]

class ActionExtractUseroName(Action):
    def name(self) -> Text:
        return "action_extract_user_name"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        text = tracker.latest_message['text']
        name = ''
        name_key_phrases = ["I am ", "name is ", "Call me "]
        for phrase in name_key_phrases:
            if phrase in text:
                index = text.find(phrase) + len(phrase)
                name = text[index:]
        if name != '':
            return [SlotSet('name_input', 'get'), SlotSet("PERSON", name)]
        else:
            return []

class ActionStartDemo(Action):
    def name(self) -> Text:
        return "action_start_demo"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        client.publish("cait/demoState", "Start", qos=1)
        dispatcher.utter_message("Start Demo Now")
        
        return[]

class ActionStopDemo(Action):
    def name(self) -> Text:
        return "action_stop_demo"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        client.publish("cait/demoState", "Stop Demo", qos=1)
        dispatcher.utter_message("Stopping demo now")
        
        return[]

class ActionNextDemoState(Action):
    def name(self) -> Text:
        return "action_next_demo_state"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        client.publish("cait/demoState", "Next State", qos=1)
        dispatcher.utter_message("Change to next demo state")
        return[UserUtteranceReverted()]

class ActionNextDemo(Action):
    def name(self) -> Text:
        return "action_next_demo"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        client.publish("cait/demoState", "Next Demo", qos=1)
        dispatcher.utter_message("Change to next demo")
        return[UserUtteranceReverted()]

class ActionRepeatDemo(Action):
    def name(self) -> Text:
        return "action_repeat_demo"

    def run(self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        client.publish("cait/demoState", "Repeat Demo", qos=1)
        dispatcher.utter_message("Repeat the current demo")
        return[UserUtteranceReverted()]
