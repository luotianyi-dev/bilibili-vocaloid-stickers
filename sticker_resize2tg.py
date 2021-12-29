import os
import sys
import shutil
from PIL import Image

sticker_group_id = int(sys.argv[1])
sticker_group_path = list(filter(lambda name: int(name.split("-")[0].strip()) == sticker_group_id, os.listdir("pictures")))[0]
print("表情包名称:", sticker_group_path)

source = os.path.join("pictures", sticker_group_path)
target = os.path.join("telegram", sticker_group_path)
shutil.rmtree(target, ignore_errors=True)
os.makedirs(target, exist_ok=True)

for filename in os.listdir(source):
    print("正在缩放", filename)
    img = Image.open(os.path.join(source, filename))
    img = img.resize((512, 512), Image.ANTIALIAS)
    img.save(os.path.join(target, filename))
print("完成")
