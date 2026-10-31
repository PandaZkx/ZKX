"""Met à jour data/banners.json à partir des annonces Epic Seven (miroir epic7db.com/news).

Lancé toutes les 6 h par .github/workflows/banners.yml. Utilisable à la main : python tools/banners_update.py
Les entrées marquées "manual": true (ajoutées à la main) ne sont jamais modifiées.
Le journal du dernier passage est écrit dans data/banners_log.txt.
"""
import html, json, re, sys, time, urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FILE = ROOT / "data" / "banners.json"
LOG = ROOT / "data" / "banners_log.txt"
BASE = "https://epic7db.com"
UA = {"User-Agent": "Mozilla/5.0 (ZKX banner bot; +https://github.com/PandaZkx/ZKX)"}
NOW = datetime.now(timezone.utc)
MONTHS = {m: i + 1 for i, m in enumerate("january february march april may june july august september october november december".split())}
RELEVANT = re.compile(r"drop-rate-up|update-content|limited|mystic|collab|class-summon|summon", re.I)
log_lines = []


def log(*a):
    s = " ".join(str(x) for x in a)
    log_lines.append(s)
    print(s)


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def to_text(h):
    h = re.sub(r"(?is)<(script|style|noscript)[^>]*>.*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</(p|div|li|td|tr|h\d|section|article|table)>", "\n", h)
    h = re.sub(r"(?s)<[^>]+>", " ", h)
    h = html.unescape(h).replace("\xa0", " ").replace("★", "★")
    lines = [re.sub(r"[ \t]+", " ", x).strip() for x in h.split("\n")]
    return "\n".join(x for x in lines if x)


def list_slugs():
    slugs = []
    for url in (BASE + "/news", BASE + "/news?page=2"):
        try:
            h = get(url)
        except Exception as e:
            log("liste", url, "échec :", e)
            continue
        for s in re.findall(r'href="(?:https?://(?:www\.)?epic7db\.com)?/news/([a-z0-9][a-z0-9\-]*)/?"', h):
            if s not in slugs:
                slugs.append(s)
        time.sleep(1)
    if not slugs:
        try:
            x = get(BASE + "/sitemap.xml")
            found = re.findall(r"<loc>\s*https?://(?:www\.)?epic7db\.com/news/([a-z0-9][a-z0-9\-]*)/?\s*</loc>(?:\s*<lastmod>([^<]+)</lastmod>)?", x)
            found.sort(key=lambda t: t[1], reverse=True)
            slugs = [s for s, _ in found][:60]
            log("sitemap :", len(slugs), "articles")
        except Exception as e:
            log("sitemap échec :", e)
    log("articles trouvés :", len(slugs), slugs[:40])
    return slugs


def article_date(raw, text):
    m = re.search(r'datetime="(\d{4})-(\d{2})-(\d{2})', raw)
    if m:
        return datetime(int(m[1]), int(m[2]), int(m[3]), tzinfo=timezone.utc)
    m = re.search(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),\s+(\d{4})", text)
    if m:
        return datetime(int(m[3]), MONTHS[m[1].lower()], int(m[2]), tzinfo=timezone.utc)
    return NOW


SCHED = re.compile(
    r"(\d{1,2})/(\d{1,2})\s*\(\w{3}\)\s*(after the maintenance|(\d{1,2}):(\d{2}))?\s*(?:UTC)?\s*[–—\-~]+\s*"
    r"(?:(\d{4})/)?(\d{1,2})/(\d{1,2})\s*\(\w{3}\)\s*(\d{1,2}):(\d{2})", re.I)


def parse_sched(seg, ref):
    m = SCHED.search(seg)
    if not m:
        return None
    sm, sd = int(m[1]), int(m[2])
    sy = ref.year + (1 if sm < ref.month - 6 else 0) - (1 if sm > ref.month + 6 else 0)
    sh, smin = (int(m[4]), int(m[5])) if m[4] else (3, 0)
    em, ed = int(m[7]), int(m[8])
    ey = int(m[6]) if m[6] else sy + (1 if em < sm else 0)
    try:
        st = datetime(sy, sm, sd, sh, smin, tzinfo=timezone.utc)
        en = datetime(ey, em, ed, int(m[9]), int(m[10]), tzinfo=timezone.utc)
    except ValueError:
        return None
    return st, en


