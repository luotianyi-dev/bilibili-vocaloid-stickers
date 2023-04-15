import os
from PIL import Image

FROM = "skindump"
DEST = "anidest"
FRAME_RATE = 24

for skin_id in os.listdir(FROM):
    try:
        skin_id = int(skin_id)
    except ValueError:
        continue
    print("Processing skin %d" % skin_id)
    for skin_file in os.listdir(os.path.join(FROM, str(skin_id))):
        if not skin_file.endswith(".svga"):
            continue
        print("    Found SVGA file %s" % skin_file)
        animate_name = skin_file[:-5]
        animate_pngs_directory = os.path.join(FROM, str(skin_id), animate_name)
        animate_pngs_name = os.listdir(animate_pngs_directory)
        animate_pngs_name = [x for x in animate_pngs_name if x.endswith(".png")]
        animate_pngs_name = [f"img_{i}.png" for i in range(len(animate_pngs_name))]
        animate_pngs_path = [os.path.join(animate_pngs_directory, x) for x in animate_pngs_name]
        print("        Found %d PNGs" % len(animate_pngs_path))
        frames = []
        for png in animate_pngs_name:
            frame = Image.open(os.path.join(animate_pngs_directory, png))
            if frame.mode != "RGBA":
                print("        Converting %s to RGBA" % png)
            frames.append(frame)
        animate_dest_directory = os.path.join(DEST, str(skin_id))
        animate_dest_path_title = os.path.join(animate_dest_directory, animate_name)
        os.makedirs(animate_dest_directory, exist_ok=True)
        frames = []
        for png in animate_pngs_name:
            frame = Image.open(os.path.join(animate_pngs_directory, png))
            frames.append(frame)
        frames[0].save(animate_dest_path_title + ".gif", format="GIF", save_all=True, append_images=frames[1:], duration=1000/FRAME_RATE, loop=0, disposal=2, optimize=False, dither=None)
        print("        Saved to %s" % animate_dest_path_title + ".gif")
