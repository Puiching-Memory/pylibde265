import os

if __name__ == "__main__":
    command = 'coverage run -m pytest'

    os.system(command=command)

    command = 'coverage report -m'

    os.system(command=command)