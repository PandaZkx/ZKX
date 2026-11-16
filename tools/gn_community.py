"""Ajoute un build Go Next! envoyé par issue GitHub (label build-ok) dans data/gonext_community.json.
Usage (Action) : python tools/gn_community.py  (lit ISSUE_BODY, ISSUE_URL, ISSUE_USER dans l'environnement)"""
import base64, json, os, re, sys, datetime
from pathlib import Path
body = os.environ.get("ISSUE_BODY", "")
m = re.search(r"GN1\.([A-Za-z0-9+/=]+)", body)
if not m:
    print("Pas de code GN1 dans l'issue."); sys.exit(1)
o = json.loads(base64.b64decode(m.group(1)).decode("utf-8"))
if o.get("k") != "b":
    print("Le code n'est pas un build."); sys.exit(1)
b = o["b"]
data = json.loads((Path(__file__).parent.parent / "data" / "gonext.json").read_text(encoding="utf-8"))
ids = {k: {x["id"] for x in data[k]} for k in ("characters", "weapons", "items")}
clean = lambda s, n=60: re.sub(r"[<>]", "", str(s or ""))[:n]
build = {
    "name": clean(b.get("name"), 60) or "Build top 1",
    "char": b.get("char") if b.get("char") in ids["characters"] else "",
    "weapons": [w if w in ids["weapons"] else "" for w in (b.get("weapons") or [])][:4],
    "items": [i for i in (b.get("items") or []) if i in ids["items"]][:8],
    "stats": [s for s in (b.get("stats") or []) if s in data["stats"]][:6],
    "player": clean(b.get("player"), 40), "rank": clean(b.get("rank"), 60),
    "source": os.environ.get("ISSUE_URL", ""), "by": os.environ.get("ISSUE_USER", ""),
    "date": datetime.date.today().isoformat(),
}
if not build["char"] or len([w for w in build["weapons"] if w]) < 2:
    print("Build incomplet."); sys.exit(1)
f = Path(__file__).parent.parent / "data" / "gonext_community.json"
lst = json.loads(f.read_text(encoding="utf-8")) if f.exists() else []
lst = [x for x in lst if x.get("source") != build["source"]]
lst.insert(0, build)
f.write_text(json.dumps(lst[:200], ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("Ajouté :", build["name"])