def clean_name(s):
    s = re.sub(r"^\s*\d\s*★?\s+(?=[A-Z])", "", s.strip())
    s = re.sub(r"\s*[!.]+$", "", s)
    return s.strip(" -:\"'")


def parse_dru(title):
    t = re.sub(r"^\[[^\]]*\]\s*", "", title).strip().rstrip("!")
    m = re.match(r"^(.+?)\s+Class Summon\s*(?:&|and)\s*(.+?)\s+(?:Limited\s+)?(?:Summon\s+)?Drop Rate Up", t, re.I)
    if m:
        cls = {"knight": "Chevalier", "warrior": "Guerrier", "thief": "Voleur", "ranger": "Ranger", "mage": "Mage", "soul weaver": "Tisseur d'âmes"}.get(m[1].strip().lower(), clean_name(m[1]))
        return {"kind": "class", "hero": None, "art": clean_name(m[2]), "title": "Invocation de classe : " + cls}
    m = re.match(r"^(.+?)\s+&\s+(.+?)\s+(Limited\s+)?(?:Summon\s+)?Drop Rate Up", t, re.I) or \
        re.match(r"^(.+?)\s+and\s+(.+?)\s+(Limited\s+)?(?:Summon\s+)?Drop Rate Up", t, re.I)
    if m:
        return {"kind": "limited" if m[3] else "rateup", "hero": clean_name(m[1]), "art": clean_name(m[2])}
    return None


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")


def from_article(slug, raw):
    text = to_text(raw)
    ref = article_date(raw, text)
    mt = re.search(r"(?is)<h1[^>]*>(.*?)</h1>", raw) or re.search(r"(?is)<title>(.*?)</title>", raw)
    title = to_text(mt[1]).split("|")[0].strip() if mt else slug.replace("-", " ")
    out = []

    def add(b, seg):
        sc = parse_sched(seg, ref)
        if not sc:
            log("  pas de dates pour", b)
            return
        b["start"], b["end"] = sc[0].strftime("%Y-%m-%dT%H:%M:%SZ"), sc[1].strftime("%Y-%m-%dT%H:%M:%SZ")
        head = text[:2500].lower()
        if b["kind"] in ("rateup", "limited") and ("collaboration" in head or "collab" in title.lower()):
            b["kind"] = "collab"
        elif b["kind"] == "rateup" and re.search(r"only obtain[^.]{0,80}from this limited", head):
            b["kind"] = "limited"
        b["src"] = BASE + "/news/" + slug
        out.append(b)

    d = parse_dru(title)
    if d:
        i = text.find("Schedule")
        add(d, text[i:] if i >= 0 else text)
    lines = text.split("\n")
    pos = 0
    for ln in lines:
        p = text.find(ln, pos)
        pos = p + len(ln) if p >= 0 else pos
        seg = text[pos:pos + 1800]
        m = re.match(r"^\d+\.\s*(.+?Drop Rate Up)\s*!?$", ln, re.I)
        if m and not d:
            x = parse_dru(m[1])
            if x:
                add(x, seg)
            continue
        m = re.match(r"^(.+?)\s+Mystic Summon Schedule\s*$", ln, re.I)
        if m:
            add({"kind": "mystic", "hero": clean_name(m[1]), "art": None}, seg)
            continue
        if re.match(r"^\d+\.\s*Special\s*★?\s*Mystic Summon", ln, re.I):
            add({"kind": "special-mystic", "hero": None, "art": None, "title": "Mystique spéciale",
                 "note": "Tu choisis le Moonlight 4★/5★ à viser parmi ceux sortis il y a plus de 6 mois."}, seg)
            continue
        if re.match(r"^\d+\.\s*Mystic Summon Lineup Rotation", ln, re.I):
            sc = SCHED.search(seg)
            if sc:
                after = seg[sc.end():].split("\n")
                name = next((a.strip() for a in after[1:15] if a.strip() and not re.fullmatch(r"[\d★\s]+", a.strip())
                             and not re.match(r"^(\d+\.|■|\*|Schedule|Hero|Grade)", a.strip()) and 2 < len(a.strip()) < 45), None)
                if name:
                    add({"kind": "mystic", "hero": clean_name(name), "art": None}, seg)
            continue
    m = re.search(r"new limited 5\s*★?\s*Hero,\s*([^,]+),\s*through the Limited Summon", text, re.I)
    if m and not any(b["kind"] in ("limited", "collab") for b in out):
        i = m.end()
        add({"kind": "limited", "hero": clean_name(m[1]), "art": None}, text[i:i + 1800])
    return title, out


