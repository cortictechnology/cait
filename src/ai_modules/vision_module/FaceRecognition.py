""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, November 2019

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
import io
import shutil
import json

logging.getLogger().setLevel(logging.INFO)

class FaceRecognition:
    def __init__(self, inferenceProcessor="local"):
        self.ctx = tvm.cpu()

        loaded_json = open("/vision_module/tuned32_2_mobilefacenet_graph.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned32_2_mobilefacenet_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned32_2_mobilefacenet_param.params", "rb").read())
        self.mobilefacenet_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.mobilefacenet_module.load_params(loaded_params)

        self.value = [0, 0, 0]
        self.borderType = cv2.BORDER_CONSTANT

        self.ref_landmarks = np.array([
            [38.43497931, 52.31110286], 
            [75.87859646, 51.98545311], 
            [55.99915243, 74.61763367], 
            [56.40823808, 93.73636859], 
            [20.25721617, 58.40528653], 
            [96.15278721, 58.09566583]], dtype=np.float32)
        self.ref_landmarks = np.expand_dims(self.ref_landmarks, axis=0)
        self.image_size = 112

        self.face_database = {"Names": [], "Features": None}

        self.database_location = ""

        self.load_database("/vision_module/database")

    def estimate_norm(self, lmk):
        assert lmk.shape == (6, 2)
        tform = trans.SimilarityTransform()
        lmk_tran = np.insert(lmk, 2, values=np.ones(6), axis=1)
        min_M = []
        min_index = []
        min_error = float('inf')
        src = self.ref_landmarks
        
        for i in np.arange(src.shape[0]):
            tform.estimate(lmk, src[i])
            M = tform.params[0:2, :]
            results = np.dot(M, lmk_tran.T)
            results = results.T
            error = np.sum(np.sqrt(np.sum((results - src[i]) ** 2, axis=1)))
            if error < min_error:
                min_error = error
                min_M = M
                min_index = i
        return min_M, min_index

    def norm_crop(self, img, landmark):
        M, pose_index = self.estimate_norm(landmark)
        warped = cv2.warpAffine(img, M, (self.image_size, self.image_size), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        return warped

    def get_face_features(self, _img, detected_faces):
        #img = np.copy(_img)
        #img = img[...,::-1]
        all_face_features = []
        for face in detected_faces:
            ymin = int(face['face_coordinates'][0] - _img.shape[0] * 0.2)
            xmin = int(face['face_coordinates'][1] - _img.shape[1] * 0.2)
            ymax = int(face['face_coordinates'][2] + _img.shape[0] * 0.2)
            xmax = int(face['face_coordinates'][3] + _img.shape[1] * 0.2)
            if ymin < 0:
                ymin = 0
            if xmin < 0:
                xmin = 0
            if ymax >= _img.shape[0]:
                ymax = _img.shape[0] - 1
            if xmax >= _img.shape[1]:
                xmax = _img.shape[1] - 1
            crop_img = _img[ymin:ymax, xmin:xmax, :]
            face_landmarks = np.zeros((6, 2))
            for k in range(6):
                face_landmarks[k, 0] = face['landmark_coordinates'][k*2] - xmin
                face_landmarks[k, 1] = face['landmark_coordinates'][k*2+1] - ymin
            warp_img = self.norm_crop(crop_img, face_landmarks)
            warp_img = cv2.cvtColor(warp_img, cv2.COLOR_BGR2RGB)
            warp_img = warp_img.transpose((2, 0, 1))
            warp_img = warp_img[np.newaxis, :]
            self.mobilefacenet_module.run(data=warp_img)
            face_features = self.mobilefacenet_module.get_output(0).asnumpy()
            all_face_features.append(face_features)

        return all_face_features

    def generate_database(self, image_location, face_detection_model):
        for dir in os.listdir(image_location):
            item = os.path.join(image_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if not file.endswith(".bin"):
                        image_path = os.path.join(item, file)
                        img = cv2.imread(image_path)
                        detected_faces, largest_face_index = face_detection_model.detect_faces(img)
                        if len(detected_faces) > 0:
                            face_features = self.get_face_features(img, detected_faces)[0]
                            face_features.tofile(item+"/features.bin")
                        else:
                            logging.warning("No face detected for: " + file)

    def load_database(self, database_location):
        self.database_location = database_location
        self.face_database = {"Names": [], "Features": None}
        for dir in os.listdir(database_location):
            item = os.path.join(database_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if file.endswith(".bin"):
                        self.face_database["Names"].append(dir)
                        feature = np.fromfile(item+"/features.bin", np.float32)
                        if self.face_database["Features"] is None:
                            self.face_database["Features"] = feature
                        else:
                            self.face_database["Features"] = np.vstack((self.face_database["Features"], feature))
    
    def add_person_face(self, name, _img, detected_faces):
        face_features = self.get_face_features(_img, detected_faces)[0]
        new_dir = os.path.join(self.database_location, name)
        try:
            os.mkdir(new_dir)
        except OSError:
            logging.info("Creation of the directory new person directory failed")
            return -1
        else:
            cv2.imwrite(os.path.join(new_dir, "face.jpg"), _img)
            feature_path = os.path.join(new_dir, "features.bin")
            face_features.tofile(feature_path)
            self.load_database(self.database_location)
            return 0


    def get_best_match_identity(self, similarity_scores, threshold=0.7):
        sort_idx = np.argsort(-similarity_scores)
        if similarity_scores[sort_idx[0]] >= threshold:
            return self.face_database["Names"][sort_idx[0]], similarity_scores[sort_idx[0]]
        else:
            return "Unknown", similarity_scores[sort_idx[0]]


    def add_person(self, name, image, detected_faces, largest_face_index):
        if len(detected_faces) > 0:
            largest_face = [detected_faces[largest_face_index]]
            ret = self.add_person_face(name, image, largest_face)
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
        self.load_database("/vision_module/database")

    def run(self, image, detected_faces, largest_face_index, face_recognition_confidence=0.7):
        largest_face = []
        if largest_face_index > -1:
            largest_face = [detected_faces[largest_face_index]]
        all_face_features = self.get_face_features(image, largest_face)
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
            if self.face_database["Features"] is not None:
                similarity = np.dot(self.face_database["Features"], face_features.T).squeeze()
                similarity = 1.0 / (1 + np.exp(-1 * (similarity - 0.38) * 10))
                if not isinstance(similarity, np.ndarray):
                    similarity = np.array([similarity])
                identity, confidence = self.get_best_match_identity(similarity, face_recognition_confidence)
        return '{ "mode" : "FaceRecognition", "coordinates": "' + str(coordinates) + '", "name": "' + identity + '", "confidence": "' + str(confidence) + '", "largestID": "' + str(largest_face_index) + '" }'
