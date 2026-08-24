"""Minimal YAML subset loader - enough for the section outline, no dependency."""
def load(text):
    out, cur_list, cur_item = {}, None, None
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip())
        line = raw.strip()
        if indent == 0 and line.endswith(":"):
            cur_list = []
            out[line[:-1]] = cur_list
            cur_item = None
        elif indent == 0 and ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
            cur_list = None
        elif line.startswith("- "):
            cur_item = {}
            cur_list.append(cur_item)
            k, v = line[2:].split(":", 1)
            cur_item[k.strip()] = v.strip()
        elif cur_item is not None and ":" in line:
            k, v = line.split(":", 1)
            cur_item[k.strip()] = v.strip()
    return out
