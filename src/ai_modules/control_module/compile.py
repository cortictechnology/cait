from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("control",  ["/control_module/control.py"])
]
setup(
    name = 'Control Module',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)