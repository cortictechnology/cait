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
var nlp_models = [];
var virtual_processors = {"Vision": [], "STT": [], "TTS": [], "NLP": []}
var control_hubs = [];
var added_hubs = [];

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

setInterval(function() {
  myInterpreter_cloud = new Interpreter(get_cloud_accounts_code, cloudAccounts);
  get_cloud_accounts();
}, 5000);


function NLPModels(interpreter, scope) {
  var wrapper = function(callback) {
    $.post("/get_nlp_models",
    {},
    function(data, status){
      callback(data['models']);
    });
  };
  interpreter.setProperty(scope, 'get_nlp_models',
      interpreter.createAsyncFunction(wrapper));
}


var get_nlp_models_code = "get_nlp_models();";
var myInterpreter_nlp = new Interpreter(get_nlp_models_code, NLPModels);

function get_nlp_models() {
  var options = [];
  if (myInterpreter_nlp.run()) {
    setTimeout(get_nlp_models, 100);
  }
  if (myInterpreter_nlp.value != null) {
    nlp_models = myInterpreter_nlp.value;
  }
}

setInterval(function() {
  myInterpreter_nlp = new Interpreter(get_nlp_models_code, NLPModels);
  get_nlp_models();
}, 5000);

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

setInterval(function() {
  myInterpreter_light = new Interpreter(get_light_device_code, initDevices);
  get_light_devices();
}, 5000);

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

setInterval(function() {
  myInterpreter_mdeia = new Interpreter(get_media_player_code, initDevices);
  get_media_players();
}, 5000);

function ControlHubs(interpreter, scope) {
  var wrapper = function(callback) {
    $.post("/get_control_devices",
    {},
    function(data, status){
      callback(data['control_devices']);
    });
  };
  interpreter.setProperty(scope, 'get_control_devices',
      interpreter.createAsyncFunction(wrapper));
}


var get_control_devices_code = "get_control_devices();";
var myInterpreter_control_devices = new Interpreter(get_control_devices_code, ControlHubs);

function get_control_devices() {
  var options = [];
  if (myInterpreter_control_devices.run()) {
    setTimeout(get_control_devices, 100);
  }
  if (myInterpreter_control_devices.value != null) {
    control_hubs = [];
    for (var i = 0; i < myInterpreter_control_devices.value.length; i++){
      if (myInterpreter_control_devices.value[i]['device'] == "EV3") {
        control_hubs.push(myInterpreter_control_devices.value[i]['device'] + ": " + myInterpreter_control_devices.value[i]['ip_addr']);
      } else {
        control_hubs.push(myInterpreter_control_devices.value[i]['device'] + ": " + myInterpreter_control_devices.value[i]['mac_addr']);
      }
    }
  }
}

setInterval(function() {
  myInterpreter_control_devices = new Interpreter(get_control_devices_code, ControlHubs);
  get_control_devices();
}, 3000);


function update_added_hub_list() {
  var allBlocks = workspace.getAllBlocks();
  for (blk in allBlocks){
    if (allBlocks[blk].type == "add_control_hub" && allBlocks[blk].isEnabled()) {
      var hub_name = allBlocks[blk].inputList[0].fieldRow[1].value_;
      var index = added_hubs.indexOf(hub_name);
      if (index == -1) {
        added_hubs.push(hub_name);
      }
    }
  }
}

setInterval(update_added_hub_list, 1000);

load_workspace(true);