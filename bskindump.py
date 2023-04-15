import os
import sys
import zipfile
import requests
import http.cookiejar as cookiejar

URL = "https://api.bilibili.com/x/garb/v2/mall/suit/detail?from=&from_id=&item_id={}&part=suit"

if len(sys.argv) != 3:
    print("Usage: python bskindump.py <cookies.txt> <skin id>")
    sys.exit(1)

def find_image_values(data, path=''):
    image_values = {}
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = path + '.' + str(key) if path else str(key)
            image_values.update(find_image_values(value, new_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = path + '.' + str(i) if path else str(i)
            image_values.update(find_image_values(item, new_path))
    elif isinstance(data, str):
        if data.lower().endswith(('.jpeg', '.jpg', '.png', '.gif', '.webp', '.zip', '.mp4', '.bin')) and data.lower().startswith(('http://', 'https://')):
            fname = path + "." +  data.split('.')[-1]
            image_values[fname] = data
    return image_values

skin_id = sys.argv[2]
cookies = cookiejar.MozillaCookieJar()
cookies.load(sys.argv[1], ignore_discard=True, ignore_expires=True)
res = requests.get(URL.format(skin_id), cookies=cookies)
if res.status_code != 200:
    print("Error: HTTP %d" % res.status_code)
    sys.exit(1)

data = res.json().get("data", {})
images = find_image_values(data)
for path, url in images.items():
    dest = os.path.join("skindump", skin_id, path)
    dirname = os.path.dirname(dest)
    print("Downloading %s" % url)
    print("  Saving to %s" % dest)
    res = requests.get(url)
    if res.status_code != 200:
        print("Error: HTTP %d" % res.status_code)
        continue
    os.makedirs(dirname, exist_ok=True)
    with open(dest, "wb+") as f:
        f.write(res.content)

    if dest.endswith(".zip"):
        os.makedirs(dest[:-4], exist_ok=True)
        with zipfile.ZipFile(dest, "r") as z:
            z.extractall(dest[:-4])
    
    if dest.endswith(".bin"):
        os.rename(dest, dest[:-4] + ".svga")
