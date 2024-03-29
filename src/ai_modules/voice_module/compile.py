from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("voice",  ["/voice_module/voice.py"])
]
setup(
    name = 'Voice Module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)