import os

for file in os.listdir('data'):
    if not len(file.split(".")) == 1:
        continue
    with open('data/' + file, 'rb') as f:
        file_content = f.read()
        new_content = b"GIF89a" + file_content[6:]
        with open('data/' + file + ".gif", 'wb') as f:
            f.write(new_content)
