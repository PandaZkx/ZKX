"""Récupère les données publiques d'Epic7Coach (epic7coach.com) et écrit data/coach.json.

Lancé une fois par semaine par .github/workflows/coach.yml (et à la main : python tools/coach_update.py).
Appels doux : une requête par seconde, uniquement les pages publiques que le site charge pour ses visiteurs.
Données : stats RTA de la semaine (victoires, pick, bans, ordre de pick, alliés, counters), positions,
builds RTA (sets, artefacts, stats cibles), compétences et souvenirs, liste des artefacts.
"""
import json, sys, time, urllib.request
from pathlib import Path

BASE = "https://epic7coach.com/api"
OUT = Path(__file__).resolve().parent.parent / "data" / "coach.json"
UA = {"User-Agent": "ZKX/1.0 (appli de fans Epic Seven ; +https://github.com/PandaZkx/ZKX)", "Accept": "application/json"}
MIN_SAMPLE = 30   # héros avec assez de matchs pour récupérer leur build détaillé
log = []


def get(path, tries=3):
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read().decode("utf-8"))
            time.sleep(1)
            return data
        except Exception as e:
            log.append(f"échec {path} ({e})")
            time.sleep(3 * (i + 1))
    return None


def pages(path, key):
    out, page = [], 1
    while page < 20:
        d = get(f"{path}?page={page}&limit=100")
        if not d:
            break
        out += d.get(key, [])
        meta = d.get("meta")
        if not d.get("has_more"):
            return out, meta
        page += 1
    return out, None


def r3(x):
    return round(float(x), 4) if x is not None else None


