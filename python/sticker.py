import os
import sys
import shutil
import zipfile
import argparse
import requests
import connection
from conf import CONF
from PIL import Image
from qcloud_cos import CosConfig, CosS3Client


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}


def load_downloaded_sticker_sets() -> list:
    folders         = os.listdir(CONF.PATH_STICKERS)
    sticker_folders = list(filter(lambda x: ('-' in x) and not x.startswith("."), folders))
    sticker_sets    = [
        {
            "id":       int(item.split('-')[0]),
            "name":     item.split('-')[1],
            "stickers": list(filter(lambda x: x.endswith(".png"),
                                    os.listdir(os.path.join(CONF.PATH_STICKERS, item))))
        }
        for item in sticker_folders
    ]
    return sticker_sets


def load_fetched_sticker_sets() -> list:
    with open(CONF.PATH_STICKERS_LIST, "r", encoding="utf-8") as f:
        lines = f.readlines()
    lines = [tuple(i.strip().split('\t')) for i in lines]
    sticker_sets = [
        {
            "id":   int(item[0]),
            "name": item[1]
        }
        for item in lines
    ]
    return sticker_sets


def fetch():
    cookies  = connection.load_cookies()
    response = requests.get(CONF.URL_FETCH_STICKERS, cookies=cookies, headers=HEADERS)
    connection.ensure_ok(response)

    sticker_sets = response.json()["data"]["all_packages"]
    sticker_sets.sort(key=lambda x: x["id"])
    sticker_sets = ["{}\t{}".format(i["id"], i["text"]) for i in sticker_sets]

    with open(CONF.PATH_STICKERS_LIST, "w+") as f:
        f.write("\n".join(sticker_sets))
    print(f"Fetched {len(sticker_sets)} stickers.")


def dump(id: int):
    cookies  = connection.load_cookies()
    response = requests.get(CONF.URL_DUMP_STICKERS_F.format(id), cookies=cookies, headers=HEADERS)
    connection.ensure_ok(response)

    sticker_set      = response.json()["data"]["packages"][0]
    sticker_set_id   = sticker_set["id"]
    sticker_set_name = sticker_set["text"]
    stickers         = sticker_set["emote"]
    stickers.sort(key=lambda x: x["id"])
    dist = os.path.join(CONF.PATH_STICKERS, f"{sticker_set_id}-{sticker_set_name}")

    os.makedirs(dist, exist_ok=True)
    print(f"Saving stickers to {dist}")
    for sticker in stickers:
        sticker_url      = sticker["url"]
        sticker_name     = sticker["text"][1:-1]
        sticker_filename = os.path.join(dist, f"{sticker_name}.png")
        print(f"  Downloading: {sticker_name}")
        sticker_response = requests.get(sticker_url)
        connection.ensure_ok(sticker_response)
        print(f"    Saving to: {sticker_filename}")
        with open(sticker_filename, "wb+") as f:
            f.write(sticker_response.content)


def find(keyword: str):
    if not os.path.exists(CONF.PATH_STICKERS_LIST):
        print("Not fetched stickers yet, fetching...")
        fetch()
    sticker_sets_downloaded  = load_downloaded_sticker_sets()
    sticker_sets_fetched     = load_fetched_sticker_sets()

    query_sticker_downloaded = [s for s in sticker_sets_downloaded if keyword in s["name"]]
    print(f"In downloaded stickers, found {len(query_sticker_downloaded)}:")
    for sticker_set in query_sticker_downloaded:
        print(f"  {sticker_set['id']:>8}  {sticker_set['name']}")

    sticker_sets_fetched         = [s for s in sticker_sets_fetched if keyword in s["name"]]
    sticker_sets_fetched         = [s for s in sticker_sets_fetched if s["id"] not in [s["id"] for s in query_sticker_downloaded]]
    print(f"In fetched stickers, found {len(sticker_sets_fetched)} (that not downloaded):")
    for sticker_set in sticker_sets_fetched:
        print(f"  {sticker_set['id']:>8}  {sticker_set['name']}")


def show(id: int):
    sticker_sets = load_downloaded_sticker_sets()
    sticker_sets = list(filter(lambda x: x["id"] == id, sticker_sets))
    if len(sticker_sets) == 0:
        print(f"Unable to find sticker set {id}.")
        sys.exit(1)

    sticker_set = next(iter(sticker_sets))
    print(f"Sticker set {id}: {sticker_set['name']}")
    for sticker in sticker_set["stickers"]:
        print(f"    {sticker}")


def pack(silent: bool = False):
    shutil.rmtree(CONF.DIST_STICKERS, ignore_errors=True)
    os.makedirs(CONF.DIST_STICKERS, exist_ok=True)
    for sticker_set in load_downloaded_sticker_sets():
        zip_filename = os.path.join(CONF.DIST_STICKERS, f"{sticker_set['id']}-{sticker_set['name']}.zip")
        print(f"Creating {zip_filename}")
        with zipfile.ZipFile(zip_filename, "w") as f:
            for sticker in sticker_set["stickers"]:
                sticker_filename = os.path.join(CONF.PATH_STICKERS, f"{sticker_set['id']}-{sticker_set['name']}", sticker)
                if not silent:
                    print(f"    Adding {sticker_filename}")
                f.write(sticker_filename, f"{sticker_set['id']}-{sticker_set['name']}/{sticker}")


