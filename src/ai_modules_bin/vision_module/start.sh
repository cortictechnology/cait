rmmod uvcvideo
modprobe uvcvideo quirks=128 nodrop=1 timeout=6000
export PYTHONPATH=$PYTHONPATH:~/tvm/python
python3 /vision_module/main.py
