""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, Nov 2020

"""

import tvm
from tvm.contrib import graph_runtime
import numpy as np
from PIL import Image
import time
from scipy.special import expit, logit
import cv2
from skimage import transform as trans
from picamera.array import PiRGBArray
from picamera import PiCamera
import math
import os
import logging

from utils import object_labels, image_labels

logging.getLogger().setLevel(logging.INFO)

class ImageLib:

    def __init__(self):
        self.ctx = tvm.cpu()
        
        loaded_json = open("/vision_module/tuned32_efficientnet_lite.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned32_efficientnet_lite_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned32_efficientnet_lite_param.params", "rb").read())
        self.image_classify_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.image_classify_module.load_params(loaded_params)


    def classify_image(self, _img, threshold):
        dim = (224, 224)
        img = np.copy(_img)

        img = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = img.astype("float32")
        image = cv2.normalize(image, None, -0.992188, 1, cv2.NORM_MINMAX)
        image = image[np.newaxis, :]
        self.image_classify_module.run(images=image)
        softmax_tensor = self.image_classify_module.get_output(0).asnumpy().squeeze()

        top5 = (-softmax_tensor).argsort()[:5]

        classified_results = []
        for idx in top5:
            label = image_labels[idx]
            probability = softmax_tensor[idx]
            if label.find(",") != -1:
                label = label[0:label.find(",")]
            classified_results.append([label, probability])

        return classified_results