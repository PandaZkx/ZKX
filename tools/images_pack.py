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


def main(src):
    src = Path(src)
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
    m = main(sys.argv[1] if len(sys.argv) > 1 else ".")
    print("ex. non reconnus :", m["h"][:40], m["a"][:20])
