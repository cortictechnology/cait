""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from image_classify import ImageLib
import logging
import time
import cv2
import io
from PIL import Image
import json
import ast

init_time = time.time()
frame_counter = 0
fps = 0

logging.getLogger().setLevel(logging.INFO)

class ImageClassification:

    def __init__(self, inferenceProcessor="local"):
        self.image_lib = ImageLib()


    def run(self, image, threshold):
        top5_results = self.image_lib.classify_image(image, threshold)
        #logging.info(str(top5_results))
        result = '{ "mode" : "ImageClassification", "names": "' + str(top5_results) + '" }'
        return result