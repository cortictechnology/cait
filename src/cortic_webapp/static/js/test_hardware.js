/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

var stopStreaming = true;
var hostname = window.location.hostname
var clientID = "cait_" + parseInt(Math.random() * 100);
var client = new Paho.Client(hostname, 8083, clientID);

client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;
var cait_system_up = false

function MQTTconnect() {
  client.connect({
      onSuccess:onConnect,
      onFailure:onFailure,
      reconnect : true});
}

MQTTconnect();

function onFailure(message) {
  console.log("Failed Connecting, Retrying...");
  setTimeout(MQTTconnect, 500);
}

function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("Connected to cait");
  client.subscribe("cait/displayFrame");
  client.subscribe("cait/system_status");
  stopVideoFeed();
  emptyVisionMode();
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
    cait_system_up = false;
    loader.style.display = "flex";
    loader.style.zIndex = 1;
    setTimeout(MQTTconnect, 500);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  //console.log("onMessageArrived:");
  if (message.payloadString == "CAIT UP") {
    if(!cait_system_up){
        cait_system_up = true;
        loader.style.display = "none";
    }
  }
  else {
    if (stopStreaming) {
      document.getElementById("cameraImage").setAttribute("src", '/static/img/video_placeholder.png');
    }
    else {
      //console.log(message.payloadString)
      document.getElementById("cameraImage").setAttribute(
        'src', "data:image/png;base64," + message.payloadString
        );
    } 
  }
}

function stopVideoFeed() {
  topicMessage = new Paho.Message("VisionDown");
  topicMessage.topic = "cait/vision_control";
  client.publish(topicMessage)
}

function emptyVisionMode() {
  topicMessage = new Paho.Message("ResetMode");
  topicMessage.topic = "cait/vision_control";
  client.publish(topicMessage)
}

async function ajax_post(url, data) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: data
    });
}

async function test_camera(){
  var e = document.getElementById("cameras");
  var camera = e.options[e.selectedIndex].value;
  var index = camera[0];
  console.log("Camera Index: " + String(index));
  try {
    const result = await ajax_post("/testcam", {'index': index});
    stopStreaming = false;
    console.log(result);
  } catch(err) {
      console.log(err);
      return err;
  }
}

var current_video_devices = [];
var current_audio_devices = [];

async function get_video_devices(){
      try {
        const result = await ajax_post("/getvideodev", {});
        var device_list = document.getElementById("cameras");
        device_list.innerHTML = "";
        var new_device = [];
        for (var i = 0; i < result.length; i++) {
            device = result[i];
            device_name = device["index"] + ": " + device["device"];
            new_device.push(device_name);
            if (current_video_devices.includes(device_name) == false){
              current_video_devices.push(device_name);
            }
        }
        for (var j = 0; j < result.length; j++) {
            exist_device = current_video_devices[j];
            if (new_device.includes(exist_device) == false){
              current_video_devices.splice(j, 1);
            } 
        }
        for (var k = 0; k < result.length; k++) {
            device = current_video_devices[k];
            var option = document.createElement("option");
            option.text = device;
            device_list.add(option);
        }
      } catch(err) {
          console.log(err);
          return err;
      }
}

get_video_devices()
setInterval(get_video_devices, 5000);

async function get_audio_devices(){
    try {
      const result = await ajax_post("/getaudiodev", {});
      var speaker_list = document.getElementById("speakers");
      var speaker_options = [];
      for (var i = 0, n = speaker_list.options.length; i < n; i++) { 
        if (speaker_list.options[i].value) speaker_options.push(speaker_list.options[i].value);
      }
      var microphone_list = document.getElementById("microphones");
      microphone_options = [];
      for (var i = 0, n = microphone_list.options.length; i < n; i++) { 
        if (microphone_list.options[i].value) microphone_options.push(microphone_list.options[i].value);
      }

      // speaker_list.innerHTML = "";
      // microphone_list.innerHTML = "";
        var new_devices = [];
        for (var i = 0; i < result.length; i++) {
            device = result[i];
            device_index = device["index"];
            device_name = device["device"];
            device_type = device["type"];
            this_device = {"name": device_name, "type": device_type, "index": device_index};
            new_devices.push(this_device );
            var new_device = true;
            for (dev in current_audio_devices){
              current_dev = current_audio_devices[dev];
              if (current_dev['name'] == device_name && current_dev['index'] == device_index) {
                new_device = false;
              }
            }
            if (new_device) {
              current_audio_devices.push(this_device);
            }
        }
        for (var j = 0; j < result.length; j++) {
            exist_device = current_audio_devices[j];
            device_gone = true;
            for (dev in new_devices){
              current_dev = new_devices[dev];
              if (current_dev['name'] == exist_device['name'] && current_dev['index'] == exist_device['index']) {
                device_gone  = false;
              }
            }
            if (device_gone){
              current_audio_devices.splice(j, 1);
            }
        }
        for (var k = 0; k < current_audio_devices.length; k++) {
            device = current_audio_devices[k];
            var option = document.createElement("option");
            option.text = device['index'] + ': ' + device['name'];
            if (device['type'] == "Input"){
              if (microphone_options.includes(option.text) == false){
                microphone_list.add(option);
                microphone_options.push(option.text);
              } 
            }
            else{

              if (speaker_options.includes(option.text) == false) {
                speaker_list.add(option);
                speaker_options.push(option.text);
              }
            }
        }
        
        for (opt in microphone_options) {
          option_gone = true;
          this_option = microphone_options[opt];
          for (dev in current_audio_devices) {
            if (this_option == current_audio_devices[dev]['index'] + ': ' + current_audio_devices[dev]['name']) {
              option_gone = false;
            }
          }
          if (option_gone) {
            microphone_list.remove(opt);
          }
        }
        for (opt in speaker_options) {
          option_gone = true;
          this_option = speaker_options[opt];
          for (dev in current_audio_devices) {
            if (this_option == current_audio_devices[dev]['index'] + ': ' + current_audio_devices[dev]['name']) {
              option_gone = false;
            }
          }
          if (option_gone) {
            speaker_list.remove(opt);
          }
        }

    } catch(err) {
        console.log(err);
        return err;
    }
}

get_audio_devices()
setInterval(get_audio_devices, 5000);

async function test_speaker(){
  var speaker_list = document.getElementById("speakers");
  var speaker_index = parseInt(speaker_list[speaker_list.selectedIndex].value[0]);
  try {
    ajax_post("/testspeaker", {'index': speaker_index});
  } catch(err) {
      console.log(err);
      return err;
  }
}

async function test_microphone(){
  var e = document.getElementById("microphones");
  var microphone = e.options[e.selectedIndex].value;
  var index = microphone[0];
  try {
    ajax_post("/testmicrophone", {'index': index});
    alert("Now say something...")
  } catch(err) {
      console.log(err);
      return err;
  }
}

async function third_signin(){
  try {
    ajax_post("/thirdsignin");
  } catch(err) {
      console.log(err);
      return err;
  }
}