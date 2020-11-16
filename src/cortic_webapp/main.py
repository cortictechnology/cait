""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from flask import Flask
from flask import render_template, request, redirect, g, session, jsonify, Response
from flask_httpauth import HTTPBasicAuth
from flask_cors import CORS
from urllib.parse import urlparse
from PIL import Image, ImageTk
from io import BytesIO
import time
import base64
import nbformat as nbf
import logging
import errno
import json
import subprocess
import os
import socket
import fcntl
import struct
import crypt
import threading
import sys
import pyaudio
import wave
from wifi import Cell
from shutil import copyfile

logging.getLogger().setLevel(logging.INFO)

auth = HTTPBasicAuth()

application = Flask(__name__)
CORS(application)

new_hostname = ""

connecting_to_wifi = False

def is_internet_connected(host="8.8.8.8", port=53, timeout=3):
  """
  Host: 8.8.8.8 (google-public-dns-a.google.com)
  OpenPort: 53/tcp
  Service: domain (DNS/TCP)
  """
  try:
    socket.setdefaulttimeout(timeout)
    socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
    return True
  except socket.error as ex:
    print(ex)
    return False

def import_cait_modules():
    global essentials
    from cait import essentials

import_thread = threading.Thread(target=import_cait_modules, daemon=True)
import_thread.start()

def get_ip(ifname):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    return socket.inet_ntoa(fcntl.ioctl(
        s.fileno(),
        0x8915,  # SIOCGIFADDR
        struct.pack('256s', bytes(ifname[:15], 'utf-8'))
    )[20:24])

@auth.verify_password
def verify_password(username, password):
    #logging.info("Username: " + username)
    if username == "":
        return False
    g.username = username
    return True

@application.route('/setup')
def setup():
    if not os.path.exists("/usr/share/done_setup"):
        if not is_internet_connected():
            return render_template('setup.html')
        else:
            return redirect('/set_device_info')
    else:
        return render_template('setup.html')

@application.route('/prev_setup')
def prev_setup():
    return render_template('setup.html')


@application.route('/wifi')
def wifi():
    if is_internet_connected():
        return redirect('/set_device_info')
    return render_template('wifi.html')

@application.route('/prev_wifi')
def prev_wifi():
    return render_template('wifi.html')

@application.route('/getwifi', methods=['POST'])
def getwifi():
    global connecting_to_wifi
    wifilist = []
    if not connecting_to_wifi:
        cells = list(Cell.all('wlan0'))
        for cell in cells:
            if cell.ssid != "":
                wifilist.append(cell.ssid)
    return jsonify(wifilist)

@application.route('/connectwifi', methods=['POST'])
def connectwifi():
    global connecting_to_wifi
    ssid = request.form.get('ssid')
    password = request.form.get('password')
    network_str = '\nnetwork={\n        ssid=\"' + ssid + '\"\n        psk=\"' + password + '\"\n}\n'
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", 'w') as f:
        f.write('ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev\nupdate_config=1\ncountry=CA')
        f.write(network_str)
    os.system("sudo wpa_cli -i wlan0 reconfigure")
    init_time = time.time()
    connecting_to_wifi = True
    while not is_internet_connected():
        time.sleep(1)
        logging.info("Connecting to wifi..no internet yet...")
        if time.time() - init_time >= 50:
            success = False
            break
    if is_internet_connected():
        logging.info("Wifi connected.Internet connected.")
        success = True
        
    connecting_to_wifi = False
    result = {"result" : success}
    return jsonify(result)

@application.route('/set_device_info')
def set_device_info():
    return render_template('set_device_info.html')

@application.route('/customdev', methods=['POST'])
def customdev():
    global new_hostname
    device_name = request.form.get('device_name')
    new_hostname = device_name
    username = request.form.get('username')
    password = request.form.get('user_password')
    subprocess.run(['sudo', '/usr/sbin/change_hostname.sh', device_name])
    res = os.system("sudo useradd -m " + username)
    if res != 0:
        result = {"result" : res}
        return jsonify(result)
    out = os.system("echo " + "\"" + password + "\n" +  password + "\" | sudo passwd " + username)
    g_out = os.system("sudo usermod -a -G cait " + username)
    os.system("sudo touch /usr/share/done_device_info")
    result = {"result" : out}
    return jsonify(result)

