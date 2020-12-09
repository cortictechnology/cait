cd ../src/
mkdir cait_bin
cd cait_bin
mkdir managers
cd ../cait
python3 compile.py build_ext --inplace
mv *.so ../cait_bin
cp managers/NotoSansCJKtc-Regular.ttf ../cait_bin/managers

rm *.c
rm -rf build
cd managers
rm *.c
cd ../../cait_bin
mv component_manager* device_manager* offloading* managers

cd ..
mkdir ai_modules_bin
cd ai_modules_bin
mkdir control_module
mkdir nlp_module
mkdir vision_module
mkdir voice_module
cd ../ai_modules/vision_module
docker run -it --network host --privileged -v $(pwd):/vision_module --rm cortictech/vision:0.52 python3 /vision_module/compile.py build_ext --build-lib /vision_module
sudo rm *.c
sudo mv *.so ../../ai_modules_bin/vision_module
cp -R * ../../ai_modules_bin/vision_module
rm ../../ai_modules_bin/vision_module/facelib.py
rm ../../ai_modules_bin/vision_module/FaceRecognition.py
rm ../../ai_modules_bin/vision_module/ObjectDetection.py
rm ../../ai_modules_bin/vision_module/object_detection.py
rm ../../ai_modules_bin/vision_module/ImageClassification.py
rm ../../ai_modules_bin/vision_module/image_classify.py
rm ../../ai_modules_bin/vision_module/inference.py
rm ../../ai_modules_bin/vision_module/compile.py
cd ../control_module
docker run -it --network host --privileged -v $(pwd):/control_module --rm cortictech/control:0.52 python3.5 /control_module/compile.py build_ext --build-lib /control_module
sudo rm *.c
sudo mv *.so ../../ai_modules_bin/control_module
cp main.py ../../ai_modules_bin/control_module
cd ../nlp_module
docker run -it --network host --privileged -v $(pwd):/nlp_module --rm cortictech/nlp:0.52 python3 /nlp_module/compile.py build_ext --build-lib /nlp_module
sudo rm *.c
sudo mv *.so ../../ai_modules_bin/nlp_module
cp -R * ../../ai_modules_bin/nlp_module
rm ../../ai_modules_bin/nlp_module/nlu.py
rm ../../ai_modules_bin/nlp_module/compile.py
cd ../voice_module
docker run -it --network host --privileged -v $(pwd):/voice_module --rm cortictech/speech:0.52 python3 /voice_module/compile.py build_ext --build-lib /voice_module
sudo rm *.c
sudo mv *.so ../../ai_modules_bin/voice_module
cp -R * ../../ai_modules_bin/voice_module
rm ../../ai_modules_bin/voice_module/voice.py
rm ../../ai_modules_bin/voice_module/compile.py

cd ../../
cp -R cortic_webapp cortic_webapp_bin
cd cortic_webapp_bin
python3 compile.py build_ext --inplace
rm main.py
rm *.c
rm -rf build
cd static/js
javascript-obfuscator cait_blocks.js --output cait_blocks_obf.js
mv cait_blocks_obf.js cait_blocks.js
javascript-obfuscator cait_functions.js --output cait_functions_obf.js
mv cait_functions_obf.js cait_functions.js
javascript-obfuscator entry_setup.js --output entry_setup_obf.js
mv entry_setup_obf.js entry_setup.js
javascript-obfuscator finish.js --output finish_obf.js
mv finish_obf.js finish.js
javascript-obfuscator main.js --output main_obf.js
mv main_obf.js main.js
javascript-obfuscator setup_device.js --output setup_device_obf.js
mv setup_device_obf.js setup_device.js
javascript-obfuscator setup_wifi.js --output setup_wifi_obf.js
mv setup_wifi_obf.js setup_wifi.js
javascript-obfuscator signup.js --output signup_obf.js
mv signup_obf.js signup.js
javascript-obfuscator test_hardware.js --output test_hardware_obf.js
mv test_hardware_obf.js test_hardware.js
javascript-obfuscator thirdsignin.js --output thirdsignin_obf.js
mv thirdsignin_obf.js thirdsignin.js
javascript-obfuscator workspace_utils.js --output workspace_utils_obf.js
mv workspace_utils_obf.js workspace_utils.js