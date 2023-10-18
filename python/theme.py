import os
import sys
import uuid
import shutil
import zipfile
import argparse
import requests
import connection
import http.server
import socketserver
from conf import CONF


def local_themes():
    themes_id = os.listdir(CONF.PATH_THEMES)
    themes_id = [i for i in themes_id if i.isdigit()]
    themes_id = [i for i in themes_id if not i.startswith(".")]
    themes_id.sort(key=lambda x: int(x))
    return themes_id


def find_resources(data, path=''):
    resources = {}
    if isinstance(data, dict):
        for key, value in data.items():
            new_path = path + '.' + str(key) if path else str(key)
            resources.update(find_resources(value, new_path))
    elif isinstance(data, list):
        for i, item in enumerate(data):
            new_path = path + '.' + str(i) if path else str(i)
            resources.update(find_resources(item, new_path))
    elif isinstance(data, str):
        if data.lower().endswith(('.jpeg', '.jpg', '.png', '.gif', '.webp', '.zip', '.mp4', '.bin')) and data.lower().startswith(('http://', 'https://')):
            fname = path + "." +  data.split('.')[-1]
            resources[fname] = data
    return resources


def dump_theme(id: int):
    cookies = connection.load_cookies()
    response = requests.get(CONF.URL_DUMP_THEME_F.format(id), cookies=cookies)
    connection.ensure_ok(response)
    data = response.json().get("data", {})
    resources = find_resources(data)

    for filename, url in resources.items():
        dest = os.path.join(CONF.PATH_THEMES, str(id), filename)
        os.makedirs(os.path.dirname(dest), exist_ok=True)

        print(f"Downloading {url}")
        resource_response = requests.get(url)
        connection.ensure_ok(resource_response)

        print(f"  Saving to {dest}")
        with open(dest, "wb+") as f:
            f.write(resource_response.content)
        if dest.endswith(".zip"):
            os.makedirs(dest[:-4], exist_ok=True)
            with zipfile.ZipFile(dest, "r") as z:
                z.extractall(dest[:-4])
        if dest.endswith(".bin"):
            os.rename(dest, dest[:-4] + ".svga")


def generate_html(theme_id: int, filename: str):
    with open(CONF.PATH_TEMPLATE_SVGA, "r") as f:
        template = f.read()
    template = template.replace("%name%",     f"{theme_id}/{filename}.svga")
    template = template.replace("%theme_id%", f"{theme_id}")
    template = template.replace("%output%",   os.path.abspath(os.path.join(CONF.PATH_THEMES_GIF, str(theme_id), filename + ".mp4")))
    template = template.replace("%savename%", filename + ".mp4")
    template = template.replace("%path%",     os.path.join(CONF.PATH_SVGA_RSEOURCES, str(theme_id), filename + ".svga"))
    print(os.path.join(CONF.PATH_SVGA_RSEOURCES, str(theme_id), filename + ".svga"))
    return template


def svga_theme(host: str, port: int):
    wwwroot = os.path.join(CONF.DIST_SVGA_WWWROOT, str(uuid.uuid4()))
    resroot = os.path.join(wwwroot, CONF.PATH_SVGA_RSEOURCES)
    os.makedirs(resroot, exist_ok=True)
    shutil.copy(CONF.PATH_SVGA_LIBRARY, resroot)

    for theme_id in local_themes():
        for svga in os.listdir(os.path.join(CONF.PATH_THEMES, theme_id)):
            if svga.endswith(".svga"):
                svga_src  = os.path.join(CONF.PATH_THEMES, theme_id, svga)
                svga_dest = os.path.join(resroot, theme_id, svga)
                html_dist = os.path.join(wwwroot, theme_id, svga[:-5] + ".html")
                os.makedirs(os.path.dirname(svga_dest), exist_ok=True)
                shutil.copy(svga_src, svga_dest)
                os.makedirs(os.path.dirname(html_dist), exist_ok=True)
                with open(html_dist, "w+") as f:
                    f.write(generate_html(theme_id, svga[:-5]))
    print(f"SVGA files are ready at {wwwroot}")

    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=wwwroot, **kwargs)
    with socketserver.TCPServer((host, port), Handler) as httpd:
        print("Please open http://{}:{}/ in your browser".format(host, port))
        httpd.serve_forever()


def open_theme(id: int):
    theme_folder = os.path.join(CONF.PATH_THEMES, str(id))
    if not os.path.exists(theme_folder):
        print(f"Unable to find theme {id}")
        sys.exit(1)
    platform = os.uname().sysname
    open_command = CONF.SHELL_OPEN_WINDOWS
    if platform == "Darwin":
        open_command = CONF.SHELL_OPEN_MACOSX
    if platform == "Linux":
        open_command = CONF.SHELL_OPEN_LINUX
    os.system(f"{open_command} {theme_folder}")


def list_theme():
    themes_id = local_themes()
    for theme in themes_id:
        print(f"    id = {theme:<12}:", os.path.abspath(os.path.join(CONF.PATH_THEMES, theme)))


def main(argument: argparse.Namespace):
    if argument.action == "dump":
        dump_theme(argument.id)
    if argument.action == "svga":
        svga_theme(argument.host, argument.port)
    if argument.action == "open":
        open_theme(argument.id)
    if argument.action == "list":
        list_theme()
