import io
import json
import multiprocessing
import os
import pathlib
import itertools
import threading
import time
from collections import Counter
from typing import Optional

import imagehash
import tqdm
from PIL import Image, ImageFont, ImageDraw, ImageChops

TEXT = "§"

ph_dir = pathlib.Path("images/ph")
dh_dir = pathlib.Path("images/dh")
f_dir = pathlib.Path("images/f")


def determine_size(font_file, text, size, target_height):
    font_size = size
    font = font_w = font_h = None
    for attempt in range(10):
        font = ImageFont.truetype(font_file, int(font_size))
        font_w, font_h = font.getsize(text)
        if font_w <= 10 or font_h <= 10:
            return None
        # print(font_file, font_size, font_w, font_h)
        if font_w > size or font_h > size:
            font_size *= 0.95
        elif font_h < target_height:
            font_size /= font_h / target_height
        else:
            break
    return (font, font_w, font_h)


def render_text(font_file, text, size=500) -> Optional[Image.Image]:
    font_fwh = determine_size(font_file, text, size, target_height=size * 0.9)
    if not font_fwh:
        return None
    font, font_w, font_h = font_fwh
    img = Image.new("RGB", (size, size), color="white")
    draw = ImageDraw.Draw(img)
    x = (size - font_w) / 2
    y = (size - font_h) / 2 - 5
    draw.text((x, y), text, font=font, fill="black")
    bbox = ImageChops.invert(img).getbbox()
    if not bbox:
        return None
    return img.crop(bbox).convert("L")


def process_font(font_file):
    font_file = str(font_file)
    try:
        im = render_text(font_file, TEXT)
    except Exception as exc:
        return {"font": font_file, "ok": False, "error": str(exc)}
    png_name = f"{os.path.basename(font_file)}.png"
    if im:
        ph = str(imagehash.phash(im))
        dh = str(imagehash.dhash(im))
        bio = io.BytesIO()
        im.save(bio, format="PNG")
        for pth in (
            ph_dir / f"{ph}.png",
            # dh_dir / f"{dh}.png",
            # f_dir / png_name
        ):
            pth.write_bytes(bio.getvalue())
        return {"font": font_file, "ok": True, "ph": ph, "dh": dh, "png": png_name}
    return {"font": font_file, "ok": False}


def main():
    for directory in (ph_dir, dh_dir, f_dir):
        directory.mkdir(parents=True, exist_ok=True)
    fonts_root = pathlib.Path("/Users/akx/Resources/fonts")
    fonts = set(itertools.chain(fonts_root.rglob("*.otf"), fonts_root.rglob("*.ttf")))
    filename = f"s-{time.time()}.jsonl"
    with multiprocessing.Pool() as p:
        with open(filename, "w") as outf:
            for i, result in enumerate(
                tqdm.tqdm(
                    p.imap_unordered(process_font, fonts, chunksize=25),
                    total=len(fonts),
                )
            ):
                print(json.dumps(result), file=outf)


if __name__ == "__main__":
    main()
