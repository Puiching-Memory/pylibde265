import os



if __name__ == "__main__":
    #os.system('python setup.py build_ext --inplace')
    #os.system('python setup.py bdist_wheel')

    #os.system('python -m build')
    os.system('hatch build')