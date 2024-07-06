import os

if __name__ == "__main__":
    os.system('twine upload dist/*')
    #os.system('hatch publish')