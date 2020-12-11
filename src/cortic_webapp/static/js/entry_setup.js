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

get_cloud_accounts();


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

get_nlp_models()


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

load_workspace(true);