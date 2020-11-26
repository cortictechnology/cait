""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

"""

from facelib import FaceLib
import cv2
import numpy as np
import io
import shutil
from PIL import Image
import json
import logging

logging.getLogger().setLevel(logging.INFO)

class FaceRecognition:
    def __init__(self, inferenceProcessor="local"):
        self.face_lib = FaceLib()
        self.face_lib.generate_database("/vision_module/database")
        self.face_lib.load_database("/vision_module/database")
        # self.face_detector = FaceDetector()
        # self.face_recognizer = FaceRecognizer()
        # self.face_recognizer.convert_faces_to_features_in_files("/vision_module/database")
        # self.face_recognizer.load_face_features_from_file("/vision_module/database")

    def add_person(self, name, image):
        detected_faces, largest_face_index = self.face_lib.detect_faces(image)
        if len(detected_faces) > 0:
            largest_face = [detected_faces[largest_face_index]]
            ret = self.face_lib.add_person(name, image, largest_face)
            if ret != 0:
                print("Error during adding person")
                return False
            return True
        else:
            return False
    
    def remove_person(self, name):
        logging.info("In remove person")
        try:
            shutil.rmtree("/vision_module/database/" + name)
        except:
            logging.warning('Error while removing person, please try again later..')
        self.face_lib.load_database("/vision_module/database")

    def run(self, image, face_recognition_confidence):
        detected_faces, largest_face_index = self.face_lib.detect_faces(image)
        largest_face = []
        if largest_face_index > -1:
            largest_face = [detected_faces[largest_face_index]]
        all_face_features = self.face_lib.get_face_features(image, largest_face)
        coordinates = []
        if len(detected_faces) == 0:
            coordinates = []
        else:
            for face in detected_faces:
                face_coordinate = face['face_coordinates']
                coordinates.append([face_coordinate[1], face_coordinate[0], face_coordinate[3], face_coordinate[2]])
        identity = "Unknown"
        confidence = 0
        for face_features in all_face_features:
            if self.face_lib.face_database["Features"] is not None:
                similarity = np.dot(self.face_lib.face_database["Features"], face_features.T).squeeze()
                similarity = 1.0 / (1 + np.exp(-1 * (similarity - 0.38) * 10))
                if not isinstance(similarity, np.ndarray):
                    similarity = np.array([similarity])
                identity, confidence = self.face_lib.get_best_match_identity(similarity)
        return '{ "mode" : "FaceRecognition", "coordinates": "' + str(coordinates) + '", "name": "' + identity + '", "confidence": "' + str(confidence) + '", "largestID": "' + str(largest_face_index) + '" }'
