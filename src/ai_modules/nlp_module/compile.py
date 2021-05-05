from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("nlu",  ["/nlp_module/nlu.py"])
]
setup(
    name = 'NLP Module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)