@application.route('/testhardware')
def testhardware():
    return render_template("testhardware.html")

@application.route('/getvideodev', methods=['POST'])
def getvideodev():
    devices = essentials.get_video_devices()
    video_devices = []
    for vid_dev in devices:
        dev = {"index": vid_dev["index"], "device": vid_dev["device"]}
        video_devices.append(dev)
    return jsonify(video_devices)

@application.route('/getaudiodev', methods=['POST'])
def getaudiodev():
    devices = essentials.get_audio_devices()
    audio_devices = []
    for aud_dev in devices:
        dev = {"index": aud_dev["index"], "device": aud_dev["device"], "type": aud_dev["type"]}
        audio_devices.append(dev)
    return jsonify(audio_devices)

@application.route('/testcam', methods=['POST'])
def testcam():
    cam_index = request.form.get('index')
    result = essentials.test_camera(cam_index)
    return jsonify(result)

@application.route('/testspeaker', methods=['POST'])
def testspeaker():
    out = os.system("sudo -u pi aplay /opt/cortic_modules/voice_module/siri.wav")

    result = {"result": out}        
    return jsonify(result)

@application.route('/testmicrophone', methods=['POST'])
def testmicrophone():
    index = request.form.get('index')
    BLOCKS_PER_SECOND = 50
    sample_format = pyaudio.paInt16  # 16 bits per sample
    channels = 1
    fs = 16000  
    seconds = 5
    filename = "output.wav"

    p = pyaudio.PyAudio()  # Create an interface to PortAudio

    print('Recording')
    block_size = int(fs / float(BLOCKS_PER_SECOND))
    chunk = int(fs / float(BLOCKS_PER_SECOND))
    stream = p.open(format=sample_format,
                    channels=channels,
                    rate=fs,
                    frames_per_buffer=chunk,
                    input=True)

    frames = []  # Initialize array to store frames

    # Store data in chunks for 3 seconds
    for i in range(0, int(fs / chunk * seconds)):
        data = stream.read(chunk)
        frames.append(data)

    # Stop and close the stream 
    stream.stop_stream()
    stream.close()
    # Terminate the PortAudio interface
    p.terminate()

    print('Finished recording')

    # Save the recorded data as a WAV file
    wf = wave.open(filename, 'wb')
    wf.setnchannels(channels)
    wf.setsampwidth(p.get_sample_size(sample_format))
    wf.setframerate(fs)
    wf.writeframes(b''.join(frames))
    wf.close()

    os.system("sudo -u pi aplay " + filename)

    out = os.system("rm " + filename)

    result = {"result": out}        
    return jsonify(result)

@application.route('/thirdsignin')
def thirdsignin():
    return render_template('third_signin.html')

@application.route('/upload_account',  methods=['POST'])
def upload_account():
    account_credentials = request.form.get('account_credentials')
    account_credentials = json.loads(account_credentials)
    with open('/opt/accounts', 'w') as f:
        f.write('["google_cloud", "account.json"]')
    with open('/opt/cortic_modules/voice_module/account.json', 'w') as outfile:
        json.dump(account_credentials, outfile)
    result = {"result": True}        
    return jsonify(result)

@application.route('/newname', methods=['POST'])
def newname():
    global new_hostname
    result = {"hostname": new_hostname}    
    return jsonify(result)

@application.route('/congrats')
def congrats():
    return render_template("congrats.html")

@application.route('/finish', methods=['POST'])
def finish():
    global new_hostname
    os.system('sudo sed -i \'s/ssid=[^"]*/ssid=' + new_hostname + '/g\' /etc/hostapd/hostapd.conf')
    os.system('sudo sed -i \'s/ignore_broadcast_ssid=[^"]*/ignore_broadcast_ssid==' + new_hostname + '/g\' /etc/hostapd/hostapd.conf')
    os.system("sudo touch /usr/share/done_setup")
    result = {"done": True}   
    return jsonify(result)

@application.route('/reboot', methods=['POST'])
def reboot():
    os.system("sudo reboot")

@application.route('/')
@application.route('/index')
def index():
    if not os.path.exists("/usr/share/done_setup"):
        return redirect('/setup')
    return render_template('index.html')

