"""Diagnostic : visite epic7coach.com avec un navigateur et enregistre les réponses JSON (pour voir les données disponibles)."""
import json, re, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
OUT = Path("data/_src/coach2"); OUT.mkdir(parents=True, exist_ok=True)
log = []
saved = {}
def on_resp(r):
    try:
        ct = r.headers.get("content-type", "")
        u = r.url
        log.append(f"{r.status} {ct[:30]} {u}")
        if "json" in ct and r.status == 200:
            b = r.body()
            name = re.sub(r"[^a-zA-Z0-9]+", "_", u.split("//", 1)[-1])[:150] + ".json"
            if len(saved) < 300:
                (OUT / name).write_bytes(b); saved[u] = len(b)
    except Exception as e:
        log.append(f"ERR {e}")
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.on("response", on_resp)
    pg.goto("https://epic7coach.com/", wait_until="networkidle", timeout=90000)
    pg.wait_for_timeout(4000)
    (OUT / "home.html").write_text(pg.content(), encoding="utf-8")
    (OUT / "home.txt").write_text(pg.inner_text("body"), encoding="utf-8")
    links = sorted(set(pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")))
    (OUT / "links.txt").write_text("\n".join(links), encoding="utf-8")
    # visite quelques pages internes
    inner = ["https://epic7coach.com/heroes/c1144", "https://epic7coach.com/heroes/c5154"]
    for l in inner:
        try:
            pg.goto(l, wait_until="networkidle", timeout=60000); pg.wait_for_timeout(2500)
            slug = re.sub(r"[^a-zA-Z0-9]+", "_", l.split("epic7coach.com", 1)[-1]) or "root"
            (OUT / f"page{slug}.txt").write_text(pg.inner_text("body")[:20000], encoding="utf-8")
            more = pg.eval_on_selector_all("a[href]", "els => els.map(e => e.href)")
            links += [m for m in more if m not in links]
        except Exception as e:
            log.append(f"ERR page {l} {e}")
    (OUT / "links_all.txt").write_text("\n".join(sorted(set(links))), encoding="utf-8")
    b.close()
(OUT / "network.txt").write_text("\n".join(log), encoding="utf-8")
(OUT / "saved.json").write_text(json.dumps(saved, indent=1), encoding="utf-8")
print(len(log), "réponses,", len(saved), "JSON")
