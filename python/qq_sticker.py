import os
import argparse
from io import BytesIO
from PIL import Image, ImageSequence

QQ_STICKERS_ROOT = os.path.abspath("assets/qq_stickers")

def convert_gif(src: str, dest: str):
    with open(src, "rb") as f:
        file_content = f.read()
        new_content = b"GIF89a" + file_content[6:]
        with BytesIO(new_content) as bs:
            with Image.open(bs) as img:
                frames = [f for f in ImageSequence.Iterator(img)]
                print(f"      [GIF] Frames: {len(frames)}")
                frames[0].save(
                    dest,
                    save_all=True,
                    append_images=frames[1:],
                    loop=1,
                    disposal=2,
                )

def scale_gif(src: str, dest: str, width: int, height: int):
    with open(src, "rb") as f:
        with Image.open(src) as img:
            frames = [f.resize((width, height)) for f in ImageSequence.Iterator(img)]
            print(f"      [GIF] Frames: {len(frames)}")
            print(f"      [GIF] Size: {width}x{height}")
            frames[0].save(
                dest,
                save_all=True,
                append_images=frames[1:],
                loop=1,
                disposal=2,
                width=width,
                height=height,
            )

def main (_arguments: argparse.Namespace) -> None:
    for package in os.listdir(QQ_STICKERS_ROOT):
        if package.startswith("."):
            continue
        package_data = os.path.join(QQ_STICKERS_ROOT, package, "data")
        package_dest = os.path.join(QQ_STICKERS_ROOT, package, "gif")
        if not os.path.exists(package_data):
            continue
        os.makedirs(package_dest, exist_ok=True)
        for file in os.listdir(package_data):
            if not len(file.split(".")) == 1:
                continue
            file_src = os.path.join(package_data, file)
            file_dest = os.path.join(package_dest, file + ".gif")
            print(f"Converting: {file_src}")
            print(f"         -> {file_dest}")
            convert_gif(file_src, file_dest)
            scaled_dest = os.path.join(package_dest, file + "_126px.gif")
            print(f"Scaling:    {file_dest}")
            print(f"         -> {scaled_dest}")
            scale_gif(file_dest, scaled_dest, 126, 126)
