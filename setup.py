from setuptools import setup,Extension,find_packages
import os

from Cython.Build import cythonize
from Cython.Distutils import build_ext

#package_dir = {
#    'pylibde265': './lib',
#}

def extension_sources(directory, suffix):
    matches = []  
    for root, dirnames, filenames in os.walk(directory):  
        for filename in filenames:  
            if filename.endswith(suffix):  
                matches.append(os.path.join(root, filename))  
    return matches  

ext_modules = [
    Extension("pylibde265",
              sources=extension_sources('./pylibde265','.pyx'),
              include_dirs=[os.path.abspath('./pylibde265/lib')],
              libraries=['./pylibde265/lib/de265'],
              #language='c++',
              #extra_compile_args=['-std=c++11'],
              )
]

setup(
    name='pylibde265',
    ext_modules=cythonize(ext_modules),
    packages=find_packages(include=['./pylibde265']),
    cmdclass={"build_ext": build_ext},
)