def same(a, b):
    if a.get("kind") != b.get("kind") and not ({a.get("kind"), b.get("kind")} <= {"rateup", "limited", "collab"}):
        return False
    if slugify(a.get("hero")) != slugify(b.get("hero")) or (not a.get("hero") and slugify(a.get("art")) != slugify(b.get("art"))):
        return False
    try:
        da = datetime.fromisoformat(a["start"].replace("Z", "+00:00"))
        db = datetime.fromisoformat(b["start"].replace("Z", "+00:00"))
    except Exception:
        return False
    return abs((da - db).days) <= 4


def main():
    data = json.loads(FILE.read_text(encoding="utf-8"))
    banners, seen = data.get("banners", []), set(data.get("seen", []))
    before = json.dumps(banners, sort_keys=True)
    slugs = [s for s in list_slugs() if RELEVANT.search(s)]
    todo = [s for s in slugs if s not in seen][:25]
    log("articles à lire :", len(todo))
    for slug in todo:
        try:
            raw = get(BASE + "/news/" + slug)
        except Exception as e:
            log("  échec", slug, e)
            continue
        title, found = from_article(slug, raw)
        seen.add(slug)
        log("-", slug, "|", title, "->", [(b["kind"], b.get("hero"), b.get("art"), b["start"][:10], b["end"][:10]) for b in found])
        for b in found:
            if datetime.fromisoformat(b["end"].replace("Z", "+00:00")) < NOW - timedelta(days=30):
                continue
            old = next((x for x in banners if same(x, b)), None)
            if old:
                if not old.get("manual"):
                    for k in ("start", "end", "art", "kind", "src", "title", "note"):
                        if b.get(k):
                            old[k] = b[k]
                continue
            b["id"] = f'{b["kind"]}-{slugify(b.get("hero") or b.get("art") or b.get("title"))}-{b["start"][:10].replace("-", "")}'
            b.setdefault("note", "")
            banners.append(b)
            log("  + ajoutée :", b["id"])
        time.sleep(1)
    keep = []
    for b in banners:
        if b.get("perm") or not b.get("end"):
            keep.append(b)
            continue
        if datetime.fromisoformat(b["end"].replace("Z", "+00:00")) > NOW - timedelta(days=45):
            keep.append(b)
    # une mystique sans date de fin se termine quand la suivante commence
    myst = sorted([b for b in keep if b.get("kind") == "mystic"], key=lambda b: b["start"])
    for a, b in zip(myst, myst[1:]):
        if not a.get("end"):
            a["end"] = b["start"]
    data["banners"] = keep
    data["seen"] = sorted(seen)[-400:]
    changed = json.dumps(keep, sort_keys=True) != before
    if changed:
        data["updated"] = NOW.strftime("%Y-%m-%dT%H:%M:%SZ")
    FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    log("bannières :", len(keep), "| changement :", changed)
    LOG.write_text(NOW.isoformat() + "\n" + "\n".join(log_lines) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
