/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

var vision_func = ["recognize_face", "add_person", "delete_person", "detect_objects"];
var speech_func = ["listen", "say"];
var nlp_func = ["analyze"];
var control_func = ["rotate_motor", "control_motor", "control_motor_speed_group", "control_motor_degree_group", "move", "rotate"];
var smart_home_func = ["control_light", "control_media_player"]

Blockly.defineBlocksWithJsonArray([
    {
      "type": "setup_block",
      "message0": "setup",
      "message1": "%1",
      "args1": [
        {
          "type": "input_statement",
          "name": "init_blocks"
        }
      ],
      "colour" : "#1d8cf7",
      "tooltip": "Setup point of the program.",
      "helpUrl": ""
    },
    {
      "type": "main_block",
      "message0": "main",
      "message1": "%1",
      "args1": [
        {
          "type": "input_statement",
          "name": "main_blocks"
        }
      ],
      "colour" : "#1d8cf7",
      "tooltip": "Entry point of the program.",
      "helpUrl": ""
    },
    {
      "type": "set_parameter",
      "message0": "set parameter %1 %2 %3 to value %4",
      "args0": [
        {
          "type": "input_dummy",
          "align": "CENTRE"
        },
        {
          "type": "field_input",
          "name": "parameter",
          "text": ""
        },
        {
          "type": "input_dummy",
          "align": "CENTRE"
        },
        {
          "type": "input_value",
          "name": "value"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#1d8cf7",
      "tooltip": "",
      "helpUrl": ""
    },
    {
      "type": "init_vision",
      "message0": "initialize vision",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "processor",
          "options": [
            [
              "local",
              "local"
            ],
            [
              "virtual",
              "virtual"
            ]
          ]
        },
        {
          "type": "input_dummy",
          "name" : "proc_param",
          "align": "CENTRE"
        },
        {
          "type": "input_dummy",
          "name": "ending",
          "text": ""
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#5D0095",
      "tooltip": "Initialize the voice component",
      "helpUrl": ""
    },
    {
      "type": "init_voice",
      "lastDummyAlign0": "CENTRE",
      "message0": "initialize voice with %1 mode %2 using %3 account %4",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "mode",
          "options": [
            [
              "online",
              "online"
            ],
            [
              "offline",
              "offline"
            ]
          ]
        },
        {
          "type": "input_dummy",
          "name" : "params",
          "align": "CENTRE"
        },
        {
          "type": "input_dummy",
          "name" : "cloud_accounts",
          "align": "CENTRE"
        },
        {
          "type": "input_dummy",
          "name": "ending",
          "text": ""
        }
      ],
      "extensions": ["dynamic_cloud_accounts_extension"],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#019191",
      "tooltip": "Initialize the voice component",
      "helpUrl": ""
    },
    {
      "type": "init_nlp",
      "lastDummyAlign0": "CENTRE",
      "message0": "initialize nlp",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#3ACFF7",
      "tooltip": "Initialize the nlp component",
      "helpUrl": ""
    },
    {
      "type": "init_control",
      "lastDummyAlign0": "CENTRE",
      "message0": "initialize control",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "Initialize the control component",
      "helpUrl": ""
    },
    {
      "type": "init_smarthome",
      "lastDummyAlign0": "CENTRE",
      "message0": "initialize smart home control",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F70090",
      "tooltip": "Scan for available devices, initialize their status",
      "helpUrl": ""
    },
    {
      "type": "vision_recognize_face",
      "message0": "Recognize Face",
      "inputsInline": true,
      "output": "String",
      "colour": "#5D0095",
      "tooltip": "Recognize the person above the specific confidence in scene",
      "helpUrl": ""
    },
    {
      "type": "vision_add_person",
      "message0": "Add person with name %1",
      "args0": [
        {
          "type": "input_value",
          "name": "person_name",
          "align": "CENTRE"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#5D0095",
      "tooltip": "Add a new person into database with input name",
      "helpUrl": ""
    },
    {
      "type": "vision_remove_person",
      "message0": "Remove person named %1",
      "args0": [
        {
          "type": "input_value",
          "name": "person_name",
          "align": "CENTRE"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#5D0095",
      "tooltip": "Remove a person from database with specific name",
      "helpUrl": ""
    },
    {
      "type": "vision_detect_objects",
      "lastDummyAlign0": "CENTRE",
      "message0": "detect objects",
      "inputsInline": true,
      "output": null,
      "colour": "#5D0095",
      "tooltip": "Detect objects in front of camera",
      "helpUrl": ""
    },
    {
      "type": "listen",
      "lastDummyAlign0": "CENTRE",
      "message0": "listen for user speech",
      "output": null,
      "colour": "#019191",
      "tooltip": "Listen to user speech, and output that as text",
      "helpUrl": ""
    },
    {
      "type": "say",
      "lastDummyAlign0": "CENTRE",
      "message0": "say %1",
      "args0": [
        {
          "type": "input_value",
          "name": "text",
          "align": "CENTRE"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#019191",
      "tooltip": "Convert text to audio speech",
      "helpUrl": ""
    },
    {
      "type": "analyze",
      "message0": "analyze %1",
      "args0": [
        {
          "type": "input_value",
          "name": "text",
          "align": "CENTRE"
        }
      ],
      "output": null,
      "colour": "#3ACFF7",
      "tooltip": "Analyze text from input",
      "helpUrl": ""
    },
    {
      "type": "get_name",
      "message0": "get name with: intention %1",
      "args0": [
        {
          "type": "input_value",
          "name": "intention",
          "align": "CENTRE"
        }
      ],
      "inputsInline": true,
      "output": null,
      "colour": "#3252D4",
      "tooltip": "Get person name from an intention",
      "helpUrl": ""
    },
    {
      "type": "comment",
      "message0": "Comment:  %1",
      "args0": [
        {
          "type": "input_value",
          "name": "comment",
          "check": "String"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#B2820B",
      "tooltip": "Comment Block",
      "helpUrl": ""
    },
    {
      "type": "create_empty_dictionary",
      "message0": "Create empty dictionary",
      "inputsInline": true,
      "output": null,
      "colour": "#001F4E",
      "tooltip": "Create an empty Dictionary",
      "helpUrl": ""
    },
    {
      "type": "dictionary_keys",
      "message0": "In dictionary %1 get list of keys",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        }
      ],
      "inputsInline": true,
      "output": null,
      "colour": "#001F4E",
      "tooltip": "Get a list of keys from the dictionary",
      "helpUrl": ""
    },
    {
      "type": "dictionary_value",
      "message0": "In dictionary %1 get value for key %2",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        },
        {
          "type": "input_value",
          "name": "key_name"
        }
      ],
      "inputsInline": true,
      "output": null,
      "colour": "#001F4E",
      "tooltip": "Get value from a dictionary with a specific key",
      "helpUrl": ""
    },
    {
      "type": "dictionary_value_set",
      "message0": "In dictionary %1 set value for key %2 to %3",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        },
        {
          "type": "input_value",
          "name": "key_name"
        },
        {
          "type": "input_value",
          "name": "value"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#001F4E",
      "tooltip": "Set the value from a dictionary with a specific key",
      "helpUrl": ""
    },
    {
      "type": "dictionary_remove",
      "message0": "In dictionary %1 remove value with key %2",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        },
        {
          "type": "input_value",
          "name": "key_name"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#001F4E",
      "tooltip": "Remove a key-value pair from dictionary",
      "helpUrl": ""
    },
    {
      "type": "dictionary_add",
      "message0": "In dictionary %1 add key %2 with value %3",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        },
        {
          "type": "input_value",
          "name": "key_name"
        },
        {
          "type": "input_value",
          "name": "value"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#001F4E",
      "tooltip": "Add a key-value pair to dictionary",
      "helpUrl": ""
    },
    {
      "type": "motor_speed_block",
      "message0": "setup motor group speed %1 %2",
      "args0": [
        {
          "type": "input_dummy",
          "align": "CENTRE"
        },
        {
          "type": "input_statement",
          "name": "statements",
          "align": "CENTRE"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "Execute motor controls concurrently",
      "helpUrl": ""
    },
    {
      "type": "motor_degree_block",
      "message0": "setup motor group angle %1 %2",
      "args0": [
        {
          "type": "input_dummy",
          "align": "CENTRE"
        },
        {
          "type": "input_statement",
          "name": "statements",
          "align": "CENTRE"
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "Rotate motor for certain degrees concurrently",
      "helpUrl": ""
    },
    {
      "type": "motor_control",
      "lastDummyAlign0": "CENTRE",
      "message0": "set motor %1 %2 to speed %3 for %4 second(s)",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "motor_name",
          "options": [
            [
              "motor_A",
              "motor_A"
            ],
            [
              "motor_B",
              "motor_B"
            ],
            [
              "motor_C",
              "motor_C"
            ],
            [
              "motor_D",
              "motor_D"
            ]
          ]
        },
        {
          "type": "input_dummy"
        },
        {
          "type": "input_value",
          "name": "speed",
          "check": "Number"
        },
        {
          "type": "input_value",
          "name": "duration",
          "check": "Number"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "Control individual motor motion",
      "helpUrl": ""
    },
    {
      "type": "motor_rotate",
      "message0": "rotate motor %1 for %2 %3 degree(s)",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "motor_name",
          "options": [
            [
              "motor_A",
              "motor_A"
            ],
            [
              "motor_B",
              "motor_B"
            ],
            [
              "motor_C",
              "motor_C"
            ],
            [
              "motor_D",
              "motor_D"
            ]
          ]
        },
        {
          "type": "input_dummy"
        },
        {
          "type": "input_value",
          "name": "degree",
          "check": "Number"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "Rotate the motor to certain degree",
      "helpUrl": ""
    },
    {
      "type": "move",
      "lastDummyAlign0": "RIGHT",
      "message0": "move with: motors %1 direction %2",
      "args0": [
        {
          "type": "input_value",
          "name": "motors",
          "align": "CENTRE"
        },
        {
          "type": "field_dropdown",
          "name": "direction",
          "options": [
            [
              "forward",
              "forward"
            ],
            [
              "backward",
              "backward"
            ]
          ]
        }
      ],
      "previousStatement": null,
      "nextStatement": null,
      "inputsInline": true,
      "colour": "#3252D4",
      "tooltip": "Get person name from an intention",
      "helpUrl": ""
    },
    {
      "type": "turn",
      "lastDummyAlign0": "CENTRE",
      "message0": "turn with: motors %1 degree %2",
      "args0": [
        {
          "type": "input_value",
          "name": "motors",
          "align": "CENTRE"
        },
        {
          "type": "field_number",
          "name": "degree",
          "value": 0,
          "min": -360,
          "max": 360,
          "precision": 1
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#3252D4",
      "tooltip": "Turn the robot to certain degree",
      "helpUrl": ""
    },
    {
      "type": "lights",
      "message0": "for light %1 perform %2 %3 %4",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "light_devices",
          "align": "CENTRE"
        },
        {
          "type": "field_dropdown",
          "name": "operation",
          "options": [
            [
              "turn on",
              "turn_on"
            ],
            [
              "turn off",
              "turn_off"
            ],
            [
              "toggle",
              "toggle"
            ],
            [
              "change colour to",
              "color_name"
            ],
            [
              "set brightness to (0-100)",
              "brightness_pct"
            ]
          ]
        },
        {
          "type": "input_dummy",
          "name" : "param_input",
          "align": "CENTRE"
        },
        {
          "type": "input_dummy",
          "name": "ending",
          "text": ""
        }
      ],
      "extensions": ["dynamic_lights_extension"],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F70090",
      "tooltip": "Control media player devices",
      "helpUrl": ""
    },
    {
      "type": "media_player",
      "lastDummyAlign0": "CENTRE",
      "message0": "for media player %1 perform %2",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "media_players",
          "align": "CENTRE"
        },
        {
          "type": "field_dropdown",
          "name": "operation",
          "options": [
            [
              "play musics",
              "media_play"
            ],
            [
              "pause musics",
              "media_pause"
            ],
            [
              "volume up",
              "volume_up"
            ],
            [
              "volume down",
              "volume_down"
            ]
          ]
        }
      ],
      "extensions": ["dynamic_media_players_extension"],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F70090",
      "tooltip": "Control media player devices",
      "helpUrl": ""
    }
  ]);

// var required_modules = [];

Blockly.Extensions.register('dynamic_lights_extension',
  function() {
    this.getInput('light_devices')
      .appendField(new Blockly.FieldDropdown(
        function() {
          var options = [];
          if (light_devices.length > 0) {
            for (i in light_devices) {
              options.push([light_devices[i], light_devices[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'light');
  });

Blockly.Extensions.register('dynamic_media_players_extension',
function() {
  this.getInput('media_players')
    .appendField(new Blockly.FieldDropdown(
      function() {
        var options = [];
        if (media_players.length > 0) {
          for (i in media_players) {
            options.push([media_players[i], media_players[i]])
          }
        }
        else {
          options.push(['none', 'none']);
        }
        return options;
      }), 'media_player');
});

Blockly.Extensions.register('dynamic_cloud_accounts_extension',
function() {
  this.getInput('cloud_accounts')
    .appendField(new Blockly.FieldDropdown(
      function() {
        var options = [];
        if (cloud_accounts.length > 0) {
          for (i in cloud_accounts) {
            options.push([cloud_accounts[i], cloud_accounts[i]])
          }
        }
        else {
          options.push(['none', 'none']);
        }
        return options;
      }), 'accounts');
});

if (cloud_accounts.length < 1) {

}

Blockly.JavaScript['setup_block'] = function(block) {
  var statements_main = Blockly.JavaScript.statementToCode(block, 'init_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index+1) + statements_main.substring(index+3, statements_main.length);
    index = statements_main.indexOf("\n", index+1);
  }
  var code = "// Initialize and setup different components\n" + statements_main;
  return code;
};

Blockly.Python['setup_block'] = function(block) {
  var statements_main = Blockly.Python.statementToCode(block, 'init_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index+1) + statements_main.substring(index+3, statements_main.length);
    index = statements_main.indexOf("\n", index+1);
  }
  var code = "import cait.essentials\n\n" + "# Initialize and setup different components\n" + statements_main;
  return code;
};

Blockly.JavaScript['main_block'] = function(block) {
  var statements_main = Blockly.JavaScript.statementToCode(block, 'main_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index+1) + statements_main.substring(index+3, statements_main.length);
    index = statements_main.indexOf("\n", index+1);
  }
  var code = "// Entry point of program\n" + statements_main;
  return code;
};

Blockly.Python['main_block'] = function(block) {
  var statements_main = Blockly.Python.statementToCode(block, 'main_blocks');
  statements_main = statements_main.substring(2, statements_main.length)
  index = statements_main.indexOf("\n");
  while (index != -1) {
    statements_main = statements_main.substring(0, index+1) + statements_main.substring(index+3, statements_main.length);
    index = statements_main.indexOf("\n", index+1);
  }
  var code = "\n# Entry point of program\n" + statements_main;
  return code;
};

Blockly.JavaScript['set_parameter'] = function(block) {
  var text_parameter = block.getFieldValue('parameter');
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "set_module_parameters('" + text_parameter + "', " + value_value +  ");\n";
  return code;
};

Blockly.Python['set_parameter'] = function(block) {
  var text_parameter = block.getFieldValue('parameter');
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.set_module_parameters('" + text_parameter + "', " + value_value +  ")\n";
  return code;
};

Blockly.JavaScript['init_vision'] = function(block) {
  var dropdown_processor = block.getFieldValue('processor');
  if (dropdown_processor == "virtual") {
    dropdown_processor = block.getFieldValue('vision_proc');
    if (dropdown_processor == "none" || dropdown_processor == null){
      dropdown_processor = "local";
    }
  }
  var code = "await init_vision(\"" + dropdown_processor + "\");\n";
  return code;
};

Blockly.Python['init_vision'] = function(block) {
  var dropdown_processor = block.getFieldValue('processor');
  if (dropdown_processor == "local"){
    var code = "cait.essentials.initialize_component('vision', processor='local')\n";
  }
  else {
    var code = "cait.essentials.initialize_component('vision', processor='" + dropdown_processor + "')\n";
  }
  
  return code;
};

Blockly.JavaScript['init_voice'] = function(block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  var code = "await init_voice('" + dropdown_mode + "', '" + dropdown_account + "');\n";
  return code;
};

Blockly.Python['init_voice'] = function(block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  if (dropdown_mode == "online"){
    var code = "cait.essentials.initialize_component('voice', useOnline=True, account='" + dropdown_account + "')\n";
  }
  else {
    var code = "cait.essentials.initialize_component('voice', useOnline=False)\n";
  }
  return code;
};

Blockly.JavaScript['init_nlp'] = function(block) {
  var code = 'await init_nlp();\n';
  return code;
};

Blockly.Python['init_nlp'] = function(block) {
  var code = "cait.essentials.initialize_component('nlp')\n";
  return code;
};

Blockly.JavaScript['init_control'] = function(block) {
  var code = 'await init_control();\n';
  return code;
};

Blockly.Python['init_control'] = function(block) {
  var code = "cait.essentials.initialize_component('control')\n";
  return code;
};

Blockly.JavaScript['init_smarthome'] = function(block) {
  var code = 'await init_smarthome();\n';
  return code;
};

Blockly.Python['init_smarthome'] = function(block) {
  var code = "cait.essentials.initialize_component('smart_home')\n";
  return code;
};

Blockly.JavaScript['create_empty_dictionary'] = function(block) {
  var code = '{}';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['create_empty_dictionary'] = function(block) {
  var code = '{}';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_keys'] = function(block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "Object.keys(" + value_dictionary + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['dictionary_keys'] = function(block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var code = "list(" + value_dictionary + ".keys())";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_value'] = function(block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "(" + value_dictionary + ")[" + value_key_name + "]";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['dictionary_value'] = function(block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + "[" + value_key_name + "]";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['dictionary_value_set'] = function(block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "(" + value_dictionary + ")[" + value_key_name + "] = " + value_value + ";\n";
  return code;
};

Blockly.Python['dictionary_value_set'] = function(block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + "[" + value_key_name + "] = " + value_value + "\n";
  return code;
};

Blockly.JavaScript['dictionary_remove'] = function(block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "delete (" + value_dictionary + ")[" + value_key_name + "];\n";
  return code;
};

Blockly.Python['dictionary_remove'] = function(block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var code = value_dictionary + ".pop(" + value_key_name + ")\n";
  return code;
};

Blockly.JavaScript['dictionary_add'] = function(block) {
  var value_dictionary = Blockly.JavaScript.valueToCode(block, 'dictionary', Blockly.JavaScript.ORDER_ATOMIC);
  var value_key_name = Blockly.JavaScript.valueToCode(block, 'key_name', Blockly.JavaScript.ORDER_ATOMIC);
  var value_value = Blockly.JavaScript.valueToCode(block, 'value', Blockly.JavaScript.ORDER_ATOMIC);
  var code =  "(" + value_dictionary + ")[" + value_key_name + "] = " + value_value + ";\n";
  return code;
};

Blockly.Python['dictionary_add'] = function(block) {
  var value_dictionary = Blockly.Python.valueToCode(block, 'dictionary', Blockly.Python.ORDER_ATOMIC);
  var value_key_name = Blockly.Python.valueToCode(block, 'key_name', Blockly.Python.ORDER_ATOMIC);
  var value_value = Blockly.Python.valueToCode(block, 'value', Blockly.Python.ORDER_ATOMIC);
  var code =  value_dictionary + "[" + value_key_name + "] = " + value_value + "\n";
  return code;
};

Blockly.JavaScript['vision_recognize_face'] = function(block) {
  var code = "await recognize_face()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_recognize_face'] = function(block) {
  var code = "cait.essentials.recognize_face()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['vision_add_person'] = function(block) {
  var value_person_name = Blockly.JavaScript.valueToCode(block, 'person_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await add_person(" + String(value_person_name) + ");\n";
  return code;
};

Blockly.Python['vision_add_person'] = function(block) {
  var value_person_name = Blockly.Python.valueToCode(block, 'person_name', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.add_person(" + String(value_person_name) + ")\n";
  return code;
};

Blockly.JavaScript['vision_remove_person'] = function(block) {
  var value_person_name = Blockly.JavaScript.valueToCode(block, 'person_name', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await delete_person(" + String(value_person_name) + ");\n";
  return code;
};

Blockly.Python['vision_remove_person'] = function(block) {
  var value_person_name = Blockly.Python.valueToCode(block, 'person_name', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.remove_person(" + String(value_person_name) + ")\n";
  return code;
};

Blockly.JavaScript['vision_detect_objects'] = function(block) {
  var code = 'await detect_objects()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_detect_objects'] = function(block) {
  var code = 'cait.essentials.detect_objects()';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['listen'] = function(block) {
  var code = "await listen()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['listen'] = function(block) {
  var code = "cait.essentials.listen()";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['say'] = function(block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'text', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await say(" + value_text + ");\n";
  return code;
};

Blockly.Python['say'] = function(block) {
  var value_text = Blockly.Python.valueToCode(block, 'text', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.say(" + value_text + ")\n";
  return code;
};

Blockly.JavaScript['analyze'] = function(block) {
  var value_text = Blockly.JavaScript.valueToCode(block, 'text', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await analyze(" + value_text + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['analyze'] = function(block) {
  var value_text = Blockly.Python.valueToCode(block, 'text', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.analyse_text(" + value_text + ")";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['get_name'] = function(block) {
  var value_intention = Blockly.JavaScript.valueToCode(block, 'intention', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await get_name(" + value_intention + ")";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_name'] = function(block) {
  var value_intention = Blockly.Python.valueToCode(block, 'intention', Blockly.Python.ORDER_ATOMIC);
  var code = "get_name(" + value_intention + ")";
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.JavaScript['comment'] = function(block) {
  var value_comment = String(Blockly.JavaScript.valueToCode(block, 'comment', Blockly.JavaScript.ORDER_ATOMIC));
  value_comment = value_comment.substring(1, value_comment.length-1);
  var code = "//" + value_comment + "\n";
  return code;
};

Blockly.Python['comment'] = function(block) {
  var value_comment = String(Blockly.Python.valueToCode(block, 'comment', Blockly.Python.ORDER_ATOMIC));
  value_comment = value_comment.substring(1, value_comment.length-1);
  var code = "#" + value_comment + "\n";
  return code;
};

Blockly.JavaScript['motor_rotate'] = function(block) {
  var dropdown_motor_name = block.getFieldValue('motor_name');
  var number_degree = Blockly.JavaScript.valueToCode(block, 'degree', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await rotate_motor('" + dropdown_motor_name + "', " + String(number_degree) + ");\n";
  return code;
};

Blockly.Python['motor_rotate'] = function(block) {
  var dropdown_motor_name = block.getFieldValue('motor_name');
  var number_degree = Blockly.Python.valueToCode(block, 'degree', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.rotate_motor('" + dropdown_motor_name + "', " + String(number_degree) + ")\n";
  return code;
};

Blockly.JavaScript['motor_control'] = function(block) {
  var dropdown_motor_name = block.getFieldValue('motor_name');
  var number_speed = Blockly.JavaScript.valueToCode(block, 'speed', Blockly.JavaScript.ORDER_ATOMIC);
  var number_duration = Blockly.JavaScript.valueToCode(block, 'duration', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await control_motor('" + dropdown_motor_name + "', " + String(number_speed) + ", " +  String(number_duration) + ");\n";
  return code;
};

Blockly.Python['motor_control'] = function(block) {
  var dropdown_motor_name = block.getFieldValue('motor_name');
  var number_speed = Blockly.Python.valueToCode(block, 'speed', Blockly.Python.ORDER_ATOMIC);
  var number_duration = Blockly.Python.valueToCode(block, 'duration', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.control_motor('" + dropdown_motor_name + "', " + String(number_speed) + ", " +  String(number_duration) + ")\n";
  return code;
};

Blockly.JavaScript['motor_speed_block'] = function(block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await control_motor_speed_group([\n";
  motor_control_idx = statements_statements.indexOf("control_motor", 0);
  var being_idx = motor_control_idx + 13;
  //console.log(statements_statements);
  while (motor_control_idx != -1){
    motor_name_begin_idx = statements_statements.indexOf("('", motor_control_idx) + 2
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = "{'motor_name': '" + motor_name + "', 'speed': " + speed + ", 'duration': " + duration + "}"
    code = code + code_line;

    motor_control_idx = statements_statements.indexOf("control_motor", being_idx);
    if (motor_control_idx != -1) {
      code = code + ",\n";
    }
    being_idx = motor_control_idx + 13;
  }
  code = code + "\n]);"
  return code;
};

Blockly.Python['motor_speed_block'] = function(block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.control_motor_speed_group(" + "'{" + '"operation_list" :[';
  motor_control_idx = statements_statements.indexOf("control_motor", 0);
  var being_idx = motor_control_idx + 13;
  //console.log(statements_statements);
  while (motor_control_idx != -1){
    motor_name_begin_idx = statements_statements.indexOf("('", motor_control_idx) + 2
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = '{"motor_name": "' + motor_name + '", "speed": ' + speed + ', "duration": ' + duration + "}"
    code = code + code_line;

    motor_control_idx = statements_statements.indexOf("control_motor", being_idx);
    if (motor_control_idx != -1) {
      code = code + ",";
    }
    being_idx = motor_control_idx + 13;
  }
  code = code + "]}')\n"
  return code;
};

Blockly.JavaScript['motor_degree_block'] = function(block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await control_motor_degree_group([\n";
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  var being_idx = motor_rotate_idx + 12;
  //console.log(statements_statements);
  while (motor_rotate_idx != -1){
    motor_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(");", angle_begin_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);

    code_line = "{'motor_name': '" + motor_name + "', 'angle': " + angle + "}"
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",\n";
    }
    being_idx = motor_rotate_idx + 13;
  }
  code = code + "\n]);"
  return code;
}

Blockly.Python['motor_degree_block'] = function(block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.control_motor_degree_group([\n";
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  var being_idx = motor_rotate_idx + 12;
  //console.log(statements_statements);
  while (motor_rotate_idx != -1){
    motor_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(");", angle_begin_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);

    code_line = "{'motor_name': '" + motor_name + "', 'angle': " + angle + "}"
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",\n";
    }
    being_idx = motor_rotate_idx + 13;
  }
  code = code + "\n])\n"
  return code;
}

Blockly.JavaScript['move'] = function(block) {
  var value_motors = Blockly.JavaScript.valueToCode(block, 'motors', Blockly.JavaScript.ORDER_ATOMIC);
  var dropdown_direction = block.getFieldValue('direction');
  var code = "await move(" + value_motors + ", '" + dropdown_direction + "');\n";
  return code;
};

Blockly.Python['move'] = function(block) {
  var value_motors = Blockly.Python.valueToCode(block, 'motors', Blockly.Python.ORDER_ATOMIC);
  var dropdown_direction = block.getFieldValue('direction');
  var code = "move(" + value_motors + ", '" + dropdown_direction + "')\n";
  return code;
};

Blockly.JavaScript['turn'] = function(block) {
  var value_motors = Blockly.JavaScript.valueToCode(block, 'motors', Blockly.JavaScript.ORDER_ATOMIC);
  var number_degree = block.getFieldValue('degree');
  var code = "await rotate(" + value_motors + ", " + number_degree + ");\n";
  return code;
};

Blockly.Python['turn'] = function(block) {
  var value_motors = Blockly.Python.valueToCode(block, 'motors', Blockly.Python.ORDER_ATOMIC);
  var number_degree = block.getFieldValue('degree');
  var code = "turn(" + value_motors + ", " + number_degree + ")\n";
  return code;
};

Blockly.JavaScript['lights'] = function(block) {
  var dropdown_light = block.getFieldValue('light');
  var dropdown_operation = block.getFieldValue('operation');
  var text_parameter = block.getFieldValue('parameter');
  if (text_parameter != null) {
    var code = "control_light('" + dropdown_light + "', '" + dropdown_operation + "', '" + text_parameter + "');\n";
  }
  else{
    var code = "control_light('" + dropdown_light + "', '" + dropdown_operation + "', 'none');\n";
  }
  return code;
};

Blockly.Python['lights'] = function(block) {
  var dropdown_light = block.getFieldValue('light');
  var dropdown_operation = block.getFieldValue('operation');
  var text_parameter = block.getFieldValue('parameter');
  if (text_parameter != null) {
    var code = "cait.essentials.control_light('light." + dropdown_light + "', '" + dropdown_operation + "', '" + text_parameter + "')\n";
  }
  else{
    var code = "cait.essentials.control_light('light." + dropdown_light + "', '" + dropdown_operation + "')\n";
  }
  return code;
};

Blockly.JavaScript['media_player'] = function(block) {
  var dropdown_media_player = block.getFieldValue('media_player');
  var dropdown_operation = block.getFieldValue('operation');
  var code = "control_media_player('" + dropdown_media_player + "', '" + dropdown_operation + "');\n";
  return code;
};

Blockly.Python['media_player'] = function(block) {
  var dropdown_media_player = block.getFieldValue('media_player');
  var dropdown_operation = block.getFieldValue('operation');
  var code = "cait.essentials.control_media_player('media_player." + dropdown_media_player + "', '" + dropdown_operation + "')\n";
  return code;
};