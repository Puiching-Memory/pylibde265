import os

toml_path = './pyproject.toml'

include_path = os.path.abspath('./src/pylibde265/lib').replace('\\','/')

with open(toml_path,'r',encoding='utf8') as file:
    data = file.readlines()

    #print(data)
    for index,line in enumerate(data):
        if line.startswith('library_dirs'):
            print(line,index)
            data[index] = f'library_dirs = ["{include_path}"]\n'

    print(data)

with open(toml_path,'w',encoding='utf8') as file:
    file.writelines(data)