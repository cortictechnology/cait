/* 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, May 2020
  
 */

'use strict';

var localizedStrings={
    login:{
        'en/US':'User Login',
        'chs/CN':'用户登录'
    },
    username:{
        'en/US':'Username',
        'chs/CN':'用户名'
    },
    usernameReq:{
        'en/US':'Username is required',
        'chs/CN':'用户名为必填项'
    },
    pass:{
        'en/US':'Password',
        'chs/CN':'密码'
    },
    passReq:{
        'en/US':'Password is required',
        'chs/CN':'密码是必需的'
    },
    loginBtn:{
        'en/US':'Login',
        'chs/CN':'登录'
    },
    usernameNotExist:{
        'en/US':'Username does not exist!',
        'chs/CN':'用户名不存在！'
    },
    usernameExist:{
        'en/US':'Username already exists!',
        'chs/CN':'此用户名已存在！'
    },
    wrongPass:{
        'en/US':'Wrong password!',
        'chs/CN':'密码错误！'
    },
    usernameOrPassEmpty:{
        'en/US':'Username or password cannot be empty!',
        'chs/CN':'用户名或密码不能为空！'
    },
    initCAIT:{
        'en/US':'Starting CAIT System',
        'chs/CN':'正在启动CAIT系统中'
    },
    createAcc:{
        'en/US':'Create your Account',
        'chs/CN':'创建您的帐户'
    },
    signupTitle:{
        'en/US':'Signup to start using CAIT',
        'chs/CN':'注册以开始使用CAIT'
    },
    register:{
        'en/US':'Register',
        'chs/CN':'注册'
    },
    cancel:{
        'en/US':'Cancel',
        'chs/CN':'取消'
    },
    registerSuccess:{
        'en/US':'Registration succeeded!',
        'chs/CN':'注册成功！'
    },
    vpTitle:{
        'en/US':'CAIT Visual Programming Interface',
        'chs/CN':'CAIT可视化编程界面'
    },
    save:{
        'en/US':'Save',
        'chs/CN':'保存'
    },
    saveName:{
        'en/US':'Filename to save: ',
        'chs/CN':'要保存的文件名： '
    },
    load:{
        'en/US':'Load',
        'chs/CN':'加载'
    },
    loadName:{
        'en/US':'Filename to load: ',
        'chs/CN':'要加载的文件名： '
    },
    run:{
        'en/US':'Run',
        'chs/CN':'运行'
    },
    stop:{
        'en/US':'Stop',
        'chs/CN':'停止'
    },
    genPython:{
        'en/US':'Generate Python Code',
        'chs/CN':'生成Python代码'
    },
    genPyName:{
        'en/US':'Filename to save generated python code: ',
        'chs/CN':'保存生成的python代码的文件名： '
    },
    genPyNB:{
        'en/US':'Generate Jupyter Notebook',
        'chs/CN':'生成Jupyter笔记本'
    },
    genPyNBName:{
        'en/US':'Filename to save generated jupyter notebook: ',
        'chs/CN':'保存生成的jupyter笔记本的文件名：'
    },
    visInit:{
        'en/US':'Initializing vision component...',
        'chs/CN':'初始化视觉组件...'
    },
    voiceInit:{
        'en/US':'Initializing voice component...',
        'chs/CN':'初始化语音组件...'
    },
    nlpInit:{
        'en/US':'Initializing nlp component...',
        'chs/CN':'初始化自然语言处理组件...'
    },
    controlInit:{
        'en/US':'Initializing control component...',
        'chs/CN':'初始化控制组件...'
    },
    sHomeInit:{
        'en/US':'Initializing smart home component...',
        'chs/CN':'初始化智能家居组件...'
    },
    visNotInit:{
        'en/US':'Vision is not initialized. Please initialize it in the setup block first',
        'chs/CN':'视觉未初始化。请首先在设置块中对其进行初始化'
    },
    voiceNotInit:{
        'en/US':'Speech is not initialized. Please initialize it in the setup block first',
        'chs/CN':'语音未初始化。请首先在设置块中对其进行初始化'
    },
    nlpNotInit:{
        'en/US':'NLP is not initialized. Please initialize it in the setup block first',
        'chs/CN':'自然语言处理未初始化。请首先在设置块中对其进行初始化'
    },
    controlNotInit:{
        'en/US':'Control is not initialized. Please initialize it in the setup block first',
        'chs/CN':'控制系统未初始化。请首先在设置块中对其进行初始化'
    },
    sHomeNotInit:{
        'en/US':'Smart Home Control is not initialized. Please initialize it in the setup block first',
        'chs/CN':'智能家居控制未初始化。请首先在设置块中对其进行初始化'
    },
    logout:{
        'en/US':'Logout',
        'chs/CN':'登出'
    },
    setupWelcome:{
        'en/US':'Welcome! This is the first step of customizing your own CAIT.',
        'chs/CN':'欢迎！这是定制自己的CAIT的第一步。'
    },
    eula:{
        'en/US':'End-User License Agreement ("Agreement")',
        'chs/CN':'最终用户许可协议（“协议”）'
    },
    lastUpdate:{
        'en/US':'Last updated: May 22, 2020',
        'chs/CN':'上次更新时间：2020年5月22日'
    },
    agree:{
        'en/US':'  I Agree ',
        'chs/CN':' 我同意 '
    },
    connectWifi:{
        'en/US':"Let's connect to a WiFi network",
        'chs/CN':'让我们连接到WiFi网络'
    },
    selectedWifi:{
        'en/US':"Select WiFi",
        'chs/CN':'选择WiFi'
    },
    availWifi:{
        'en/US':"Available WiFi",
        'chs/CN':'可用的Wifi'
    },
    enterPassword:{
        'en/US':"Enter Password",
        'chs/CN':'输入密码'
    },
    connect:{
        'en/US':"Connect",
        'chs/CN':'连接'
    },
    loadingTextWifi:{
        'en/US':"Testing WiFi Connection",
        'chs/CN':'测试WiFi连接'
    },
    loadingReboot:{
        'en/US':"Cleaning up and rebooting CAIT",
        'chs/CN':'正在重新启动CAIT中'
    },
    doneTextWifi:{
        'en/US':"Please refresh this page in a few minutes",
        'chs/CN':'请在几分钟后刷新此页面'
    },
    wifiSuccess:{
        'en/US':"WiFi Connection successed! CAIT will reboot now. Please switch to your selected Wifi and wait for a few minutes",
        'chs/CN':'WiFi连接成功！ CAIT现在将重新启动。请切换到您选择的Wifi，然后等待几分钟。'
    },
    wifiFailed:{
        'en/US':"Cannot connect to selected WiFi, please refresh this page and try again.",
        'chs/CN':'无法连接到所选的WiFi，请刷新此页面，然后重试。'
    },
    startSetup:{
        'en/US':'Start setup',
        'chs/CN':'开始设定'
    },
    customDevice:{
        'en/US':'Customizing your device',
        'chs/CN':'自定义您的设备'
    },
    nameDevice:{
        'en/US':'How do you want to name your device?',
        'chs/CN':'您想如何命名您的设备？'
    },
    askUsername:{
        'en/US':'What is your username?',
        'chs/CN':'您的用户名是什么？'
    },
    askPassword:{
        'en/US':'Please enter a password for your user',
        'chs/CN':'请输入您的用户密码'
    },
    testHardware:{
        'en/US':'We will now test the connected camera and audio devices',
        'chs/CN':'现在，我们将测试连接的摄像头和音频设备'
    },
    availCam:{
        'en/US':'Available Camera',
        'chs/CN':'可用摄像头'
    },
    availMicrophone:{
        'en/US':'Available Microphone',
        'chs/CN':'可用麦克风'
    },
    testCam:{
        'en/US':'Test Camera',
        'chs/CN':'测试摄像头'
    },
    testSpeaker:{
        'en/US':'Test Speaker',
        'chs/CN':'测试扬声器'
    },
    testMicrophone:{
        'en/US':'Test Microphone',
        'chs/CN':'测试麦克风'
    },
    loadingTextHardware:{
        'en/US':'Initializing Hardware',
        'chs/CN':'初始化硬件'
    },
    thirdSignin:{
        'en/US':"Let's sign in or register to third party cloud service provider, after creating an account, please enter the API key and Secret Key to below, then press the next button",
        'chs/CN':'让我们登录或注册到第三方云服务提供商，创建帐户后，请在下面输入API Key和Secret Key，然后按下一步按钮'
    },
    signinSuccess:{
        'en/US':"Sign in Success! Please press next button to continue.",
        'chs/CN':'登录成功！请按下一步按钮继续。'
    },
    next:{
        'en/US':'Next',
        'chs/CN':'下一步'
    },
    previous:{
        'en/US':'Previous',
        'chs/CN':'上一步'
    },
    skip:{
        'en/US':'Skip',
        'chs/CN':'跳过'
    },
    skipWifi:{
        'en/US':'If you skip setting up the Wifi, you can only connect to CAIT through AP mode',
        'chs/CN':'如果您跳过设置Wifi，则只能通过AP模式连接到CAIT'
    },
    skipDeviceInfo:{
        'en/US':'If you skip setting up account, you will not have a personal account for Visual Programming',
        'chs/CN':'如果您跳过设置帐户，则将没有用于可视化编程的个人帐户'
    },
    skipBaidu:{
        'en/US':'If you skip setting up Baidu account, you will not be able to use any speech services',
        'chs/CN':'如果您跳过设置百度帐户的操作，则将无法使用任何语音服务'
    },
    thirdlogin:{
        'en/US':'Login/Register Baidu Account',
        'chs/CN':'登录/注册百度帐号'
    },
    apiKey:{
        'en/US':'API Key',
        'chs/CN':'API Key'
    },
    secretKey:{
        'en/US':'Secret Key',
        'chs/CN':'Secret Key'
    },
    emptyField:{
        'en/US':"All fields cannot be empty!",
        'chs/CN':'所有字段不能为空！'
    },
    congrats:{
        'en/US':"Congratulation! CAIT is now all setup, click the button below to restart CAIT now",
        'chs/CN':'恭喜你！现在已完成CAIT的所有设置，请单击下面的按钮立即重新启动CAIT'
    },
    reboot:{
        'en/US':"Reboot CAIT",
        'chs/CN':'重新启动CAIT'
    }
}