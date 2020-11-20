from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("component_manager",  ["./managers/component_manager.py"]),
    Extension("device_manager",  ["./managers/device_manager.py"]),
    Extension("offloading_device_manager",  ["./managers/offloading_device_manager.py"]),
    Extension("cait_core",  ["cait_core.py"]),
    Extension("core",  ["core.py"]),
    Extension("essentials",  ["essentials.py"])
]
setup(
    name = 'cait',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)