""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

References: 

https://github.com/mozilla/DeepSpeech-examples/tree/r0.6/mic_vad_streaming
https://github.com/googleapis/python-speech/tree/master/samples/microphone

"""

from __future__ import division

import traceback
import logging
import datetime
import paho.mqtt.client as mqtt
import os
from time                  import time, sleep
import sys
import threading
from six.moves import queue
from google.cloud import speech
import numpy as np
import json
import pygame
import pyaudio
from vad_utils import Audio, VADAudio
import deepspeech

WAKE_WORD_KALDI = ['Kate', 'eight kate', 'a cave', 'it came', 'ec aid', 'kate', 'in case',"cain't", 'it cave', 'eight', 'pete', 'and kate', 'a kate', 'nay tate', 'a paint', 'a cake', 'a tape', 'they take', 'kid', 'hey kid', 'it kid', 'kit', 'a tate']
WAKE_WORD_GOOGLE = ['Kate', 'kate', 'Hecate', '8/8', 'placate', 'cake', 'k', 'bait', 'hey', 'AK', 'KK', 'Escape', 'locate', 'dictate', "I can't", 'okay', 'pick 8', 'Tay k']

language_code = 'en-US'  # a BCP-47 language tag

audio_in_index = -1
mode = "N/A"
online_account = "cortic"
VoiceInit = False
startListen = False
wakeWordMode = False
robotSpeak = False
robotSpeakMsg = ""
playedNotification = False
wasListening = False
doneSpeaking = True

logging.getLogger().setLevel(logging.INFO)

def restart_program():
    python = sys.executable
    logging.info("in restart program")
    os.execl(python, python, *sys.argv)
    logging.info("Done restart program")

def connectMQTT(client):
    try:
        client.connect("127.0.0.1",1883,60)
        logging.info("Connected to broker")
        return 0
    except:
        logging.info("Broker not up yet, retrying...")
        return -1

client_stt_response = mqtt.Client()
ret = connectMQTT(client_stt_response)
while ret != 0:
    sleep(1)
    ret = connectMQTT(client_stt_response)
client_stt_response.loop_start()

def on_connect_stt_mode(client, userdata, flags, rc):
    print("STT mode client Connected with result code "+str(rc))
    client.subscribe("cait/voice_control")

def on_message_stt_mode(client, userdata, msg):
    global audio_in_index
    global mode
    global language_code
    global online_account
    global VoiceInit
    global startListen
    data = msg.payload.decode()
    logging.info("Voice Control: " + data)
    #logging.info("STT Control Init: "+data)
    if data.find("Online") != -1 or data.find("Offline") != -1:
        audio_device = json.loads(data[data.find(" ")+1:])
        audio_in_index = int(audio_device["index"])
    # if data == "Online" or data == "Offline":
        if mode == "N/A":
            logging.info("got init mode")
            if data.find("Offline") != -1:
                mode = "Offline"
            else:
                online_account = audio_device["account"]
                if audio_device["language"] == "french":
                    language_code = "fr-FR"
                mode = "Online"
        else:
            if VoiceInit:
                restart_program()
    elif data.find("VoiceDown") != -1:
        startListen = False

client_stt_mode = mqtt.Client()
client_stt_mode.on_connect = on_connect_stt_mode
client_stt_mode.on_message = on_message_stt_mode
ret = connectMQTT(client_stt_mode)
while ret != 0:
    sleep(1)
    ret = connectMQTT(client_stt_mode)
client_stt_mode.loop_start()

logging.info("Not recieve mode yet")
while mode == "N/A":
    sleep(0.2)

logging.info("Recieved mode, initializing pygame")
pygame.mixer.init()
effect = pygame.mixer.Sound('/voice_module/siri.wav')
logging.info("pygame done init")

client_stt_response.publish("cait/module_states", "STT Init Done", qos=1)
VoiceInit = True
logging.info("Recieved mode, initializing")

def on_connect_stt_control(client, userdata, flags, rc):
    print("STT control client Connected with result code "+str(rc))
    client.subscribe("cait/voice_control")

def on_message_stt_control(client, userdata, msg):
    global startListen
    global wakeWordMode
    global robotSpeak
    global robotSpeakMsg
    global playedNotification
    global wasListening
    data = msg.payload.decode()
    print("STT Control Online mode:",data)
    if data == "Reset":
        startListen = False
        wakeWordMode = False
        robotSpeak = False
        robotSpeakMsg = ""
        playedNotification = False
        wasListening = False
    elif data == "Start Listen":
        client_stt_response.publish("cait/module_states", "Init recording", qos=1)
        print("received Start Listen")
        startListen = True
        wakeWordMode = False
    elif data == "Start Listen Wakeword":
        print("received Start Listen Wakeword")
        client_stt_response.publish("cait/module_states", "Init recording", qos=1)
        startListen = True
        wakeWordMode = True

client_stt_control = mqtt.Client()
client_stt_control.on_connect = on_connect_stt_control
client_stt_control.on_message = on_message_stt_control
ret = connectMQTT(client_stt_control)
while ret != 0:
    sleep(1)
    ret = connectMQTT(client_stt_control)
client_stt_control.loop_start()        

def on_connect_tts(client, userdata, flags, rc):
    print("TTS client Connected with result code "+str(rc))
    client.subscribe("cait/ttsInput")

def on_message_tts(client, userdata, msg):
    global robotSpeak
    global startListen
    global robotSpeakMsg
    global playedNotification
    global wasListening
    global doneSpeaking
    data = msg.payload.decode()
    print("ttsInput:",data)
    if startListen:
        wasListening = True
    startListen = False
    robotSpeak = True
    doneSpeaking = False
    print("Set done speaking to false")
    robotSpeakMsg = data
    playedNotification = False

client_tts = mqtt.Client()
client_tts.on_connect = on_connect_tts
client_tts.on_message = on_message_tts
ret = connectMQTT(client_tts)
while ret != 0:
    sleep(1)
    ret = connectMQTT(client_tts)
client_tts.loop_start()

client_heartbeat = mqtt.Client()
ret = connectMQTT(client_heartbeat)
while ret != 0:
    time.sleep(1)
    ret = connectMQTT(client_heartbeat)
client_heartbeat.loop_start()

class MicrophoneStream(object):
    """Opens a recording stream as a generator yielding the audio chunks."""
    def __init__(self, mic_index, rate, chunk):
        self._rate = rate
        self._chunk = chunk

        # Create a thread-safe buffer of audio data
        self._buff = queue.Queue()
        self.closed = True
        self.mic_index = mic_index

    
    def open_audio_interface(self):
        try:
            self._audio_stream = self._audio_interface.open(
                format=pyaudio.paInt16,
                # The API currently only supports 1-channel (mono) audio
                # https://goo.gl/z757pE
                channels=1, rate=self._rate,
                input=True, frames_per_buffer=self._chunk,
                input_device_index = self.mic_index,
                # Run the audio stream asynchronously to fill the buffer object.
                # This is necessary so that the input device's buffer doesn't
                # overflow while the calling thread makes network requests, etc.
                stream_callback=self._fill_buffer,
            )
            return True
        except:
            return False


    def __enter__(self):
        global mic_index
        self._audio_interface = pyaudio.PyAudio()
        success = self.open_audio_interface()
        retry_counter = 0
        while not success:
            retry_counter += 1
            success = self.open_audio_interface()
            if retry_counter >= 2:
                break
            sleep(0.5)
        self.closed = False

        return self

    def __exit__(self, type, value, traceback):
        self._audio_stream.stop_stream()
        self._audio_stream.close()
        self.closed = True
        # Signal the generator to terminate so that the client's
        # streaming_recognize method will not block the process termination.
        self._buff.put(None)
        self._audio_interface.terminate()

    def _fill_buffer(self, in_data, frame_count, time_info, status_flags):
        """Continuously collect data from the audio stream, into the buffer."""
        self._buff.put(in_data)
        return None, pyaudio.paContinue

    def generator(self):
        global startListen
        global doneSpeaking
        while not self.closed:
            if not startListen or not doneSpeaking:
                break
            # Use a blocking get() to ensure there's at least one chunk of
            # data, and stop iteration if the chunk is None, indicating the
            # end of the audio stream.
            chunk = self._buff.get()
            if chunk is None:
                return
            data = [chunk]

            # Now consume whatever other data's still buffered.
            while True:
                try:
                    chunk = self._buff.get(block=False)
                    if chunk is None:
                        return
                    data.append(chunk)
                except queue.Empty:
                    break

            yield b''.join(data)

def listen_print_loop(responses):
    """Iterates through server responses and prints them.

    The responses passed is a generator that will block until a response
    is provided by the server.

    Each response may contain multiple results, and each result may contain
    multiple alternatives; for details, see https://goo.gl/tjCPAU.  Here we
    print only the transcription for the top alternative of the top result.

    In this case, responses are provided for interim results as well. If the
    response is an interim one, print a line feed at the end of it, to allow
    the next result to overwrite it, until the response is a final one. For the
    final one, print a newline to preserve the finalized transcription.
    """
    num_chars_printed = 0
    global startListen
    global playedNotification
    global wakeWordMode
    global doneSpeaking
    for response in responses:
        if not response.results:
            continue

        # The `results` list is consecutive. For streaming, we only care about
        # the first result being considered, since once it's `is_final`, it
        # moves on to considering the next utterance.
        result = response.results[0]
        if not result.alternatives:
            continue

        # Display the transcription of the top alternative.
        transcript = result.alternatives[0].transcript

        # Display interim results, but with a carriage return at the end of the
        # line, so subsequent lines will overwrite them.
        #
        # If the previous result was longer than this one, we need to print
        # some extra spaces to overwrite the previous result
        overwrite_chars = ' ' * (num_chars_printed - len(transcript))

        if not startListen or not doneSpeaking:
            break
        if not result.is_final:
            logging.info("In print loop for not final")
            sys.stdout.write(transcript + overwrite_chars + '\r')
            sys.stdout.flush()
            logging.info("In print loop for not final, flushed")
            num_chars_printed = len(transcript)

        else:
            sentence = transcript + overwrite_chars
            logging.info("******************** "+sentence)
            logging.info("In print loop for final")
            if not wakeWordMode:
                client_stt_response.publish("cait/sttData", sentence, qos=0)
                logging.info("Publish stt data")
                startListen = False
                playedNotification = False
                logging.info("Breaking")
                break
            else:
                sentence_list = sentence.split()
                if ' '.join(sentence_list[-2:]) in WAKE_WORD_GOOGLE or sentence_list[-1] in WAKE_WORD_GOOGLE:
                    client_stt_response.publish("cait/module_states", "WAKEWORD", qos=0)
                    #print("Published:", sentence)
                    startListen = False
                    break

def heartbeat_func():
    global client_heartbeat
    while True:
        client_heartbeat.publish("cait/module_states", "Voice Up", qos=1)
        sleep(1)

def main():
    global audio_in_index
    global robotSpeak
    global startListen
    global robotSpeakMsg
    global playedNotification
    global wasListening
    global doneSpeaking
    global online_account
    global mode
    global language_code

    DEFAULT_SAMPLE_RATE = 16000
    MODEL_FILE = "/opt/deepspeech-models/deepspeech-0.9.1-models.tflite"
    SCORE_FILE = "/opt/deepspeech-models/deepspeech-0.9.1-models.scorer"
    MODEL_FILE_CN = "/opt/deepspeech-models/deepspeech-0.9.1-models-zh-CN.tflite"
    SCORE_FILE_CN = "/opt/deepspeech-models/deepspeech-0.9.1-models-zh-CN.scorerr"

    json_file = "/voice_module/" + online_account
    # Audio recording parameters
    RATE = 16000
    CHUNK = int(RATE / 10)  # 100ms

    if mode == "Online":
        logging.warning("Using cloud account: " + json_file)
        client = speech.SpeechClient.from_service_account_json(json_file)
        config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=RATE,
            language_code=language_code)
        streaming_config = speech.StreamingRecognitionConfig(
            config=config,
            interim_results=True)
    else:
        client = deepspeech.Model(MODEL_FILE)
        client.enableExternalScorer(SCORE_FILE)

    heartbeat_thread = threading.Thread(target=heartbeat_func, daemon=True)
    heartbeat_thread.start()
    while True:
        if startListen and doneSpeaking:
            print("Start listening")
            if mode == "Online":
                with MicrophoneStream(audio_in_index, RATE, CHUNK) as stream:
                    if not playedNotification and not wakeWordMode:
                        try:
                            effect.play()
                        except:
                            effect.play()
                        playedNotification = True
                    client_stt_response.publish("cait/module_states", "Init recording done", qos=1)
                    audio_generator = stream.generator()
                    requests = (speech.StreamingRecognizeRequest(audio_content=content)
                                for content in audio_generator)
                    responses = client.streaming_recognize(streaming_config, requests)
                    # Now, put the transcription responses to use.
                    try:
                        listen_print_loop(responses)
                    except Exception as e:
                        print("Excption handle : Exceeded maximum allowed stream duration, re-listening")
            else:
                if not playedNotification and not wakeWordMode:
                    try:
                        effect.play()
                    except:
                        effect.play()
                    playedNotification = True
                #sleep(1)
                while pygame.mixer.get_busy() == True:
                    #logging.info("Playing du du")
                    continue
                vad_audio = VADAudio(audio_in_index, aggressiveness=2,
                            input_rate=DEFAULT_SAMPLE_RATE)
                logging.info("Created VAD")
                client_stt_response.publish("cait/module_states", "Init recording done", qos=1)
                frames = vad_audio.vad_collector()
                stream_context = client.createStream()
                wav_data = bytearray()
                for frame in frames:
                    if frame is not None:
                        logging.info("Streaming frame")
                        stream_context.feedAudioContent(np.frombuffer(frame, np.int16))
                    else:
                        logging.info("end utterence")
                        sentence = stream_context.finishStream()
                        logging.info("User said: " + sentence)
                        if sentence == "":
                            stream_context = client.createStream()
                            continue
                        if not wakeWordMode:
                            client_stt_response.publish("cait/sttData", sentence, qos=2)
                            startListen = False
                            playedNotification = False
                            break
                        else:
                            sentence_list = sentence.split()
                            if ' '.join(sentence_list[-2:]) in WAKE_WORD_GOOGLE or sentence_list[-1] in WAKE_WORD_GOOGLE:
                                client_stt_response.publish("cait/module_states", "WAKEWORD", qos=2)
                                #print("Published:", sentence)
                                startListen = False
                                break
                if not startListen:
                    logging.info("stop listen")
                    vad_audio.destroy()
                    logging.info("Destroyed VAD")
        else:
            if robotSpeak:
                client_stt_control.publish("cait/module_states", "Start Speaking", qos=1)
                if mode == "Online":
                    if language_code == "fr-FR":
                        os.system('/voice_module/speech_fr.sh "' + robotSpeakMsg + '"')
                    else:
                        os.system('/voice_module/speech_en.sh "' + robotSpeakMsg + '"')
                else:
                    os.system('mimic -t "' + robotSpeakMsg + '" -voice slt')
                robotSpeak = False
                if wasListening:
                    startListen = True
                    wasListening = False
                doneSpeaking = True
                print("Set done speaking to true")
                client_stt_control.publish("cait/module_states", "Done Speaking", qos=1)
            sleep(0.03)

if __name__ == '__main__':
    main()