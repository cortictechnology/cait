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
      var device_list = document.getElementById("microphones");
        device_list.innerHTML = "";
        var new_device = [];
        for (var i = 0; i < result.length; i++) {
            device = result[i];
            device_name = device["index"] + ": " + device["device"];
            new_device.push(device_name);
            if (current_audio_devices.includes(device_name) == false){
              current_audio_devices.push(device_name);
            }
        }
        for (var j = 0; j < result.length; j++) {
            exist_device = current_audio_devices[j];
            if (new_device.includes(exist_device) == false){
              current_audio_devices.splice(j, 1);
            } 
        }
        for (var k = 0; k < result.length; k++) {
            device = current_audio_devices[k];
            var option = document.createElement("option");
            option.text = device;
            device_list.add(option);
        }
    } catch(err) {
        console.log(err);
        return err;
    }
}

get_audio_devices()
setInterval(get_audio_devices, 5000);

async function test_speaker(){
  try {
    ajax_post("/testspeaker", {});
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