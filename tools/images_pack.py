"""Construit data/images.json (images partagées) à partir d'un dossier contenant heroes/ et artifacts/.
Usage : python tools/images_pack.py <dossier>
Les noms de fichiers sont reconnus comme dans l'appli : nom EN/FR du perso ou de l'artefact, clé ou code (c1144).
"""
import base64, hashlib, io, json, re, sys, unicodedata
from pathlib import Path
from PIL import Image

T = Path(__file__).resolve().parent
DATA = json.loads((T / "data.json").read_text(encoding="utf-8"))
ARTS = json.loads((T / "arts.json").read_text(encoding="utf-8"))


def nrm(s):
    s = unicodedata.normalize("NFD", str(s))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]", "", s.lower())


HN, AN = {}, {}
for h in DATA:
    for v in (h["n"], h.get("fr"), h.get("key"), h.get("code")):
        if v and nrm(v) not in HN:
            HN[nrm(v)] = h["n"]
# héros ajoutés par les données Epic7Coach (mêmes règles que l'appli)
_cf = T.parent / "data" / "coach.json"
if _cf.exists():
    _codes = {h.get("code") for h in DATA}
    for _c, _x in json.loads(_cf.read_text(encoding="utf-8")).get("heroes", {}).items():
        if _c not in _codes and _x.get("en") and ((_x.get("star") or 0) >= 5 or (_x.get("n") or 0) >= 30):
            HN.setdefault(nrm(_x["en"]), _x["en"])
for n, a in ARTS.items():
    AN[nrm(n)] = a["key"]
    AN[nrm(a["key"])] = a["key"]


def small(path, S, crop_top):
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    s = min(w, h)
    box = ((w - s) // 2, 0 if crop_top else (h - s) // 2, (w - s) // 2 + s, (0 if crop_top else (h - s) // 2) + s)
    im = im.crop(box).resize((S, S), Image.LANCZOS)
    buf = io.BytesIO()
    im.save(buf, "WEBP", quality=82, method=6)
    return "data:image/webp;base64," + base64.b64encode(buf.getvalue()).decode()


def neon(im):
    """Couleur vive dominante (pour la bordure néon)."""
    import colorsys
    sm = im.convert("RGB").resize((40, 64))
    buckets = {}
    for r, g, b in sm.getdata():
        h, sat, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        if sat < .35 or v < .35:
            continue
        k = int(h * 24) % 24
        buckets[k] = buckets.get(k, 0) + sat * v
    if not buckets:
        return None
    k = max(buckets, key=buckets.get)
    r, g, b = colorsys.hsv_to_rgb((k + .5) / 24, .78, 1)
    return "#%02x%02x%02x" % (int(r * 255), int(g * 255), int(b * 255))


def arts_big(src):
    """data/art/<clé>.webp en grand (fond des affiches) + data/art/colors.json."""
    dst = T.parent / "data" / "art"
    dst.mkdir(parents=True, exist_ok=True)
    colors = {}
    for f in sorted((src / "artifacts").glob("*")):
        k = AN.get(nrm(f.stem)) or re.sub(r"[^a-z0-9]+", "_", f.stem.lower()).strip("_")
        im = Image.open(f).convert("RGBA")
        im.thumbnail((300, 476), Image.LANCZOS)
        im.save(dst / f"{k}.webp", "WEBP", quality=80, method=6)
        c = neon(im)
        if c:
            colors[k] = c
    (dst / "colors.json").write_text(json.dumps(colors, sort_keys=True), encoding="utf-8")
    print("affiches :", len(colors), "artefacts en grand")


def main(src):
    src = Path(src)
    if "--arts" in sys.argv or not (T.parent / "data" / "art" / "colors.json").exists():
        arts_big(src)
    out, miss = {"h": {}, "a": {}}, {"h": [], "a": []}
    for f in sorted((src / "heroes").glob("*")):
        k = HN.get(nrm(f.stem)) or HN.get(nrm(f.stem.replace("-and-", "-")))
        if k:
            out["h"][k] = small(f, 128, False)
        else:
            miss["h"].append(f.name)
    for f in sorted((src / "artifacts").glob("*")):
        # artefacts inconnus de arts.json : même clé que artKey() dans l'appli
        k = AN.get(nrm(f.stem)) or re.sub(r"[^a-z0-9]+", "_", f.stem.lower()).strip("_")
        out["a"][k] = small(f, 112, True)
    blob = json.dumps(out, sort_keys=True)
    out["v"] = hashlib.sha1(blob.encode()).hexdigest()[:12]
    (T.parent / "data" / "images.json").write_text(json.dumps(out, separators=(",", ":")), encoding="utf-8")
    (T.parent / "data" / "images_v.json").write_text(json.dumps({"v": out["v"], "h": len(out["h"]), "a": len(out["a"])}), encoding="utf-8")
    have = set(out["h"])
    print(f"persos : {len(out['h'])}/{len(DATA)} · artefacts : {len(out['a'])}")
    print("persos de ZKX sans image :", [h["n"] for h in DATA if h["n"] not in have])
    print("fichiers non reconnus :", len(miss["h"]), "persos,", len(miss["a"]), "artefacts")
    return miss


if __name__ == "__main__":
    m = main(next((a for a in sys.argv[1:] if not a.startswith("--")), "."))
    print("ex. non reconnus :", m["h"][:40], m["a"][:20])
