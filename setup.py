from setuptools import setup, Extension, find_packages
import os
import shutil
import numpy as np

from Cython.Build import cythonize
from Cython.Distutils import build_ext

ext_modules = [
    Extension(
        "pylibde265.de265",
        sources=["./src/pylibde265/de265.pyx"],
        include_dirs=[
            "./libde265/build/",
            "./libde265/libde265/",
            np.get_include(),
        ],
        library_dirs=["./libde265/build/libde265/Release/"],
        libraries=["de265"],
        extra_compile_args=[
            "/openmp",
            # "/showIncludes"
        ],  # only for Windows MSVC
    ),
    Extension(
        "pylibde265.visualize",
        sources=["./src/pylibde265/visualize.pyx"],
        include_dirs=[
            "./libde265/build/",
            "./libde265/",
            "./libde265/libde265/",
            np.get_include(),
        ],
        library_dirs=["./libde265/build/libde265/Release/"],
        libraries=["de265"],
        extra_compile_args=[
            "/openmp",
            # "/showIncludes"
        ],  # only for Windows MSVC
        language='c++',
    ),
]

setup(
    name="pylibde265",
    ext_modules=cythonize(ext_modules, nthreads=os.cpu_count(), annotate=True),
    data_files=[
        ("", ["./libde265/build/libde265/Release/libde265.dll"]),
        ("Lib/site-packages/pylibde265", ["typing/de265.pyi"]),
    ],
)
