"""Liest die SavedVariables-Datei des ForeverDataCollector als DATEN (wird nicht ausgefuehrt) und fasst sie zusammen.

Aufruf: python -m pipeline.collected.summarize [Pfad]
Standard: data/collected/ForeverDataCollector.lua
"""
import statistics
import sys
from collections import Counter
from pathlib import Path

from pipeline.common.luatable import LuaParser

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "data/collected/ForeverDataCollector.lua"


def load(path):
    text = Path(path).read_text(encoding="utf-8")
    i = text.index("ForeverDataCollectorDB")
    j = text.index("{", i)
    p = LuaParser(text)
    p.i = j
    return p.parse_table()


def lst(t):
    """Lua-Positionsliste -> Python-Liste"""
    if not isinstance(t, dict):
        return []
    return [t[k] for k in sorted(t) if isinstance(k, int)]


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT
    db = load(path)
    print("Version des Sammel-Add-ons:", db.get("version"))
    for s in lst(db.get("sessions")):
        print("Sitzung:", {k: s.get(k) for k in ("startedAt", "gameVersion", "build")}, "Spieler:", s.get("player"))
    quests = db.get("quests") or {}
    kills, loots, samples, timeline = (lst(db.get(k)) for k in ("kills", "loots", "samples", "timeline"))
    print(f"\nQuests: {len(quests)} | Kills: {len(kills)} | Loot-Eintraege: {len(loots)} | Positionsproben: {len(samples)} | Zeitleiste: {len(timeline)}")
    print("XP-Kurve (Level -> XP bis zum naechsten):", dict(sorted((db.get("xpcurve") or {}).items())))
    notes = lst(db.get("notes"))
    if notes:
        print("Notizen:", [(n.get("level"), n.get("text")) for n in notes])

    # Quests mit XP-Angaben
    shown = [(q.get("title"), q.get("xpShown"), q.get("xpOnTurnInDialog"), q.get("xpInLog"), q.get("xpTurnedIn"))
             for q in quests.values()]
    with_xp = [x for x in shown if any(isinstance(v, (int, float)) and v > 0 for v in x[1:])]
    print(f"\nQuests mit XP-Angabe: {len(with_xp)} von {len(quests)}")
    for t, a, b, c, d in with_xp[:15]:
        print(f"  {str(t)[:36]:36s} Dialog {a} | Abgabe-Dialog {b} | im Log {c} | abgegeben {d}")

    # Kills
    if kills:
        lv = Counter((k.get("level"), k.get("mobLevel")) for k in kills)
        print("\nKills nach (Spielerlevel, Moblevel):", dict(lv.most_common(8)))
        by_mob = Counter(k.get("mob") for k in kills)
        print("Häufigste Mobs:", by_mob.most_common(6))
        cs = [k["combatSecs"] for k in kills if isinstance(k.get("combatSecs"), (int, float))]
        gaps = [k["sinceLast"] for k in kills if isinstance(k.get("sinceLast"), (int, float)) and k["sinceLast"] < 120]
        if cs:
            print(f"Kampfdauer: Median {statistics.median(cs):.1f}s, Mittel {statistics.mean(cs):.1f}s (n={len(cs)})")
        if gaps:
            print(f"Abstand zwischen Kills (<120s): Median {statistics.median(gaps):.1f}s (n={len(gaps)})")

    # Kampfabschnitte (ersetzen das Kampflog)
    combats = lst(db.get("combats"))
    if combats:
        secs = [c["secs"] for c in combats if isinstance(c.get("secs"), (int, float))]
        if secs:
            print(f"\nKampfabschnitte: {len(combats)}; Dauer Median {statistics.median(secs):.1f}s, Mittel {statistics.mean(secs):.1f}s")
        else:
            print(f"\nKampfabschnitte: {len(combats)}")
        print("Ziele:", Counter(c.get("mob") for c in combats).most_common(5))

    # Bewegung
    if samples:
        sp = Counter(s.get("speed") for s in samples)
        print("\nGeschwindigkeiten (yd/s) und Anzahl:", dict(sp.most_common(6)))
        print("Davon beritten:", sum(1 for s in samples if s.get("mounted")))
        maps = Counter(s.get("map") for s in samples)
        print("Karten-IDs:", dict(maps.most_common(5)))


if __name__ == "__main__":
    main()
