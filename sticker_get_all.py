import sys
import requests
import http.cookiejar as cookiejar

if len(sys.argv) != 2:
    print("Usage: python sticker_get_all.py <cookies.txt>")
    sys.exit(1)

cookies = cookiejar.MozillaCookieJar()
cookies.load(sys.argv[1], ignore_discard=True, ignore_expires=True)
res = requests.get("https://api.bilibili.com/x/emote/setting/panel?business=reply", cookies=cookies)
if res.status_code != 200:
    print("Error: HTTP %d" % res.status_code)
    sys.exit(1)
data = res.json()["data"]["all_packages"]
data.sort(key=lambda x: x["id"])
data = ["{}\t{}".format(i["id"], i["text"]) for i in data]

with open("sticker_list.tsv", "w+") as f:
    f.write("\n".join(data))
