import os
import sys
import requests
from conf import CONF
from http import cookiejar

def ensure_ok(res: requests.Response, excepted_status: int = 200) -> None:
    if res.status_code != excepted_status:
        print(f"HTTP Error: {res.request.method} {res.status_code} {res.url}")
        sys.exit(2)

def load_cookies() -> cookiejar.MozillaCookieJar:
    if not os.path.exists(CONF.CRED_BILIBILI_COOKIES):
        print("Unable to find cookies file.")
        print("Please login to Bilibili and save cookies to '{}'".format(CONF.CRED_BILIBILI_COOKIES))
        sys.exit(1)
    cookies = cookiejar.MozillaCookieJar()
    cookies.load(CONF.CRED_BILIBILI_COOKIES, ignore_discard=True, ignore_expires=False)
    return cookies
