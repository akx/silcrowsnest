import jinja2

from sillib import load_jsonl, group_data


def main():
    data = list(load_jsonl("s-1596527291.086862.jsonl"))
    groups = group_data(data)

    j2e = jinja2.Environment(
        autoescape=True, loader=jinja2.FileSystemLoader("./templates")
    )
    for page_name in ("names.html", "concise.html"):
        tem = j2e.get_template(page_name)
        html = tem.render({"groups": groups})
        with open("html/" + page_name, "w") as outf:
            outf.write(html)


if __name__ == "__main__":
    main()
