import os
import sys
import uuid
import requests
import http.cookiejar as cookiejar

if len(sys.argv) != 3:
    print("Usage: python sticker_get.py <cookies.txt> <id>")
    sys.exit(1)

cookies = cookiejar.MozillaCookieJar()
cookies.load(sys.argv[1], ignore_discard=True, ignore_expires=True)
package_id = int(sys.argv[2])
res = requests.get(
    f"https://api.bilibili.com/x/emote/package?business=reply&ids={package_id}",
    cookies=cookies)
if res.status_code != 200:
    print("Error: HTTP %d" % res.status_code)
    sys.exit(1)
data = res.json()["data"]["packages"][0]["emote"]
data.sort(key=lambda x: x["id"])
prefix = f"pictures/{package_id}-{str(uuid.uuid4())[:8]}"

os.makedirs(prefix, exist_ok=True)
print("Saving to %s" % prefix)

for i in data:
    name = i["text"][1:-1]
    url = i["url"]
    dest = os.path.join(prefix, name + ".png")
    print("Downloading %s" % url)
    print("  Saving to %s" % dest)
    res = requests.get(url)
    if res.status_code != 200:
        print("Error: HTTP %d" % res.status_code)
        continue
    with open(dest, "wb+") as f:
        f.write(res.content)
