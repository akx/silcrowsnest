import io

import tqdm
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas

from sillib import load_jsonl, group_data


def main():
    data = list(load_jsonl("s-1596527291.086862.jsonl"))
    groups = group_data(data)
    bio = io.BytesIO()
    doc = Canvas(bio, pagesize=A4)
    dw, dh = doc._pagesize
    margin = 7.5 * mm
    n_x = 8
    n_y = int(n_x * 1.618)
    per_page = n_x * n_y
    x_size = (dw - margin * 2) / n_x
    y_size = (dh - margin * 2) / n_y
    box_size = min(x_size, y_size)
    image_size = box_size - 5 * mm
    n_pages = 0
    # groups.sort(key=lambda g: len(g["filenames"]), reverse=True)
    with tqdm.tqdm(groups) as prog:
        for total_i, group in enumerate(prog):
            page_i = total_i % per_page
            gy, gx = divmod(page_i, n_x)
            if not (gx or gy):  # first item of a page
                n_pages += 1
                prog.set_description(f"page {n_pages}")
                if total_i:
                    doc.showPage()
                doc.setFont("Helvetica", 6.5)
            corner_x = margin + x_size * gx
            corner_y = margin + y_size * (n_y - 1 - gy)
            mid_x = corner_x + box_size / 2
            mid_y = corner_y + box_size / 2
            # doc.rect(corner_x, corner_y, box_size, box_size)
            ph = group["phash"]
            doc.drawImage(
                f"images/ph/{ph}.png",
                mid_x,
                mid_y + 2 * mm,
                image_size,
                image_size,
                anchorAtXY=True,
                preserveAspectRatio=True,
            )
            doc.drawCentredString(
                mid_x, corner_y + 1 * mm, f'{ph} ({len(group["filenames"])})'
            )
    doc.save()
    with open("silcrowsnest.pdf", "wb") as outf:
        outf.write(bio.getvalue())


if __name__ == "__main__":
    main()
