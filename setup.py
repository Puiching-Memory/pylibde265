from setuptools import setup, Extension, find_packages
import os
import shutil

from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_modules = [
    Extension(
        "pylibde265.pyde265",
        sources=["./src/pylibde265/pyde265.pyx"],
        include_dirs=[
            "./libde265/build/",
            "./libde265/libde265/",
        ],
        library_dirs=["./libde265/build/libde265/Release/"],
        libraries=["de265"],
    )
]

setup(
    name="pylibde265",
    ext_modules=cythonize(ext_modules),
    # packages=find_packages(include=['src/pylibde265','src/pylibde265.*']),
    # include_package_data=True,
    # zip_safe=False,
    data_files=[
        ("", ["./libde265/build/libde265/Release/libde265.dll"]),
        ("Lib/site-packages/pylibde265", ["typing/pyde265.pyi"]),
    ],
)