@application.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@application.route("/login", methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    p = subprocess.Popen(['sudo', '/opt/chkpass.sh', username], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out,err = p.communicate(str.encode(password))
    result = {"result": out, "error": err}        
    return jsonify(result)

@application.route("/signup", methods=['POST'])
def signup():
    print("IN singup")
    username = request.form.get('username')
    password = request.form.get('password')
    res = os.system("sudo useradd -m " + username)
    if res != 0:
        result = {"result" : res}
        return jsonify(result)
    out = os.system("echo " + "\"" + password + "\n" +  password + "\" | sudo passwd " + username)
    g_out = os.system("sudo usermod -a -G cait " + username)
    result = {"result" : out}
    return jsonify(result)

@application.route('/programming')
@auth.login_required
def programming():
    if not g.username or g.username == "logout":
        o = urlparse(request.base_url)
        return redirect("http://" + o.hostname, code=302)
    return render_template('programming.html')

@application.route("/get_cloud_accounts", methods=['POST'])
@auth.login_required
def get_cloud_accounts():
    account_list = essentials.get_cloud_accounts()
    return jsonify(account_list)


@application.route("/get_nlp_models", methods=['POST'])
@auth.login_required
def get_nlp_models():
    model_list = essentials.get_nlp_models()
    return jsonify(model_list)


@application.route("/initialize_component", methods=['POST'])
@auth.login_required
def initialize_component():
    component_name = request.form.get('component_name')
    mode = request.form.get('mode')
    account = request.form.get('account')
    processor = request.form.get('processor')
    language = request.form.get('language')
    success, msg = essentials.initialize_component(component_name, mode, account, processor, language)
    if success == False:
        result = {"success": success, "error": msg}
    else:
        result = {"success": success}
    return jsonify(result)


@application.route("/change_module_parameters", methods=['POST'])
@auth.login_required
def change_module_parameters():
    parameter_name = request.form.get('parameter_name')
    value = float(request.form.get('value'))
    essentials.change_module_parameters(parameter_name, value)
    result = {"success": True}
    return jsonify(result)

@application.route("/camerafeed", methods=['POST'])
@auth.login_required
def camerafeed():
    img = essentials.get_camera_image()
    if img is not None:
        encodedImage = BytesIO()
        img.save(encodedImage, "JPEG")
        contents = base64.b64encode(encodedImage.getvalue()).decode()
        encodedImage.close()
        contents = contents.split('\n')[0]
        return contents

@application.route("/recognizeface", methods=['POST'])
@auth.login_required
def recognizeface():
    person = essentials.recognize_face()
    return jsonify(person)

@application.route("/addperson", methods=['POST'])
@auth.login_required
def addperson():
    person_name = request.form.get('name')
    success = essentials.add_person(person_name)
    result = {"success": success}
    return jsonify(result)

@application.route("/removeperson", methods=['POST'])
@auth.login_required
def removeperson():
    person_name = request.form.get('name')
    logging.info("Remove: " + person_name)
    success = essentials.remove_person(person_name)
    result = {"success": success}
    return jsonify(result)

@application.route("/detectobject", methods=['POST'])
@auth.login_required
def detectobject():
    objects = essentials.detect_objects()
    return jsonify(objects)

@application.route("/listen", methods=['POST'])
@auth.login_required
def listen():
    text = essentials.listen()
    result = {"text" : text}
    return jsonify(result)

@application.route("/say", methods=['POST'])
@auth.login_required
def say():
    text = request.form.get('text')
    success = essentials.say(text)
    result = {"success": success}
    return jsonify(result)

@application.route("/analyze", methods=['POST'])
@auth.login_required
def analyze():
    text = request.form.get('text')
    result = essentials.analyse_text(text)
    return jsonify(result)

@application.route("/saveworkspace", methods=['POST'])
@auth.login_required
def saveworkspace():
    xml_text = request.form.get('xml_text')
    filename = request.form.get('filename')
    if filename != "":
        save_type = request.form.get('save_type')
        if save_type == "autosave":
            location = "/home/" + g.username + "/tmp/"
        else:
            location = "/home/" + g.username + "/cait_workspace/"
        savename = location+filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                #os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + g.username + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        f = open(savename, 'w')
        f.write(xml_text)
        f.close()
        result = {"success": 1}
    else:
        result = {"success": -1}
    return jsonify(result)

@application.route("/savepythoncode", methods=['POST'])
@auth.login_required
def savepythoncode():
    code = request.form.get('code')
    filename = request.form.get('filename')
    if filename != "":
        location = "/home/" + g.username + "/cait_workspace/python_code/"
        savename = location+filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                #os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + g.username + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        f = open(savename, 'w')
        f.write(code)
        f.close()
        result = {"success": True}
    else:
        result = {"success": -1}
    return jsonify(result)

@application.route("/savenotebook", methods=['POST'])
@auth.login_required
def savenotebook():
    nb = nbf.v4.new_notebook()
    code = request.form.get('code')
    import_code = code[0:code.find("# Initialize and setup different components")]
    import_code = import_code + "from lolviz import *"
    init_code = code[code.find("# Initialize and setup different components"):code.find("# Entry point of program")]
    rest_code = code[code.find("# Entry point of program"):]
    text = "Jupyter notebook generated from blockly Program"
    nb['cells'] = [nbf.v4.new_markdown_cell(text),
               nbf.v4.new_code_cell(import_code),
               nbf.v4.new_code_cell(init_code),
               nbf.v4.new_code_cell(rest_code)]
    filename = request.form.get('filename')
    if filename != "":
        location = "/home/" + g.username + "/cait_workspace/python_notebooks/"
        savename = location+filename
        if not os.path.exists(os.path.dirname(savename)):
            try:
                #os.makedirs(os.path.dirname(savename))
                os.system("sudo mkdir " + location)
                os.system("sudo chown " + g.username + ":cait " + location)
                os.system("sudo chmod -R g+rwx " + location)
            except OSError as exc: # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        with open(savename, 'w') as f:
            nbf.write(nb, f)
        result = {"success": True}
    else:
        result = {"success": -1}
    return jsonify(result)

@application.route("/loadworkspace", methods=['POST'])
@auth.login_required
def loadworkspace():
    filename = request.form.get('filename')
    if filename != "":
        save_type = request.form.get('save_type')
        if save_type == "autosave":
            location = "/home/" + g.username + "/tmp/"
        else:
            location = "/home/" + g.username + "/cait_workspace/"
        savename = location+filename
        if os.path.exists(savename):
            f = open(savename, 'r')
            xml_text = f.read()
            f.close()
            if filename == "workspace_autosave.xml":
                os.remove(savename) 
        else:
            xml_text = ''
        result = {"xml_text": xml_text}
    else:
        result = {"xml_text": ""}
    return jsonify(result)

@application.route("/control_motor", methods=['POST'])
@auth.login_required
def move():
    motor_name = request.form.get('motor_name')
    speed = request.form.get('speed')
    duration = request.form.get('duration')
    success = essentials.control_motor(motor_name, speed, duration)
    result = {"success": success}
    return jsonify(result)

@application.route("/control_motor_speed_group", methods=['POST'])
@auth.login_required
def control_motor_speed_group():
    operation_list = request.form.get('data')
    success = essentials.control_motor_speed_group(operation_list)
    result = {"success": success}
    return jsonify(result)

@application.route("/rotate_motor", methods=['POST'])
@auth.login_required
def rotate_motor():
    motor_name = request.form.get('motor_name')
    angle = request.form.get('angle')
    success = essentials.rotate_motor(motor_name, int(angle))
    result = {"success": success}
    return jsonify(result)

@application.route("/control_motor_degree_group", methods=['POST'])
@auth.login_required
def control_motor_degree_group():
    operation_list = request.form.get('data')
    success = essentials.control_motor_degree_group(operation_list)
    result = {"success": success}
    return jsonify(result)

@application.route("/get_states", methods=['POST'])
@auth.login_required
def get_states():
    device_type = request.form.get('device_type')
    devices = essentials.get_devices(device_type)
    return jsonify(devices)

@application.route("/control_light", methods=['POST'])
@auth.login_required
def control_light():
    device_name = "light." + request.form.get('device_name')
    operation = request.form.get('operation')
    parameter = request.form.get('parameter')
    result = essentials.control_light(device_name, operation, parameter)
    result = {'result': result}
    return jsonify(result)

@application.route("/control_media_player", methods=['POST'])
@auth.login_required
def control_media_player():
    device_name = "media_player." + request.form.get('device_name')
    operation = request.form.get('operation')
    result = essentials.control_media_player(device_name, operation)
    result = {'result': result}
    return jsonify(result)

if __name__ == "__main__":
    application.run()
    #application.run(host="0.0.0.0", port=80, threaded=True)
