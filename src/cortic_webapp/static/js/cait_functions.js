/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

async function ajax_post(url, data) {
    return $.ajax({
      url: url,
      type: 'POST',
      data: data
    });
  }
  
  async function recognize_face() {
    try {
      const res = await ajax_post("/recognizeface", {});
      console.log(res);
      return res;
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function add_person(name) {
    try {
      const res = await ajax_post("/addperson", {'name' : name});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function delete_person(name) {
    try {
      const res = await ajax_post("/removeperson", {'name' : name});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function detect_objects() {
    try {
      const res = await ajax_post("/detectobject", {});
      //console.log(res);
      return res;
    } catch(err) {
      console.log(err);
      return err;
    }
  }
  
  async function listen() {
    try {
      const res = await ajax_post("/listen", {});
      console.log(res);
      return res['text'];
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function say(text) {
    try {
      console.log("Saying: " + text)
      const res = await ajax_post("/say", {'text' : text});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function analyze(text) {
    try {
      const res = await ajax_post("/analyze", {'text' : text});
      console.log(res);
      return res;
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function rotate_motor(motor_name, angle) {
    try {
      const res = await ajax_post("/rotate_motor", {'motor_name' : motor_name, 'angle' : angle});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function control_motor(motor_name, speed, duration) {
    try {
      const res = await ajax_post("/control_motor", {'motor_name' : motor_name, "speed" : speed, "duration" : duration});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  
  async function control_motor_speed_group(operation_list) {
    try {
      dataToSend = JSON.stringify({ 'operation_list': operation_list });
      const res = await ajax_post("/control_motor_speed_group", {'data' : dataToSend});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function control_motor_degree_group(operation_list) {
    try {
      dataToSend = JSON.stringify({ 'operation_list': operation_list });
      const res = await ajax_post("/control_motor_degree_group", {'data' : dataToSend});
      console.log(res);
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function init(component_name, mode="online", processor="local", account="default") {
    try{
      loader.style.display="flex";
      document.getElementById("loading_text").innerHTML = "Initializing " + component_name + " component...";
      const res = await ajax_post("/initialize_component", {'component_name': component_name, 'mode' : mode, 'processor' : processor, 'account' : account});
      loader.style.display="none";
      if(res['success'] == false) {
        alert(res["error"] + ". Please fix the problem and click Run again in 10 seconds");
      }
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function set_module_parameters(parameter_name, value) {
    try {
      loader.style.display="flex";
      document.getElementById("loading_text").innerHTML = "Setting parameter values...";
      const res = await ajax_post("/change_module_parameters", {'parameter_name' : parameter_name, "value" : value});
      console.log(res);
      loader.style.display="none";
    } catch(err) {
        console.log(err);
        return err;
    }
  }
  
  async function init_vision(processor) {
    await init("vision", "offline", processor);
    stopStreaming = false;
  }
  
  async function init_voice(mode, account) {
    await init("voice", mode, "local", account);
  }
  
  async function init_nlp() {
    await init("nlp");
  }
  
  async function init_control() {
    await init("control");
  }
  
  async function init_smarthome() {
    return;
  }
  
  async function control_light(device_name, operation, parameter) {
    try {
      console.log("device name: " + device_name + ", operation: " + operation);
      const res = await ajax_post("/control_light", {'device_name' : device_name, 'operation' : operation, 'parameter' : parameter});
      console.log(res);
    } catch(err) {
      console.log(err);
      return err;
    }
  }
  
  async function get_name(intention) {
    if (((intention)['topic']) == 'user_give_name') {
      entities = ((intention)['entities'])[0];
      name = ((entities)['entity_value']);
    }
    return name;
  }
  
  async function control_media_player(device_name, operation) {
    try {
      console.log("device name: " + device_name + ", operation: " + operation);
      const res = await ajax_post("/control_media_player", {'device_name' : device_name, 'operation' : operation});
      console.log(res);
    } catch(err) {
      console.log(err);
      return err;
    }
  }
  
  async function move(motors, direction) {
    motor_group = [];
    for (i in motors){
      motor = motors[i]
      movement = {};
      if (direction == 'forward') {
        movement = {'motor_name': motor, 'speed': 100, 'duration': 1}
      }
      else if (direction == 'backward') {
        movement = {'motor_name': motor, 'speed': -100, 'duration': 1}
      }
      motor_group.push(movement);
    }
    await control_motor_speed_group(motor_group);
  }
  
  async function rotate(motors, degree) {
    actual_degree = 1600 * degree / 360;
    var negative_one = 1;
    motor_group = [];
    for (i in motors){
      motor = motors[i]
      movement = {'motor_name': motor, 'angle': actual_degree * negative_one};
      negative_one = negative_one * -1;
      motor_group.push(movement);
    }
    await control_motor_degree_group(motor_group);
  }