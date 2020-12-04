from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("facelib",  ["/vision_module/facelib.py"]),
    Extension("FaceRecognition",  ["/vision_module/FaceRecognition.py"]),
    Extension("ObjectDetection",  ["/vision_module/ObjectDetection.py"]),
    Extension("object_detection",  ["/vision_module/object_detection.py"]),
    Extension("ImageClassification",  ["/vision_module/ImageClassification.py"]),
    Extension("image_classify",  ["/vision_module/image_classify.py"]),
    Extension("inference",  ["/vision_module/inference.py"])
]
setup(
    name = 'Vision Module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)