def main():
    heroes_list = get("/heroes/public-list?page=1&limit=500") or {}
    stats, meta = pages("/heroes/stats", "heroes")
    pos = (get("/heroes/position-index") or {}).get("heroes", {})
    search = (get("/heroes/public-search-index") or {}).get("heroes", {})
    arts_list = (get("/artifacts/public-list?page=1&limit=300") or {}).get("artifacts", [])
    arts_stats, _ = pages("/artifacts/stats", "artifacts")
    set_labels = get("/public-config/equip_set_labels") or {}
    if not stats or not heroes_list.get("heroes"):
        print("Données principales indisponibles : rien n'est modifié.")
        print("\n".join(log))
        return 1

    by_slug = {}
    for h in search.values():
        by_slug[h.get("slug")] = h
    H = {}
    for h in heroes_list["heroes"]:
        c = h.get("code")
        if not c:
            continue
        s = by_slug.get(h.get("slug")) or {}
        mi = (h.get("memoryImprint") or {}).get("release") or {}
        H[c] = {
            "en": h.get("name_en") or h.get("name"), "ko": h.get("name_ko"), "slug": h.get("slug"),
            "el": h.get("element") or h.get("attribute"), "cl": h.get("job") or h.get("role"), "star": h.get("star"),
            "roles": ((h.get("draft_role_profile") or {}).get("combat_roles") or []),
            "imprint": (mi.get("values") or [None])[0], "imprint_shape": mi.get("shape"),
            "skills": [{"n": k.get("nameEn"), "d": k.get("descriptionEn"), "sb": k.get("soulburn"), "t": k.get("type")} for k in (s.get("skills") or [])],
        }
    for s in stats:
        c = s.get("hero_id")
        if not c:
            continue
        e = H.setdefault(c, {})
        e.update({
            "n": s.get("sample_count"), "wr": r3(s.get("win_rate")), "pick": r3(s.get("pick_rate")),
            "preban": r3(s.get("preban_rate")), "ban": r3(s.get("final_ban_rate")),
            "early": r3(s.get("early_pick_rate")), "mid": r3(s.get("mid_pick_rate")), "late": r3(s.get("late_pick_rate")),
            "order": {k[-1]: r3(v) for k, v in (s.get("pick_order_rates") or {}).items()},
            "tag": s.get("draft_role_tag"), "joker": bool(s.get("is_joker_pick")),
            "allies": [[a["hero_id"], r3(a["rate"])] for a in (s.get("allies") or [])[:10]],
            "good": [[a["hero_id"], r3(a.get("matchup_win_rate")), r3(a.get("win_rate_lift")), a.get("enemy_count")] for a in (s.get("favorable_enemies") or [])[:10]],
            "bad": [[a["hero_id"], r3(a.get("matchup_win_rate")), r3(a.get("win_rate_drop")), a.get("enemy_count")] for a in (s.get("difficult_enemies") or [])[:10]],
        })
    for c, p in pos.items():
        if c in H:
            H[c]["pos"] = p.get("recommended_position")
            H[c]["pos_rate"] = r3(p.get("recommended_position_rate"))
    # builds détaillés des héros assez joués
    todo = [c for c, e in H.items() if (e.get("n") or 0) >= MIN_SAMPLE]
    log.append(f"builds détaillés : {len(todo)} héros")
    for c in todo:
        b = get(f"/heroes/{c}/build-summary")
        if b and b.get("heroes"):
            x = b["heroes"][0]
            H[c]["sets"] = [[s["sets"], r3(s.get("use_rate")), r3(s.get("win_rate"))] for s in (x.get("set_builds") or [])[:5]]
            H[c]["arts"] = [[a["artifact_id"], r3(a.get("use_rate")), r3(a.get("win_rate"))] for a in (x.get("artifacts") or [])[:5]]
        t = get(f"/heroes/{c}/target-stats")
        prof = (((t or {}).get("heroes") or {}).get(c) or {}).get("profiles") or []
        if prof:
            p = max(prof, key=lambda q: q.get("sampleCount") or 0)
            H[c]["target"] = {"set": [[i.get("value"), i.get("pieces")] for i in p.get("items") or []], "rate": p.get("rate"),
                              "stats": {k: [round(v.get("p25") or 0), round(v.get("median") or 0), round(v.get("p75") or 0)] for k, v in (p.get("stats") or {}).items()}}
    A = {}
    for a in arts_list:
        c = a.get("code") or a.get("artifact_id")
        A[c] = {"en": a.get("name_en"), "ko": a.get("name_ko"), "cl": a.get("class_en"), "star": a.get("grade"), "d": a.get("description_en")}
    for a in arts_stats:
        c = a.get("artifact_id") or a.get("artifact_code")
        A.setdefault(c, {}).update({"use": r3(a.get("global_use_rate")), "wr": r3(a.get("win_rate")), "n": a.get("total_count")})
    # portraits des héros qui n'ont pas d'image dans le pack partagé (nouveaux persos, 3-4★)
    root = OUT.parent.parent
    names = {h.get("code"): h.get("n") for h in json.loads((root / "tools" / "data.json").read_text(encoding="utf-8"))}
    try:
        have = set(json.loads((root / "data" / "images.json").read_text(encoding="utf-8")).get("h", {}))
    except Exception:
        have = set()
    icodir = root / "data" / "hero_icons"; icodir.mkdir(exist_ok=True)
    icons = []
    for c, e in H.items():
        f = icodir / f"{c}.png"
        if f.exists():
            icons.append(c); continue
        if (names.get(c) or e.get("en")) in have or not e.get("en"):
            continue
        for u in (f"https://epic7coach.com/images/{c}_s.png", f"https://epic7coach.com/data/images/{c}_s.png"):
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA["User-Agent"]})
                with urllib.request.urlopen(req, timeout=30) as r:
                    b = r.read()
                time.sleep(1)
                if b[:4] == b"\x89PNG" and len(b) > 500:
                    f.write_bytes(b); icons.append(c); break
            except Exception as ex:
                log.append(f"portrait {c} : {ex}")
    log.append(f"portraits ajoutés : {len(icons)}")
    out = {
        "source": "Epic7Coach (epic7coach.com)",
        "range": [meta.get("range_start"), meta.get("range_end")] if meta else None,
        "matches": meta.get("total_matches") if meta else None,
        "generated": meta.get("generated_at") if meta else None,
        "heroes": H, "arts": A,
        "sets": {k: v.get("en") for k, v in set_labels.items() if not k.startswith("set_")},
        "icons": sorted(icons),
    }
    old = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    if old.get("generated") == out["generated"] and old.get("heroes") == out["heroes"] and old.get("icons") == out["icons"]:
        print("Rien de nouveau.")
        return 0
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"coach.json : {len(H)} héros, {len(A)} artefacts, {out['matches']} matchs ({out['range']}).")
    print("\n".join(log[-20:]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
