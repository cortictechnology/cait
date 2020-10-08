/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

function replaceAll(str, find, replace) {
    return str.replace(new RegExp(find, 'g'), replace);
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

function stopVoice() {
  topicMessage = new Paho.Message("VoiceDown");
  topicMessage.topic = "cait/voice_control";
  client.publish(topicMessage)
}

function resetModules() {
  topicMessage = new Paho.Message("Reset");
  topicMessage.topic = "cait/module_states";
  client.publish(topicMessage)
}

function updateFunction(event) {
  var block = workspace.getBlockById(event.blockId);

  if (event.type == Blockly.Events.BLOCK_CHANGE) {
    if (event.element == "field") {
      if (event.oldValue == "color_name" || event.oldValue == "brightness_pct") {
        block.getInput("param_input").removeField('parameter');
      }
      if (event.newValue == "color_name" || event.newValue == "brightness_pct") {
        block.getInput("param_input").appendField(
          new Blockly.FieldTextInput(), "parameter"
        )
      }
      if (event.oldValue == "offline") {
        block.getInput("cloud_accounts").setVisible(true);
        block.getInput("ending").setVisible(true);
        block.render();
      }
      if (event.newValue == "offline") {
        block.getInput("cloud_accounts").setVisible(false);
        block.getInput("ending").setVisible(false);
        block.render();
      }
      if (event.oldValue == "virtual") {
        block.getInput("proc_param").removeField("on");
        block.getInput("proc_param").removeField("vision_proc");
      }

      if (event.newValue == "virtual") {
        block.getInput("proc_param").appendField(
          new Blockly.FieldLabel("on"), "on");
          block.getInput("proc_param").appendField(new Blockly.FieldDropdown(function() {
          var options = [];
          var vision_processors = virtual_processors['Vision'];
          if (vision_processors.length > 0) {
            for (i in vision_processors) {
              options.push([vision_processors[i], vision_processors[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'vision_proc');
      }
    }
  }

  if (event.type == Blockly.Events.BLOCK_MOVE) {
    var parentBlock = workspace.getBlockById(event.newParentId);
    if (block != null){
      if (block.type == "init_vision" || 
          block.type == "init_voice" || 
          block.type == "init_nlp" || 
          block.type == "init_control" ||  
          block.type == "init_smarthome" ||
          block.type == "set_parameter") {
        var within_setup_block = false;
        while (parentBlock != null) {
          if (parentBlock.type == "setup_block") {
            within_setup_block = true;
            block.setEnabled(true);
            break;
          }
          else {
            parentBlock = parentBlock.parentBlock_;
          }
        }
        if (!within_setup_block) {
          block.setEnabled(false);
        }
      }
      else if (block.type == "setup_block" || block.type == "main_block") {
        block.setEnabled(true);
      }
      else {
        var within_main_block = false;
        while (parentBlock != null) {
          if (parentBlock.type == "main_block" || parentBlock.type.indexOf('procedures_') != -1) {
            within_main_block = true;
            block.setEnabled(true);
            break;
          }
          else {
            parentBlock = parentBlock.parentBlock_;
          }
        }
        if (!within_main_block) {
          block.setEnabled(false);
          if (block.type.indexOf("vision_") != -1) {
            console.log(block.type);
            emptyVisionMode();
          }
        }
      }
      if (block.parentBlock_ != null) {
        if (block.parentBlock_.type == "set_parameter" && !block.parentBlock_.isDisabled){
          block.setEnabled(true);
        }
      }
      if (block.type.indexOf('procedures_') != -1) {
        block.setEnabled(true);
      } 
    }
  }
}

var stopCode = false;

function run_code() {
  //var xml = Blockly.Xml.workspaceToDom(workspace);
  //var xml_text = Blockly.Xml.domToText(xml);
  //console.log(xml_text);
  stopCode = false;
  Blockly.JavaScript.addReservedWords('code');

  var code = Blockly.JavaScript.workspaceToCode(workspace);
  save_workspace(true);
  try {
    if (code.indexOf("await") != -1){
      if (code.indexOf("function") != -1) {
        if (code[code.indexOf("function")-1] != '_' || code[code.indexOf("function")+8] != '_'){
          code = replaceAll(code, 'function', 'async function');
        }
      }
      async_function = [];
      index = 0;
      while(code.indexOf("async function", index) != -1) {
        begin_idx = code.indexOf("async function", index) + 15;
        end_idx = code.indexOf("(", begin_idx);
        func_name = code.substring(begin_idx, end_idx);
        if (func_name.indexOf("async function") != -1) {
          end_idx = begin_idx;
        }
        else {
          async_function.push(func_name);
        }
        index = end_idx;
      }
      console.log("Async Functions: " + async_function);
      init_idx = code.indexOf("await init_");
      runtime_code = code.substring(init_idx, code.length);
      for (f in async_function) {
        runtime_code = replaceAll(runtime_code, async_function[f], "await " + async_function[f]);
      }
      code = code.substring(0, init_idx) + runtime_code;
      code = "(async () => {" + code + "})()";
    }
    var ready_to_execute_code = true;
    for (i in vision_func){
      if (code.indexOf(vision_func[i]) != -1){
        if (code.indexOf('init_vision') == -1) {
          alert("Vision is not initialized. Please initialize it in the setup block first");
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in speech_func){
      if (code.indexOf(speech_func[i]) != -1){
        if (code.indexOf('init_voice') == -1) {
          alert("Speech is not initialized. Please initialize it in the setup block first");
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in nlp_func){
      if (code.indexOf(nlp_func[i]) != -1){
        if (code.indexOf('init_nlp') == -1) {
          alert("NLP is not initialized. Please initialize it in the setup block first");
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in control_func){
      if (code.indexOf(control_func[i]) != -1){
        if (code.indexOf('init_control') == -1) {
          alert("Control is not initialized. Please initialize it in the setup block first");
          ready_to_execute_code = false;
          break;
        }
      }
    }
    for (i in smart_home_func){
      if (code.indexOf(smart_home_func[i]) != -1){
        if (code.indexOf('init_smarthome') == -1) {
          alert("Smart Home Control is not initialized. Please initialize it in the setup block first");
          ready_to_execute_code = false;
          break;
        }
      }
    }
    console.log(code);
    if (ready_to_execute_code){
      eval(code);
    }
  } catch (e) {
    alert(e);
  }
}

$(document).ready(function () {
  if (window.location.hash == '#reload') {
    onReload();
  }
});

function onReload () {
  window.location.hash = '';
  load_workspace(true);
}

function stop_code() {
  window.location.hash = '#reload';
  location.reload();
}

async function gen_py_code() {
  Blockly.Python.addReservedWords('code');
  var code = Blockly.Python.workspaceToCode(workspace);
  var filename;
  filename = prompt("Filename to save generated python code: ");
  if(filename != ''){
    const res = await $.ajax({
      url: "/savepythoncode",
      type: 'POST',
      data: {"filename" : filename, 
              "code" : code}
    });
  }
}

async function gen_py_notebook() {
  Blockly.Python.addReservedWords('code');
  var code = Blockly.Python.workspaceToCode(workspace);
  var filename;
  filename = prompt("Filename to save generated jupyter notebook: ");
  if(filename != ''){
    const res = await $.ajax({
      url: "/savenotebook",
      type: 'POST',
      data: {"filename" : filename, 
              "code" : code}
    });
  }
}

async function save_workspace(autosave=false) {
  var xml = Blockly.Xml.workspaceToDom(workspace);
  var xml_text = Blockly.Xml.domToText(xml);
  var filename;
  var path;
  if (autosave) {
    save_type = "autosave";
    filename="workspace_autosave.xml";
  }
  else {
    save_type = "save";
    filename = prompt("Filename to save: ");
  }
  if(filename != ''){
    const res = await $.ajax({
      url: "/saveworkspace",
      type: 'POST',
      data: {"filename" : filename, 
              "xml_text" : xml_text,
              "save_type": save_type}
    });
  }
  //console.log(res);
}

async function load_workspace(from_autosave=false) {
  var filename;
  var path;
  var autosave;
  if(from_autosave) {
    save_type = "autosave";
    filename="workspace_autosave.xml";
  }
  else {
    save_type = "save";
    filename = prompt("Filename to load: ");
  }
  const res = await $.ajax({
    url: "/loadworkspace",
    type: 'POST',
    data: {"filename" : filename, "save_type": save_type }
  });
  //console.log(res);
  xml_text = res['xml_text'];
  if (xml_text != ''){
    var xml = Blockly.Xml.textToDom(xml_text);
    Blockly.Xml.domToWorkspace(xml, workspace);
  }
}