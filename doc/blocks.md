# CAIT Block Description

## Program Structure Blocks

<img src="../images/setup.png" width="20%">	

**Description:** Perform setup steps, all initialize blocks goes within this block.   
**Usage:** Must be placed above a main block.  
* * *

<img src="../images/main.png" width="20%">	

**Description:** Main event loop. All program logic goes within this block.  
**Usage:** Must be placed after a setup block.  
* * *

<img src="../images/init_vision.png" width="20%">	

**Description:** Initialize the vision module, must call before using any other vision blocks.  
**Usage:** Can only be use in a setup block.  
**Example:**   
<img src="../images/init_vision_example.png" width="20%">	
* * *

