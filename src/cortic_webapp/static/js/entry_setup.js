/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

var stopStreaming = true;
var hostname = window.location.hostname
var clientID = "blockly_" + parseInt(Math.random() * 100);
var client = new Paho.Client(hostname, 8083, clientID);

client.onConnectionLost = onConnectionLost;
client.onMessageArrived = onMessageArrived;
client.connect({onSuccess:onConnect});

function onConnect() {
  // Once a connection has been made, make a subscription and send a message.
  console.log("Connected to cait");
  client.subscribe("cait/displayFrame");
  stopVideoFeed();
  emptyVisionMode();
  stopVoice();
  resetModules();
}

// called when the client loses its connection
function onConnectionLost(responseObject) {
  if (responseObject.errorCode !== 0) {
    console.log("onConnectionLost:"+responseObject.errorMessage);
  }
}

// called when a message arrives
function onMessageArrived(message) {
  //console.log("onMessageArrived:");
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

var light_devices = [];
var media_players = [];
var cloud_accounts = [];
var virtual_processors = {"Vision": [], "STT": [], "TTS": [], "NLP": []}

function initVProcessors(interpreter, scope) {
  var wrapper = function(processor_type, callback) {
    $.post("/get_virtual_processors",
    {
      'processor_type': processor_type
    },
    function(data, status){
      callback(data['virtual_processors']);
    });
  };
  interpreter.setProperty(scope, 'get_virtual_processors',
      interpreter.createAsyncFunction(wrapper));
}

function initDevices(interpreter, scope) {
  var wrapper = function(device_type, callback) {
    $.post("/get_states",
    {
      'device_type': device_type
    },
    function(data, status){
      callback(data['devices']);
    });
  };
  interpreter.setProperty(scope, 'get_devices',
      interpreter.createAsyncFunction(wrapper));
}

function cloudAccounts(interpreter, scope) {
  var wrapper = function(callback) {
    $.post("/get_cloud_accounts",
    {},
    function(data, status){
      callback(data['accounts']);
    });
  };
  interpreter.setProperty(scope, 'get_cloud_accounts',
      interpreter.createAsyncFunction(wrapper));
}

var get_light_device_code = "get_devices('light');";
var myInterpreter_light = new Interpreter(get_light_device_code, initDevices);

function get_light_devices() {
  var options = [];
  if (myInterpreter_light.run()) {
    setTimeout(get_light_devices, 100);
  }
  if (myInterpreter_light.value != null) {
    light_devices = myInterpreter_light.value;
  }
}

get_light_devices();

var get_media_player_code = "get_devices('media_player');";
var myInterpreter_mdeia = new Interpreter(get_media_player_code, initDevices);

function get_media_players() {
  var options = [];
  if (myInterpreter_mdeia.run()) {
    setTimeout(get_media_players, 100);
  }
  if (myInterpreter_mdeia.value != null) {
    media_players = myInterpreter_mdeia.value;
  }
}

get_media_players();

var get_cloud_accounts_code = "get_cloud_accounts();";
var myInterpreter_cloud = new Interpreter(get_cloud_accounts_code, cloudAccounts);

function get_cloud_accounts() {
  var options = [];
  if (myInterpreter_cloud.run()) {
    setTimeout(get_cloud_accounts, 100);
  }
  if (myInterpreter_cloud.value != null) {
    cloud_accounts = myInterpreter_cloud.value;
  }
}

get_cloud_accounts();

var get_vision_processor_code = "get_virtual_processors('Vision');";
var myInterpreter_vision = new Interpreter(get_vision_processor_code, initVProcessors);
var get_stt_processor_code = "get_virtual_processors('STT');";
var myInterpreter_stt = new Interpreter(get_stt_processor_code, initVProcessors);
var get_tts_processor_code = "get_virtual_processors('TTS');";
var myInterpreter_tts = new Interpreter(get_tts_processor_code, initVProcessors);
var get_nlp_processor_code = "get_virtual_processors('NLP');";
var myInterpreter_nlp = new Interpreter(get_nlp_processor_code, initVProcessors);

function get_vision_processors() {
  var options = [];
  if (myInterpreter_vision.run()) {
    setTimeout(get_vision_processors, 100);
  }
  if (myInterpreter_vision.value != null) {
    vision_processors = myInterpreter_vision.value;
    virtual_processors["Vision"] = vision_processors
    myInterpreter_vision = new Interpreter(get_vision_processor_code, initVProcessors);
  }
}

function get_stt_processors() {
  var options = [];
  if (myInterpreter_stt.run()) {
    setTimeout(get_stt_processors, 100);
  }
  if (myInterpreter_stt.value != null) {
    stt_processors = myInterpreter_stt.value;
    virtual_processors["STT"] = stt_processors
  }
}

function get_tts_processors() {
  var options = [];
  if (myInterpreter_tts.run()) {
    setTimeout(get_tts_processors, 100);
  }
  if (myInterpreter_tts.value != null) {
    tts_processors = myInterpreter_tts.value;
    virtual_processors["TTS"] = tts_processors
  }
}

function get_nlp_processors() {
  var options = [];
  if (myInterpreter_nlp.run()) {
    setTimeout(get_nlp_processors, 100);
  }
  if (myInterpreter_nlp.value != null) {
    nlp_processors = myInterpreter_nlp.value;
    virtual_processors["NLP"] = nlp_processors
  }
}

var stt_processors_dropdown = new Blockly.FieldDropdown(function() {
  var options = [];
  var stt_processors = virtual_processors['STT'];
  if (stt_processors.length > 0) {
    for (i in stt_processors) {
      options.push([stt_processors[i], stt_processors[i]])
    }
  }
  else {
    options.push(['none', 'none']);
  }
  return options;
});

var tts_processors_dropdown = new Blockly.FieldDropdown(function() {
  var options = [];
  var tts_processors = virtual_processors['TTS'];
  if (tts_processors.length > 0) {
    for (i in tts_processors) {
      options.push([tts_processors[i], tts_processors[i]])
    }
  }
  else {
    options.push(['none', 'none']);
  }
  return options;
});

var nlp_processors_dropdown = new Blockly.FieldDropdown(function() {
  var options = [];
  var nlp_processors = virtual_processors['NLP'];
  if (nlp_processors.length > 0) {
    for (i in nlp_processors) {
      options.push([nlp_processors[i], nlp_processors[i]])
    }
  }
  else {
    options.push(['none', 'none']);
  }
  return options;
});

function get_virtual_processors() {
  if (Blockly.getMainWorkspace().getBlocksByType('init_vision').length > 0){
    get_vision_processors();
    vision_blocks = Blockly.getMainWorkspace().getBlocksByType("init_vision");
    if(virtual_processors['Vision'].length == 0) {
      for (i in vision_blocks) {
        if (vision_blocks[i].getInput('proc_param').fieldRow[1].value_ == "virtual") {
          vision_blocks[i].getInput('proc_param').fieldRow[4].setText('none');
          vision_blocks[i].getInput('proc_param').fieldRow[4].setValue('none');
        }
      }
    }
  }
  if (Blockly.getMainWorkspace().getBlocksByType('init_voice').length > 0){
    get_stt_processors();
    get_tts_processors();
  }
  if (Blockly.getMainWorkspace().getBlocksByType('init_nlp').length > 0){
    get_nlp_processors();
  }
}

setInterval(get_virtual_processors, 1000);