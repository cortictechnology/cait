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

logging.getLogger().setLevel(logging.INFO)

class ObjectLib:
    
     def __init__(self):
        self.ctx = tvm.cpu()
        loaded_json = open("/vision_module/tuned_ssdlite_graph.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned_ssdlite_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned_ssdlite_param.params", "rb").read())
        self.ssdlite_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.ssdlite_module.load_params(loaded_params)

        self.anchors = np.load("/vision_module/obj_anchors.npy")


    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        assert raw_box_tensor.ndim == 3
        assert raw_box_tensor.shape[1] == 2034
        assert raw_box_tensor.shape[2] == 4

        assert raw_score_tensor.ndim == 3
        assert raw_score_tensor.shape[1] == 2034
        assert raw_score_tensor.shape[2] == 91

        assert raw_box_tensor.shape[0] == raw_score_tensor.shape[0]
        
        detection_boxes = self.decode_boxes(raw_box_tensor, anchors)
        
        thresh = 100.0
        raw_score_tensor = np.clip(raw_score_tensor, -thresh, thresh)
        detection_scores = expit(raw_score_tensor).squeeze(axis=2)
        
        # Note: we stripped off the last dimension from the scores tensor
        # because there is only has one class. Now we can simply use a mask
        # to filter out the boxes with too low confidence.
        mask = detection_scores >= 0.6
        # Because each image from the batch can have a different number of
        # detections, process them one at a time using a loop.
        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]
            scores = detection_scores[i, mask[i]][:, np.newaxis]
            output_detections.append(np.concatenate((boxes, scores), axis=1))

        return output_detections
