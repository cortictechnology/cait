""" 

Copyright (C) Cortic Technology Corp. - All Rights Reserved
Written by Michael Ng <michaelng@cortic.ca>, Feb 2020

Reference: 

https://github.com/hollance/BlazeFace-PyTorch

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

class FaceLib:
    
    def __init__(self):
        self.ctx = tvm.cpu()

        loaded_json = open("/vision_module/tuned_blazeface_graph.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned_blazeface_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned_blazeface_param.params", "rb").read())
        self.blazeface_module = graph_runtime.create(loaded_json, loaded_lib, self.ctx)
        self.blazeface_module.load_params(loaded_params)

        loaded_json = open("/vision_module/tuned3_mobilefacenet_graph.json").read()
        loaded_lib = tvm.runtime.load_module("/vision_module/tuned3_mobilefacenet_lib.tar")
        loaded_params = bytearray(open("/vision_module/tuned3_mobilefacenet_param.params", "rb").read())
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

        self.anchors = np.load("/vision_module/anchors.npy")

        self.database_location = ""

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

    def tensors_to_detections(self, raw_box_tensor, raw_score_tensor, anchors):
        assert raw_box_tensor.ndim == 3
        assert raw_box_tensor.shape[1] == 896
        assert raw_box_tensor.shape[2] == 16

        assert raw_score_tensor.ndim == 3
        assert raw_score_tensor.shape[1] == 896
        assert raw_score_tensor.shape[2] == 1

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

    def decode_boxes(self, raw_boxes, anchors):
        """Converts the predictions into actual coordinates using
        the anchor boxes. Processes the entire batch at once.
        """
        boxes = np.zeros(raw_boxes.shape)

        x_center = raw_boxes[..., 0] / 128.0 * anchors[:, 2] + anchors[:, 0]
        y_center = raw_boxes[..., 1] / 128.0 * anchors[:, 3] + anchors[:, 1]

        w = raw_boxes[..., 2] / 128.0 * anchors[:, 2]
        h = raw_boxes[..., 3] / 128.0 * anchors[:, 3]

        boxes[..., 0] = y_center - h / 2.  # ymin
        boxes[..., 1] = x_center - w / 2.  # xmin
        boxes[..., 2] = y_center + h / 2.  # ymax
        boxes[..., 3] = x_center + w / 2.  # xmax

        for k in range(6):
            offset = 4 + k*2
            keypoint_x = raw_boxes[..., offset    ] / 128.0 * anchors[:, 2] + anchors[:, 0]
            keypoint_y = raw_boxes[..., offset + 1] / 128.0 * anchors[:, 3] + anchors[:, 1]
            boxes[..., offset    ] = keypoint_x
            boxes[..., offset + 1] = keypoint_y

        return boxes

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
            """The alternative NMS method as mentioned in the BlazeFace paper:
            "We replace the suppression algorithm with a blending strategy that
            estimates the regression parameters of a bounding box as a weighted
            mean between the overlapping predictions."
            The original MediaPipe code assigns the score of the most confident
            detection to the weighted detection, but we take the average score
            of the overlapping detections.
            The input detections should be a Tensor of shape (count, 17).
            Returns a list of PyTorch tensors, one for each detected face.
            
            This is based on the source code from:
            mediapipe/calculators/util/non_max_suppression_calculator.cc
            mediapipe/calculators/util/non_max_suppression_calculator.proto
            """
            if len(detections) == 0: return []

            output_detections = []

            # Sort the detections from highest to lowest score.
            remaining = np.argsort(-detections[:, 16])

            while len(remaining) > 0:
                detection = detections[remaining[0]]
                # Compute the overlap between the first box and the other 
                # remaining boxes. (Note that the other_boxes also include
                # the first_box.)
                first_box = detection[:4]
                other_boxes = detections[remaining, :4]
                ious = self.overlap_similarity(first_box, other_boxes)

                # If two detections don't overlap enough, they are considered
                # to be from different faces.
                mask = ious > 0.4
                overlapping = remaining[mask]
                remaining = remaining[~mask]

                # Take an average of the coordinates from the overlapping
                # detections, weighted by their confidence scores.
                weighted_detection = np.copy(detection)
                if len(overlapping) > 1:
                    coordinates = detections[overlapping, :16]
                    scores = detections[overlapping, 16:17]
                    total_score = scores.sum()
                    weighted = (coordinates * scores).sum(axis=0) / total_score
                    weighted_detection[:16] = weighted
                    weighted_detection[16] = total_score / len(overlapping)

                output_detections.append(weighted_detection)

            return output_detections    

    def detect_faces(self, _img):
        top = 0
        bottom = 0
        right = 0
        left = 0
        dim = None
        resize_ratio = 1

        img = np.copy(_img)

        if img.shape[0] < img.shape[1]:
            resize_ratio = img.shape[1] / 128.0
            width = int(img.shape[1] / resize_ratio)
            height = int(img.shape[0] / resize_ratio)
            dim = (width, height)
            right = 128 - width
            top = int((width - height) /2 )
            bottom = width - (height + top)
        else:
            resize_ratio = img.shape[0] / 128.0
            width = int(img.shape[1] / resize_ratio)
            height = int(img.shape[0] / resize_ratio)
            dim = (width, height)
            top = 128 - height
            right = int((height - width) / 2)
            left = height - (width + right)

        img = cv2.resize(img, dim, interpolation=cv2.INTER_NEAREST)
        img = cv2.copyMakeBorder(img, top, bottom, left, right, self.borderType, None, self.value)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        image = img.astype("float32")
        image = cv2.normalize(image, None, -1, 1, cv2.NORM_MINMAX)
        image = image[np.newaxis, :]

        self.blazeface_module.run(input=image)

        raw_box_tensor = self.blazeface_module.get_output(0).asnumpy()
        raw_score_tensor = self.blazeface_module.get_output(1).asnumpy()

        detections = self.tensors_to_detections(raw_box_tensor, raw_score_tensor, self.anchors)
        filtered_detections = []
        largest_face_index = -1
        for i in range(len(detections)):
            faces = self.weighted_non_max_suppression(detections[i])
            largest_face_area = 0
            for i in range(len(faces)):
                face = faces[i]
                is_largest_face = False
                face_info = {}
                scaled_coordinates = []
                ymin = int((face[0] * 128 - top) * resize_ratio)
                scaled_coordinates.append(ymin)
                xmin = int((face[1] * 128 - left) * resize_ratio)
                scaled_coordinates.append(xmin)
                ymax = int((face[2] * 128 - top) * resize_ratio)
                scaled_coordinates.append(ymax)
                xmax = int((face[3] * 128 - left) * resize_ratio)
                scaled_coordinates.append(xmax)
                face_info['face_coordinates'] = scaled_coordinates
                if (xmax - xmin) * (ymax - ymin) > largest_face_area:
                    largest_face_area = (xmax - xmin) * (ymax - ymin)
                    is_largest_face = True
                scaled_coordinates = []
                raw_coordinates = []
                for k in range(6):
                    kp_x = int((face[4+k*2] * 128 - left) * resize_ratio)
                    scaled_coordinates.append(kp_x)
                    raw_coordinates.append(face[4+k*2])
                    kp_y = int((face[4+k*2+1] * 128 - top) * resize_ratio)
                    scaled_coordinates.append(kp_y)
                    raw_coordinates.append(face[4+k*2+1])
                face_info['landmark_coordinates'] = scaled_coordinates
                face_info['landmark_raw_coordinates'] = raw_coordinates
                if is_largest_face:
                    largest_face_index = i
                filtered_detections.append(face_info)
        return filtered_detections, largest_face_index

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

    def generate_database(self, image_location):
        for dir in os.listdir(image_location):
            item = os.path.join(image_location, dir)
            if os.path.isdir(item):
                for file in os.listdir(item):
                    if not file.endswith(".bin"):
                        image_path = os.path.join(item, file)
                        img = cv2.imread(image_path)
                        detected_faces, largest_face_index = self.detect_faces(img)
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
    
    def add_person(self, name, _img, detected_faces):
        face_features = self.get_face_features(_img, detected_faces)[0]
        new_dir = os.path.join(self.database_location, name)
        try:
            os.mkdir(new_dir)
        except OSError:
            logging.info("Creation of the directory new person directory failed")
        else:
            cv2.imwrite(os.path.join(new_dir, "face.jpg"), _img)
            feature_path = os.path.join(new_dir, "features.bin")
            face_features.tofile(feature_path)
            self.load_database(self.database_location)

    def get_best_match_identity(self, similarity_scores, threshold=0.7):
        sort_idx = np.argsort(-similarity_scores)
        if similarity_scores[sort_idx[0]] >= threshold:
            return self.face_database["Names"][sort_idx[0]], similarity_scores[sort_idx[0]]
        else:
            return "Unknown", similarity_scores[sort_idx[0]]

# for testing
def main():
    # camera = PiCamera()
    # camera.resolution = (640, 480)
    # camera.framerate = 32
    # rawCapture = PiRGBArray(camera, size=(640, 480))

    cam = cv2.VideoCapture(0)

    time.sleep(0.1)

    face_lib = FaceLib()

    face_lib.generate_database("./database")

    face_lib.load_database("./database")

    #for frame in camera.capture_continuous(rawCapture, format="rgb", use_video_port=True):
    while cam.isOpened():
    #total_landmarks = np.zeros(12).astype("float32")
    #for i in range(20000):    
        #img = frame.array
        _, img = cam.read()
        #img = cv2.imread("./cropped_face_images/" + str(i) + ".jpg")
        #print("Processing image: " + str(i))
        start_time = time.time()

        detected_faces = face_lib.detect_faces(img, get_max_face=True)

        identity = None
        confidence = 0
        
        all_face_features = face_lib.get_face_features(img, detected_faces)
        for face_features in all_face_features:
            similarity = np.dot(face_lib.face_database["Features"], face_features.T).squeeze()
            similarity = 1.0 / (1 + np.exp(-1 * (similarity - 0.38) * 10))
            identity, confidence = face_lib.get_best_match_identity(similarity)

        print(str(detected_faces[0]['face_coordinates']))
        print(identity)
        print(confidence)
        #print(features)
        # for face in detected_faces:
        #     raw_landmarks = np.array(face['landmark_raw_coordinates'])
        #     total_landmarks = total_landmarks + raw_landmarks
        #print(detected_faces)

        # for face in detected_faces:
        #     ymin = face['face_coordinates'][0]
        #     xmin = face['face_coordinates'][1]
        #     ymax = face['face_coordinates'][2]
        #     xmax = face['face_coordinates'][3] 
            #cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (255,0,0), 1)
            # face_landmarks = np.zeros((6, 2))
            # for k in range(6):
            #     face_landmarks[k, 0] = face['landmark_coordinates'][k*2]
            #     face_landmarks[k, 1] = face['landmark_coordinates'][k*2+1]
            #     #cv2.circle(img, (kp_x, kp_y), 1, (0, 0, 255), 2)
            # wrap_img = face_lib.norm_crop(img, face_landmarks)
            #cv2.imshow("face detection", wrap_img)
            #cv2.waitKey(1)
        #faces = torch.stack(faces) if len(faces) > 0 else torch.zeros((0, 17))
        #filtered_detections.append(faces)
        #cv2.imshow("face detection", img)
        #cv2.waitKey(1)

        #rawCapture.truncate(0)

        # blank_img = np.zeros((112,112))
        # landmarks = [
        #     [38.43497931, 52.31110286], 
        #     [75.87859646, 51.98545311], 
        #     [55.99915243, 74.61763367], 
        #     [56.40823808, 93.73636859], 
        #     [20.25721617, 58.40528653], 
        #     [96.15278721, 58.09566583]]
        # for mark in landmarks:
        #     kp_x = int(mark[0])
        #     kp_y = int(mark[1])
        #     cv2.circle(blank_img, (kp_x, kp_y), 1, (255, 255, 255), 2)
        # cv2.imshow("face detection", blank_img)
        # cv2.waitKey(1)

        print("Overall time: ", time.time() - start_time)
    #average_landmarks = total_landmarks / 20000.0
    #print(average_landmarks * 112.0)
    #print(average_landmarks)

if __name__ == '__main__':
    main()