def upload(dry: bool = True):
    if CONF.COS_SECRET_ID is None or CONF.COS_SECRET_KEY is None:
        print("Unable to find COS credentials.")
        print("Please save credentials to '{}'".format(CONF.CRED_COS_CREDENTIALS))
        sys.exit(1)
    pack(silent=True)
    client = CosS3Client(CosConfig(None, CONF.COS_REGION, CONF.COS_SECRET_ID, CONF.COS_SECRET_KEY))
    for filename in os.listdir(CONF.DIST_STICKERS):
        if not filename.endswith(".zip") or filename.startswith("."):
            continue
        print(f"Uploading {filename}")
        if not dry:
            client.upload_file(
                Bucket=CONF.COS_BUCKET,
                LocalFilePath=os.path.join(CONF.DIST_STICKERS, filename),
                Key=f"{CONF.COS_PREFIX}{filename}",
                PartSize=10,
                MAXThread=10
            )
    update_readme()


def update_readme(include_telegram: bool = False):
    update_readme_cdn()
    if include_telegram:
        update_readme_telegram()
    print("Markdown updated.")


def readme_update_block(mark: str, content: str) -> str:
    with open(CONF.PATH_README, "r", encoding="utf-8") as f:
        readme = f.read()
        start, _ , end = [x.strip() for x in readme.split(mark)]
    with open(CONF.PATH_README, "w", encoding="utf-8") as f:
        f.write("".join([
            start,
            "\n\n",
            mark,
            "\n",
            content,
            "\n",
            mark,
            "\n\n",
            end,
            "\n"
        ]))


def update_readme_cdn():
    sticker_sets = load_downloaded_sticker_sets()
    sticker_sets.sort(key=lambda x: x["id"])
    links_text = []
    for sticker_set in sticker_sets:
        link_label = f"[cos-{sticker_set['id']}]:"
        link_url   = f"https://{CONF.COS_DOMAIN}/{CONF.COS_PREFIX}{sticker_set['id']}-{sticker_set['name']}.zip"
        links_text.append(f"{link_label:<14}{link_url}")
    readme_update_block(CONF.MARK_CDN, "\n".join(links_text))


def update_readme_telegram():
    if not os.path.exists(CONF.PATH_STICKERS_TG_LINK):
        print(f"Unable to find Telegram links configuration file '{CONF.PATH_STICKERS_TG_LINK}'.")
        return
    with open(CONF.PATH_STICKERS_TG_LINK, "r", encoding="utf-8") as f:
        links = []
        for line in f.readlines():
            if not line or line.strip().startswith("#") or line.strip() == "":
                continue
            sticker_set_id, sticker_set_link = line.strip().split("=")
            links.append((int(sticker_set_id.strip()), sticker_set_link.strip()))
    links.sort(key=lambda x: x[0])
    links_text = []
    for sticker_set_id, sticker_set_link in links:
        link_label = f"[tg-{sticker_set_id}]:"
        link_url   = f"https://t.me/addstickers/{sticker_set_link}"
        links_text.append(f"{link_label:<14}{link_url}")
    readme_update_block(CONF.MARK_TELEGRAM, "\n".join(links_text))


def resize(target: str):
    if target == "tg":
        resize_telegram()
        return
    print("Unknown platform:", target)


def resize_telegram():
    sticker_sets = load_downloaded_sticker_sets()
    for sticker_set in sticker_sets:
        print(f"Sticker set {sticker_set['id']}: {sticker_set['name']}")
        src  = os.path.join(CONF.PATH_STICKERS,  f"{sticker_set['id']}-{sticker_set['name']}")
        dest = os.path.join(CONF.DIST_TELEGRAM, f"{sticker_set['id']}-{sticker_set['name']}")
        os.makedirs(dest, exist_ok=True)
        for filename in os.listdir(src):
            if not filename.endswith(".png"):
                continue
            print("  Scaling", filename)
            img = Image.open(os.path.join(src, filename))
            img = img.resize((512, 512), Image.LANCZOS)
            img.save(os.path.join(dest, filename))
        print("Saved to", dest, "\n")


def main(argument: argparse.Namespace):
    if argument.action == "fetch":
        fetch()
    if argument.action == "dump":
        dump(argument.id)
    if argument.action == "find":
        find(argument.keyword)
    if argument.action == "show":
        show(argument.id)
    if argument.action == "pack":
        pack(argument.silent)
    if argument.action == "upload":
        upload(argument.dry)
    if argument.action == "resize":
        resize(argument.target)
    if argument.action == "update-readme":
        update_readme(argument.tg)
