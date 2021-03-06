/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, December 2019
  
 */

var vision_func = ["detect_face", "recognize_face", "add_person", "delete_person", "detect_objects", "classify_image"];
var speech_func = ["listen", "say"];
var nlp_func = ["analyze"];
var control_func = ["rotate_motor", "control_motor", "control_motor_speed_group", "control_motor_degree_group", "move", "rotate"];
var smart_home_func = ["control_light", "control_media_player"]

Blockly.defineBlocksWithJsonArray([
    {
      "type": "setup_block",
      "message0": "%{BKY_SETUP}",
      "message1": "%1",
      "args1": [
        {
          "type": "input_statement",
          "name": "init_blocks"
        }
      ],
      "colour" : "#1d8cf7",
      "tooltip": "%{BKY_SETUP_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "main_block",
      "message0": "%{BKY_MAIN}",
      "message1": "%1",
      "args1": [
        {
          "type": "input_statement",
          "name": "main_blocks"
        }
      ],
      "colour" : "#1d8cf7",
      "tooltip": "%{BKY_MAIN_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "set_parameter",
      "message0": "%{BKY_SET_PARAMS}",
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
      "tooltip": "%{BKY_SET_PARAMS_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "sleep",
      "message0": "%{BKY_SLEEP}",
      "args0": [
        {
          "type": "input_dummy",
          "align": "CENTRE"
        },
        {
          "type": "input_value",
          "name": "time"
        }
      ],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#1d8cf7",
      "tooltip": "%{BKY_SLEEP_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "init_vision",
      "message0": "%{BKY_INIT_VISION}",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#5D0095",
      "tooltip": "%{BKY_INIT_VISION_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "init_voice",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_INIT_VOICE}",
      "args0": [
        {
          "type": "input_dummy",
          "name": "voice_mode",
          "align": "CENTRE"
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
        },
        {
          "type": "field_dropdown",
          "name": "language",
          "options": [
            [
              "English",
              "english"
            ],
            [
              "Française",
              "french"
            ],
            [
              "普通话",
              "chinese"
            ]
          ]
        }
        
      ],
      "extensions": ["dynamic_voice_mode_extension", "dynamic_cloud_accounts_extension"],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#019191",
      "tooltip": "%{BKY_INIT_VOICE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "init_nlp",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_INIT_NLP}",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "model_list",
          "align": "CENTRE"
        },
      ],
      "extensions": ["dynamic_model_list_extension"],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#3ACFF7",
      "tooltip": "%{BKY_INIT_NLP_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "init_control",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_INIT_CONTROL}",
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
      "tooltip": "%{BKY_INIT_CONTROL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "add_control_hub",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_ADD_CONTROL_HUB}",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "control_hubs",
          "align": "CENTRE"
        }
      ],
      "extensions": ["dynamic_control_hubs_extension"],
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "%{BKY_ADD_CONTROL_HUB_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "init_smarthome",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_INIT_HOME}",
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F70090",
      "tooltip": "%{BKY_INIT_HOME_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_detect_face",
      "message0": "%{BKY_FACE_DETECT}",
      "inputsInline": true,
      "output": "String",
      "colour": "#5D0095",
      "tooltip": "%{BKY_FACE_DETECT_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_recognize_face",
      "message0": "%{BKY_FACE_RECOGNIZE}",
      "inputsInline": true,
      "output": "String",
      "colour": "#5D0095",
      "tooltip": "%{BKY_FACE_RECOGNIZE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_add_person",
      "message0": "%{BKY_FACE_ADD}",
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
      "tooltip": "%{BKY_FACE_ADD_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_remove_person",
      "message0": "%{BKY_FACE_DELETE}",
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
      "tooltip": "%{BKY_FACE_DELETE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_detect_objects",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_OBJECT_DETECT}",
      "inputsInline": true,
      "output": null,
      "colour": "#5D0095",
      "tooltip": "%{BKY_OBJECT_DETECT_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "vision_classify_image",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_IMAGE_CLASSIFY}",
      "inputsInline": true,
      "output": null,
      "colour": "#5D0095",
      "tooltip": "%{BKY_IMAGE_CLASSIFY_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "listen",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_LISTEN}",
      "output": null,
      "colour": "#019191",
      "tooltip": "%{BKY_LISTEN_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "say",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_SAY}",
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
      "tooltip": "%{BKY_SAY_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "analyze",
      "message0": "%{BKY_ANALYZE}",
      "args0": [
        {
          "type": "input_value",
          "name": "text",
          "align": "CENTRE"
        }
      ],
      "output": null,
      "colour": "#3ACFF7",
      "tooltip": "%{BKY_ANALYZE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "get_name",
      "message0": "%{BKY_GET_NAME}",
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
      "tooltip": "%{BKY_GET_NAME_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "comment",
      "message0": "%{BKY_COMMENT}",
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
      "tooltip": "%{BKY_COMMENT_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "create_empty_dictionary",
      "message0": "%{BKY_EMPTY_DICT}",
      "inputsInline": true,
      "output": null,
      "colour": "#001F4E",
      "tooltip": "%{BKY_EMPTY_DICT_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "dictionary_keys",
      "message0": "%{BKY_DICT_KEYS}",
      "args0": [
        {
          "type": "input_value",
          "name": "dictionary"
        }
      ],
      "inputsInline": true,
      "output": null,
      "colour": "#001F4E",
      "tooltip": "%{BKY_DICT_KEYS_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "dictionary_value",
      "message0": "%{BKY_DICT_VAL}",
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
      "tooltip": "%{BKY_DICT_VAL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "dictionary_value_set",
      "message0": "%{BKY_DICT_SET_VAL}",
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
      "tooltip": "%{BKY_DICT_SET_VAL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "dictionary_remove",
      "message0": "%{BKY_DICT_REMOVE_VAL}",
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
      "tooltip": "%{BKY_DICT_REMOVE_VAL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "dictionary_add",
      "message0": "%{BKY_DICT_ADD_VAL}",
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
      "tooltip": "%{BKY_DICT_ADD_VAL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "motor_control_block",
      "message0": "%{BKY_SET_MOTOR_GROUP}",
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
      "tooltip": "%{BKY_SET_MOTOR_GROUP_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "ev3_motor_block",
      "message0": "%{BKY_EV3_MOTOR}",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "motor_name",
          "options": [
            [
              "A",
              "ev3_motor_A"
            ],
            [
              "B",
              "ev3_motor_B"
            ],
            [
              "C",
              "ev3_motor_C"
            ],
            [
              "D",
              "ev3_motor_D"
            ]
          ]
        }
      ],
      "output": "String",
      "colour": "#F78C00",
      "tooltip": "%{BKY_EV3_MOTOR_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "robot_inventor_motor_block",
      "message0": "%{BKY_RI_MOTOR}",
      "args0": [
        {
          "type": "field_dropdown",
          "name": "motor_name",
          "options": [
            [
              "A",
              "ri_motor_A"
            ],
            [
              "B",
              "ri_motor_B"
            ],
            [
              "C",
              "ri_motor_C"
            ],
            [
              "D",
              "ri_motor_D"
            ],
            [
              "E",
              "ri_motor_E"
            ],
            [
              "F",
              "ri_motor_F"
            ]
          ]
        }
      ],
      "output": "String",
      "colour": "#F78C00",
      "tooltip": "%{BKY_RI_MOTOR_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "motor_control",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_SET_MOTOR_SPEED}",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "added_hubs",
          "align": "CENTRE"
        },
        {
          "type": "input_value",
          "name": "motor",
          "check": "String"
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
      "extensions": ["dynamic_added_hubs_extension"],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "%{BKY_SET_MOTOR_SPEED_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "motor_position",
      "message0": "%{BKY_SET_MOTOR_ANGLE}",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "added_hubs",
          "align": "CENTRE"
        },
        {
          "type": "input_value",
          "name": "motor",
          "check": "String"
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
      "extensions": ["dynamic_added_hubs_extension"],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "%{BKY_SET_MOTOR_ANGLE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "motor_rotate",
      "message0": "%{BKY_SET_MOTOR_ROTATE}",
      "args0": [
        {
          "type": "input_dummy",
          "name" : "added_hubs",
          "align": "CENTRE"
        },
        {
          "type": "input_value",
          "name": "motor",
          "check": "String"
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
      "extensions": ["dynamic_added_hubs_extension"],
      "inputsInline": true,
      "previousStatement": null,
      "nextStatement": null,
      "colour": "#F78C00",
      "tooltip": "%{BKY_SET_MOTOR_ROTATE_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "lights",
      "message0": "%{BKY_LIGHT_CONTROL}",
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
      "tooltip": "%{BKY_LIGHT_CONTROL_TOOLTIP}",
      "helpUrl": ""
    },
    {
      "type": "media_player",
      "lastDummyAlign0": "CENTRE",
      "message0": "%{BKY_MEDIA_CONTROL}",
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
      "tooltip": "%{BKY_MEDIA_CONTROL_TOOLTIP}",
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

Blockly.Extensions.register("dynamic_voice_mode_extension",
function() {
  this.getInput('voice_mode')
    .appendField(new Blockly.FieldDropdown(
      function() {
        var options = [];
        if (voice_mode.length > 0) {
          for (i in voice_mode) {
            options.push([voice_mode[i], voice_mode[i]])
          }
        }
        else {
          options.push(['none', 'none']);
        }
        return options;
      }), 'mode');
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
  if (cloud_accounts.length < 1 || this.getInput('voice_mode').fieldRow[1].value_ == "on device") {
    this.getInput("cloud_accounts").setVisible(false);
    this.getInput("ending").setVisible(false);
    this.getField("language").setVisible(false);
  }

  
});

Blockly.Extensions.register('dynamic_model_list_extension',
function() {
  this.getInput('model_list')
    .appendField(new Blockly.FieldDropdown(
      function() {
        var options = [];
        if (nlp_models.length > 0) {
          for (i in nlp_models) {
            options.push([nlp_models[i], nlp_models[i]])
          }
        }
        else {
          options.push(['none', 'none']);
        }
        return options;
      }), 'models');
});


Blockly.Extensions.register('dynamic_control_hubs_extension',
  function() {
    this.getInput('control_hubs')
      .appendField(new Blockly.FieldDropdown(
        function() {
          var options = [];
          if (control_hubs.length > 0) {
            for (i in control_hubs) {
              options.push([control_hubs[i], control_hubs[i]])
            }
          }
          else {
            options.push(['none', 'none']);
          }
          return options;
        }), 'hubs');
  });

Blockly.Extensions.register('dynamic_added_hubs_extension',
function() {
  this.getInput('added_hubs')
    .appendField(new Blockly.FieldDropdown(
      function() {
        var options = [];
        if (added_hubs.length > 0) {
          for (i in added_hubs) {
            options.push([added_hubs[i], added_hubs[i]])
          }
        }
        else {
          options.push(['none', 'none']);
        }
        return options;
      }), 'available_hubs');
});

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
  var code = "import cait.essentials\n" + "def setup():\n" + statements_main;
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
  var code = "def main():\n" + statements_main;
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

Blockly.JavaScript['sleep'] = function(block) {
  var time_value = Blockly.JavaScript.valueToCode(block, 'time', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await cait_sleep(" + time_value +  ");\n";
  return code;
};

Blockly.Python['sleep'] = function(block) {
  var time_value = Blockly.Python.valueToCode(block, 'time', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.sleep(" + time_value + ")\n";
  return code;
};

Blockly.JavaScript['init_vision'] = function(block) {
  var code = "await init_vision();\n";
  return code;
};

Blockly.Python['init_vision'] = function(block) {
  var code = "cait.essentials.initialize_component('vision', processor='local')\n";
  return code;
};

Blockly.JavaScript['init_voice'] = function(block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  var dropdown_langauage = block.getFieldValue('language');
  var code = "await init_voice('" + dropdown_mode + "', '" + dropdown_account + "', '" + dropdown_langauage + "');\n";
  return code;
};

Blockly.Python['init_voice'] = function(block) {
  var dropdown_mode = block.getFieldValue('mode');
  var dropdown_account = block.getFieldValue('accounts');
  var dropdown_langauage = block.getFieldValue('language');
  if (dropdown_mode == "online"){
    var code = "cait.essentials.initialize_component('voice', mode='online', account='" + dropdown_account + "', language='" + dropdown_langauage + "')\n";
  }
  else {
    var code = "cait.essentials.initialize_component('voice', mode='on_devie')\n";
  }
  return code;
};

Blockly.JavaScript['init_nlp'] = function(block) {
  var dropdown_models = block.getFieldValue('models');
  var code = "await init_nlp('" + dropdown_models + "');\n";
  return code;
};

Blockly.Python['init_nlp'] = function(block) {
  var dropdown_models = block.getFieldValue('models');
  var code = "cait.essentials.initialize_component('nlp', '" + dropdown_models + "')\n";
  return code;
};

Blockly.JavaScript['init_control'] = function(block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await init_control([";
  hub_name_idx = statements_statements.indexOf("<", 0);
  var being_idx = hub_name_idx + 1;
  while (hub_name_idx != -1) {
    var end_idx = statements_statements.indexOf(">", being_idx);
    var hub_name = statements_statements.substring(being_idx, end_idx);
    code = code + "'" +  hub_name + "'";
    hub_name_idx = statements_statements.indexOf("<", being_idx);
    being_idx = hub_name_idx + 1;
    if (hub_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "]);\n";
  return code;
};

Blockly.Python['init_control'] = function(block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.initialize_component('control', [";
  hub_name_idx = statements_statements.indexOf("(", 0);
  var being_idx = hub_name_idx + 1;
  while (hub_name_idx != -1) {
    var end_idx = statements_statements.indexOf(")", being_idx);
    var hub_name = statements_statements.substring(being_idx, end_idx);
    code = code + "'" +  hub_name + "'";
    hub_name_idx = statements_statements.indexOf("(", being_idx);
    being_idx = hub_name_idx + 1;
    if (hub_name_idx != -1) {
      code = code + ",";
    }
  }
  code = code + "])\n";
  return code;
};

Blockly.JavaScript['add_control_hub'] = function(block) {
  var dropdown_hub = block.getFieldValue('hubs');
  if (dropdown_hub == "none"){
    throw new Error("The selected hub: " + dropdown_hub + " is not valid, please make sure to select an available hub.");
  }
  var code = "<" + dropdown_hub + ">";
  return code;
};

Blockly.Python['add_control_hub'] = function(block) {
  var dropdown_hub = block.getFieldValue('hubs');
  var code = "(" + dropdown_hub + ")";
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

Blockly.JavaScript['vision_detect_face'] = function(block) {
  var code = "await detect_face()";
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_detect_face'] = function(block) {
  var code = "cait.essentials.detect_face()";
  return [code, Blockly.Python.ORDER_NONE];
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

Blockly.JavaScript['vision_classify_image'] = function(block) {
  var code = 'await classify_image()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['vision_classify_image'] = function(block) {
  var code = 'cait.essentials.classify_image()';
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

Blockly.JavaScript['ev3_motor_block'] = function(block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.JavaScript.ORDER_NONE];
}

Blockly.Python['ev3_motor_block'] = function(block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.Python.ORDER_NONE];
}

Blockly.JavaScript['robot_inventor_motor_block'] = function(block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.JavaScript.ORDER_NONE];
}

Blockly.Python['robot_inventor_motor_block'] = function(block) {
  var motor_name = block.getFieldValue('motor_name');
  return [motor_name, Blockly.Python.ORDER_NONE];
}

Blockly.JavaScript['motor_position'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1){
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_degree = Blockly.JavaScript.valueToCode(block, 'degree', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await set_motor_position('" + hub_name + "', '"  + motor_name + "', " + String(number_degree) + ");\n";
  return code;
};

Blockly.Python['motor_position'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_degree = Blockly.Python.valueToCode(block, 'degree', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.set_motor_position('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ")\n";
  return code;
};

Blockly.JavaScript['motor_rotate'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1){
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_degree = Blockly.JavaScript.valueToCode(block, 'degree', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await rotate_motor('" + hub_name + "', '"  + motor_name + "', " + String(number_degree) + ");\n";
  return code;
};

Blockly.Python['motor_rotate'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_degree = Blockly.Python.valueToCode(block, 'degree', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.rotate_motor('" + hub_name + "', '" + motor_name + "', " + String(number_degree) + ")\n";
  return code;
};

Blockly.JavaScript['motor_control'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var index = added_hubs.indexOf(hub_name);
  if (index == -1){
    throw new Error("The selected hub: " + hub_name + " is not available, please make sure the selection is valid");
  }
  var motor_name = Blockly.JavaScript.valueToCode(block, 'motor', Blockly.JavaScript.ORDER_ATOMIC);
  if (hub_name.indexOf("EV3") != -1) {
    if (motor_name.indexOf("ev3") == -1) {
      throw new Error("EV3 Hub must use EV3 motors only");
    }
  } else if (hub_name.indexOf("Robot Inventor") != -1) {
    if (motor_name.indexOf("ri") == -1) {
      throw new Error("Robot Inventor Hub must use Robot Inventor motors only");
    }
  }
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_speed = Blockly.JavaScript.valueToCode(block, 'speed', Blockly.JavaScript.ORDER_ATOMIC);
  var number_duration = Blockly.JavaScript.valueToCode(block, 'duration', Blockly.JavaScript.ORDER_ATOMIC);
  var code = "await control_motor('" + hub_name + "', '" + motor_name + "', " + String(number_speed) + ", " +  String(number_duration) + ");\n";
  return code;
};

Blockly.Python['motor_control'] = function(block) {
  var hub_name = block.getFieldValue('available_hubs');
  var motor_name = Blockly.Python.valueToCode(block, 'motor', Blockly.Python.ORDER_ATOMIC);
  motor_name = motor_name.substring(motor_name.indexOf("_") + 1,motor_name.length-1)
  var number_speed = Blockly.Python.valueToCode(block, 'speed', Blockly.Python.ORDER_ATOMIC);
  var number_duration = Blockly.Python.valueToCode(block, 'duration', Blockly.Python.ORDER_ATOMIC);
  var code = "cait.essentials.control_motor('" + hub_name + "', '" + motor_name + "', " + String(number_speed) + ", " +  String(number_duration) + ")\n";
  return code;
};

Blockly.JavaScript['motor_control_block'] = function(block) {
  var statements_statements = Blockly.JavaScript.statementToCode(block, 'statements');
  var code = "await control_motor_group([\n";
  motor_speed_idx = statements_statements.indexOf("control_motor", 0);
  init_speed_idx = motor_speed_idx;
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  var speed_being_idx = motor_speed_idx + 13;
  var degree_being_idx = motor_rotate_idx + 12;
  //console.log(statements_statements);
  while (motor_speed_idx != -1){
    hub_name_begin_idx = statements_statements.indexOf("('", speed_being_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = "{'hub_name': '" + hub_name + "', 'motor_name': '" + motor_name + "', 'speed': " + speed + ", 'duration': " + duration + "}"
    code = code + code_line;

    motor_speed_idx = statements_statements.indexOf("control_motor", speed_being_idx);
    if (motor_speed_idx != -1) {
      code = code + ",\n";
    }
    speed_being_idx = motor_speed_idx + 13;
  }
  if (init_speed_idx != -1 && motor_rotate_idx != -1) {
    code = code + ",";
  }
  while (motor_rotate_idx != -1){
    hub_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(");", angle_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);

    code_line = "{'hub_name': '" + hub_name + "', 'motor_name': '" + motor_name + "', 'angle': " + angle + "}"
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", degree_being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",\n";
    }
    degree_being_idx = motor_rotate_idx + 13;
  }

  code = code + "\n]);"
  return code;
};

Blockly.Python['motor_control_block'] = function(block) {
  var statements_statements = Blockly.Python.statementToCode(block, 'statements');
  var code = "cait.essentials.control_motor_group(" + "'{" + '"operation_list" :[';
  motor_speed_idx = statements_statements.indexOf("control_motor", 0);
  init_speed_idx = motor_speed_idx;
  motor_rotate_idx = statements_statements.indexOf("rotate_motor", 0);
  var speed_being_idx = motor_speed_idx + 13;
  var degree_being_idx = motor_rotate_idx + 12;
  while (motor_speed_idx != -1){
    hub_name_begin_idx = statements_statements.indexOf("('", motor_speed_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    speed_begin_idx = motor_name_end_idx + 3;
    speed_end_idx = statements_statements.indexOf(",", speed_begin_idx)
    duration_begin_idx = speed_end_idx + 2;
    duration_end_idx = statements_statements.indexOf(")", duration_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    speed = statements_statements.substring(speed_begin_idx, speed_end_idx);
    speed = speed.replace('(', '')
    speed = speed.replace(')', '')
    duration = statements_statements.substring(duration_begin_idx, duration_end_idx);

    code_line = '{"hub_name": "' + hub_name + '", "motor_name": "' + motor_name + '", "speed": "' + speed + '", "duration": "' + duration + '"}'
    code = code + code_line;

    motor_speed_idx = statements_statements.indexOf("control_motor", speed_being_idx);
    if (motor_speed_idx != -1) {
      code = code + ",";
    }
    speed_being_idx = motor_speed_idx + 13;
  }
  if (init_speed_idx != -1 && motor_rotate_idx != -1) {
    code = code + ",";
  }
  while (motor_rotate_idx != -1){
    hub_name_begin_idx = statements_statements.indexOf("('", motor_rotate_idx) + 2
    hub_name_end_idx = statements_statements.indexOf("', ", hub_name_begin_idx)
    motor_name_begin_idx = statements_statements.indexOf("'", hub_name_end_idx + 1) + 1
    motor_name_end_idx = statements_statements.indexOf("'", motor_name_begin_idx + 1)
    angle_begin_idx = motor_name_end_idx + 3;
    angle_end_idx = statements_statements.indexOf(")", angle_begin_idx);

    hub_name = statements_statements.substring(hub_name_begin_idx, hub_name_end_idx);
    motor_name = statements_statements.substring(motor_name_begin_idx, motor_name_end_idx);
    angle = statements_statements.substring(angle_begin_idx, angle_end_idx);
    angle = angle.replace('(', '')
    angle = angle.replace(')', '')

    
    code_line = '{"hub_name": "' + hub_name + '", "motor_name": "' + motor_name + '", "angle": "' + angle + '"}'
    code = code + code_line;

    motor_rotate_idx = statements_statements.indexOf("rotate_motor", degree_being_idx);
    if (motor_rotate_idx != -1) {
      code = code + ",";
    }
    degree_being_idx = motor_rotate_idx + 13;
  }

  code = code + "]}')\n"
  return code;
};

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
    var code = "await control_light('" + dropdown_light + "', '" + dropdown_operation + "', '" + text_parameter + "');\n";
  }
  else{
    var code = "await control_light('" + dropdown_light + "', '" + dropdown_operation + "', 'none');\n";
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
  var code = "await control_media_player('" + dropdown_media_player + "', '" + dropdown_operation + "');\n";
  return code;
};

Blockly.Python['media_player'] = function(block) {
  var dropdown_media_player = block.getFieldValue('media_player');
  var dropdown_operation = block.getFieldValue('operation');
  var code = "cait.essentials.control_media_player('media_player." + dropdown_media_player + "', '" + dropdown_operation + "')\n";
  return code;
};
