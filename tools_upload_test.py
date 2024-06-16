import os



if __name__ == "__main__":
    os.system('twine upload --repository testpypi dist/*')