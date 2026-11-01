"""Assemble app/index.html depuis le gabarit et les données. Usage : python tools/build.py"""
from pathlib import Path
T = Path(__file__).parent
t = (T / "template.html").read_text(encoding="utf-8")
t = t.replace("__JSZIP__", "<script>" + (T / "jszip.min.js").read_text(encoding="utf-8") + "</script>", 1)
for k, f in (("__DATA__", "data.json"), ("__META__", "meta.json"), ("__ARTS__", "arts.json"), ("__ARTFR__", "arts_fr.json")):
    t = t.replace(k, (T / f).read_text(encoding="utf-8"), 1)
cf = T.parent / "data" / "coach.json"
t = t.replace("__COACH__", cf.read_text(encoding="utf-8") if cf.exists() else "null", 1)
t = t.replace("__BANNERS__", (T.parent / "data" / "banners.json").read_text(encoding="utf-8"), 1)
(T.parent / "app" / "index.html").write_text(t, encoding="utf-8")
print("app/index.html OK")
