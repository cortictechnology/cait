## path_user_say_hi_and_yes_demo_known_name_next_state
* user_give_name
    - action_extract_user_name
    - utter_greet_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_state
    - action_next_demo_state

## path_user_say_hi_and_yes_demo_known_name_next_demo
* user_give_name
    - action_extract_user_name
    - utter_greet_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_demo
    - action_next_demo

## path_user_say_hi_and_yes_demo_known_name_repeat_demo
* user_give_name
    - action_extract_user_name
    - utter_greet_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_repeat_demo
    - action_repeat_demo

## path_user_say_hi_and_yes_demo_valid_name_next_state
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "get"}
    - utter_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_state
    - action_next_demo_state

## path_user_say_hi_and_yes_demo_valid_name_next_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "get"}
    - utter_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_demo
    - action_next_demo

## path_user_say_hi_and_yes_demo_valid_name_repeat_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "get"}
    - utter_user_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_repeat_demo
    - action_repeat_demo

## path_user_say_hi_and_yes_demo_invalid_name_next_state
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "noget"}
    - utter_user_name_unknown
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_state
    - action_next_demo_state

## path_user_say_hi_and_yes_demo_invalid_name_next_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "noget"}
    - utter_user_name_unknown
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_demo
    - action_next_demo

## path_user_say_hi_and_yes_demo_invalid_name_repeat_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "noget"}
    - utter_user_name_unknown
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_repeat_demo
    - action_repeat_demo

## path_user_say_hi_and_yes_demo_refuse_name_next_state
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_not_give_name OR user_say_no
    - utter_dont_record_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_state
    - action_next_demo_state

## path_user_say_hi_and_yes_demo_refuse_name_next_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_not_give_name OR user_say_no
    - utter_dont_record_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_next_demo
    - action_next_demo

## path_user_say_hi_and_yes_demo_refuse_name_repeat_demo
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_not_give_name OR user_say_no
    - utter_dont_record_name
    - utter_say_demo
* user_say_yes
    - action_start_demo
* user_say_repeat_demo
    - action_repeat_demo

## path_user_say_hi_and_no_valid_name
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "get"}
    - utter_user_name
    - utter_say_demo
* user_say_no
    - utter_say_bye
    - action_restart

## path_user_say_hi_and_no_invalid_name
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_give_name
    - action_extract_user_name
    - action_add_user_name
    - slot{"name_input" : "noget"}
    - utter_user_name_unknown
    - utter_say_demo
* user_say_no
    - utter_say_bye
    - action_restart

## path_user_say_hi_and_no_refuse_name
* user_greetings
    - utter_say_hi
    - utter_ask_user_name
* user_not_give_name OR user_say_no
    - utter_dont_record_name
    - utter_say_demo
* user_say_no
    - utter_say_bye
    - action_restart

## path_user_say_hi_and_no_demo_known_name
* user_give_name
    - utter_greet_user_name
    - utter_say_demo
* user_say_no
    - utter_say_bye
    - action_restart
