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

    #print(matches)
    return matches  

ext_modules = [
    Extension("pylibde265.pyde265",
              sources=['src/pylibde265/pyde265.pyx'],
              include_dirs=['src/pylibde265/libde265'],
              library_dirs=['src/pylibde265/lib'],
              libraries=['de265'],
              #language='c++',
              #extra_compile_args=[''],
              )
]

setup(
    name='pylibde265',
    ext_modules=cythonize(ext_modules),
    packages=find_packages(include=['src/pylibde265','src/pylibde265.*']),
    include_package_data=True,
    zip_safe=False,
    data_files=[('', ['src/pylibde265/lib/libde265.dll'])],
)