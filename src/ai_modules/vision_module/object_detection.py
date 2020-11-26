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

class ObjectLib:
    
    def __init__(self):
        self.ctx = tvm.cpu()
        loaded_json = open("/vision_module/tuned32_ssdlite.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned32_ssdlite_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned32_ssdlite_param.params", "rb").read())
        self.ssdlite_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.ssdlite_module.load_params(loaded_params)

        self.anchors = np.load("/vision_module/obj_anchors.npy")


    def decode_boxes(self, raw_boxes, anchors):
        """Converts the predictions into actual coordinates using
        the anchor boxes. Processes the entire batch at once.
        """
        boxes = np.zeros(raw_boxes.shape)

        x_center = raw_boxes[..., 1] / 10.0 * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 0] / 10.0 * anchors[:, 3] + anchors[:, 1]

        w = np.exp(raw_boxes[..., 3] / 5.0) * anchors[:, 2]
        h = np.exp(raw_boxes[..., 2] / 5.0) * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        return boxes


    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        assert raw_box_tensor.ndim == 3
        assert raw_box_tensor.shape[1] == 2034
        assert raw_box_tensor.shape[2] == 4

        assert raw_score_tensor.ndim == 3
        assert raw_score_tensor.shape[1] == 2034
        assert raw_score_tensor.shape[2] == 91

        assert raw_box_tensor.shape[0] == raw_score_tensor.shape[0]
        
        detection_boxes = self.decode_boxes(raw_box_tensor, anchors)

        detection_scores_exp = expit(raw_score_tensor)

        detection_classes = detection_scores_exp.argmax(axis=2)

        detection_scores = np.amax(detection_scores_exp, axis=2)

        mask = detection_scores >= 0.5

        output_detections = []
        for i in range(raw_box_tensor.shape[0]):
            boxes = detection_boxes[i, mask[i]]
            classes = detection_classes[i, mask[i]][:, np.newaxis]
            scores = detection_scores[i, mask[i]][:, np.newaxis]
            output_detections.append(np.concatenate((boxes, classes, scores), axis=1))

        return output_detections


    def intersect(self, box_a, box_b):
        """ We resize both tensors to [A,B,2] without new malloc:
        [A,2] -> [A,1,2] -> [A,B,2]
        [B,2] -> [1,B,2] -> [A,B,2]
        Then we compute the area of intersect between box_a and box_b.
        Args:
        box_a: (tensor) bounding boxes, Shape: [A,4].
        box_b: (tensor) bounding boxes, Shape: [B,4].
        Return:
        (tensor) intersection area, Shape: [A,B].
        """
        A = box_a.shape[0]
        B = box_b.shape[0]
        max_xy = np.minimum(np.broadcast_to(box_a[:, 2:][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, 2:][np.newaxis, :], ((A, B, 2))))
        min_xy = np.maximum(np.broadcast_to(box_a[:, :2][:, np.newaxis, :], (A, B, 2)),
                        np.broadcast_to(box_b[:, :2][np.newaxis, :], ((A, B, 2))))
        inter = np.clip((max_xy - min_xy), 0, None)
        return inter[:, :, 0] * inter[:, :, 1]


    def jaccard(self, box_a, box_b):
        """Compute the jaccard overlap of two sets of boxes.  The jaccard overlap
        is simply the intersection over union of two boxes.  Here we operate on
        ground truth boxes and default boxes.
        E.g.:
            A ∩ B / A ∪ B = A ∩ B / (area(A) + area(B) - A ∩ B)
        Args:
            box_a: (tensor) Ground truth bounding boxes, Shape: [num_objects,4]
            box_b: (tensor) Prior boxes from priorbox layers, Shape: [num_priors,4]
        Return:
            jaccard overlap: (tensor) Shape: [box_a.size(0), box_b.size(0)]
        """

        inter = self.intersect(box_a, box_b)
        area_a = np.broadcast_to(((box_a[:, 2]-box_a[:, 0]) *
                (box_a[:, 3]-box_a[:, 1]))[:, np.newaxis], inter.shape)  # [A,B]
        area_b = np.broadcast_to(((box_b[:, 2]-box_b[:, 0]) *
                (box_b[:, 3]-box_b[:, 1]))[np.newaxis, :], inter.shape)  # [A,B]
        union = area_a + area_b - inter
        return inter / union  # [A,B]


    def overlap_similarity(self, box, other_boxes):
        """Computes the IOU between a bounding box and set of other boxes."""
        return self.jaccard(box[np.newaxis, :], other_boxes).squeeze(axis=0)

    
    def weighted_non_max_suppression(self, detections):
        if len(detections) == 0: return []

        all_detections = {}
        
        filtered_detections = []

        for det in detections:
            if det[4] not in all_detections:
                all_detections[det[4]] = np.array([det])
            else:
                all_detections[det[4]] = np.vstack((all_detections[det[4]], np.array(det)))

        for class_id in all_detections:
            dets = all_detections[class_id]
            remaining = np.argsort(-dets[:, 5])
            while len(remaining) > 0:
                det = dets[remaining[0]]
                first_box = det[:4]
                other_boxes = dets[remaining, :4]
                ious = self.overlap_similarity(first_box, other_boxes)
                mask = ious > 0.4
                overlapping = remaining[mask]
                remaining = remaining[~mask]
                weighted_detection = np.copy(det)
                if len(overlapping) > 1:
                    coordinates = dets[overlapping, :4]
                    scores = dets[overlapping, 5:6]
                    total_score = scores.sum()
                    weighted = (coordinates * scores).sum(axis=0) / total_score
                    weighted_detection[:4] = weighted
                    weighted_detection[5] = total_score / len(overlapping)
                filtered_detections.append(weighted_detection)

        return filtered_detections


    def detect_objects(self, _img):
        #t1 = time.time()
        dim = (320, 320)
        resize_ratio_width = _img.shape[1] / 320.0
        resize_ratio_height = _img.shape[0] / 320.0

        img = np.copy(_img)

        img = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = img.astype("float32")
        #image = image / 127.5 - 1.0
        image = cv2.normalize(image, None, -1, 1, cv2.NORM_MINMAX)
        image = image[np.newaxis, :]
        #print("Preprocessing time:", time.time()-t1)
        #t1 = time.time()
        self.ssdlite_module.run(normalized_input_image_tensor=image)
        raw_box_tensor = self.ssdlite_module.get_output(0).asnumpy()
        raw_score_tensor = self.ssdlite_module.get_output(1).asnumpy()
        #print("Inference time:", time.time()-t1)
        #t1 = time.time()
        detections = self.tensors_to_detections(raw_box_tensor, raw_score_tensor, self.anchors)[0]
        filtered_detections = []
        objects = self.weighted_non_max_suppression(detections)
        for obj in objects:
            current_obj = {}
            ymin = int((obj[0] * 320) * resize_ratio_height)
            xmin = int((obj[1] * 320 ) * resize_ratio_width)
            ymax = int((obj[2] * 320) * resize_ratio_height)
            xmax = int((obj[3] * 320) * resize_ratio_width)
            current_obj['x0'] = xmin
            current_obj['y0'] = ymin
            current_obj['x1'] = xmax
            current_obj['y1'] = ymax
            current_obj['prob'] = obj[5]
            current_obj['name'] = object_labels[int(obj[4])]
            filtered_detections.append(current_obj)
        return filtered_detections

