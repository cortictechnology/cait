# CAIT Visual Programming Guide

CAIT's visual programming interface extends from Google's Blockly visual code editor.  Google provides a great [user's guide](https://developers.google.com/blockly/guides/overview) to Blockly.  We will not cover these basic concepts here.  Instead, we will talk the basic constructs that every program written for CAIT shares and describe the different A.I. blocks that you can use in your own project.

The main design goal of CAIT is to be intuitive and any program written for it should closely resemble simple structured programming.  For this reason, every program needs to have a least two blocks: a "setup" block and a "main" block.  The "setup" block can only contain initialization blocks for various A.I. modules, while the "main" block implements the program's logic flow.  We employ a sequential programming model in CAIT.  When a program executes, each of our A.I. block performs a specific task and waits for result to return before moving on to the next block.  The complexity of event handling and callbacks are effectively hidden within each block to offer users with an intuitive way to express their logic.

CAIT also offers a conversion tool to convert the visual code into either Jupyter notebook format or straight Python code.  The following describes the function of each custom block in CAIT.  These blocks have a one to one correspondence with the converted Python code statements.  

## Basic Blocks

<img src="../images/setup.png" width="20%">	

**Description:** This block performs initialization of A.I. components.  Every program needs to have a "setup" block.  It corresponds to the "setup" function in the converted Python code.  
**Usage:** This block is usually placed above the "main" block.  
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

