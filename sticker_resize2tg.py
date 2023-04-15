import os
import sys
import shutil
from PIL import Image

if len(sys.argv) != 2:
    print("Usage: python sticker_resize2tg.py <id>")
    sys.exit(1)

sticker_group_id = int(sys.argv[1])
for filename in os.listdir("pictures"):
    try:
        if int(filename.split("-")[0].strip()) == sticker_group_id:
            sticker_group_path = filename
            break
    except ValueError:
        continue
print("表情包名称:", sticker_group_path)

source = os.path.join("pictures", sticker_group_path)
target = os.path.join("telegram", sticker_group_path)
shutil.rmtree(target, ignore_errors=True)
os.makedirs(target, exist_ok=True)

for filename in os.listdir(source):
    if not filename.endswith(".png"):
        continue
    print("正在缩放", filename)
    img = Image.open(os.path.join(source, filename))
    img = img.resize((512, 512), Image.ANTIALIAS)
    img.save(os.path.join(target, filename))
print("完成")
