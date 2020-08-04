import collections
import json
import os


def load_jsonl(filename):
    with open(filename) as fp:
        for line in fp:
            yield json.loads(line)


def group_data(data):
    by_phash = collections.defaultdict(list)
    for datum in data:
        if not datum["ok"]:
            continue
        by_phash[datum.get("ph")].append(datum)
    groups = []
    for phash, data in sorted(by_phash.items()):
        filenames = sorted(
            os.path.splitext(os.path.basename(datum["font"]))[0] for datum in data
        )
        # if len(filenames) > 25:
        #     print("Skipping", phash, len(filenames))
        #     continue
        groups.append({"phash": phash, "filenames": filenames, "fonts": data})
    return groups
