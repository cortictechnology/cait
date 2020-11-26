from objectlib import ObjectLib
#from facelib import FaceLib
import cv2
import time

objlib = ObjectLib()
#fl = FaceLib()
cam = cv2.VideoCapture(0)
cam.set(3,320)
cam.set(4, 240)

for i in range(1000):
    _, img = cam.read()
    #t1 = time.time()
    #result = objlib.detect_objects(img)
    result = objlib.classify_image(img)
    print(result)
    #print("inference time:", time.time() - t1)
#fl.detect_faces(img)