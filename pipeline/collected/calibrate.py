"""Kalibriert Modellparameter aus den Sammeldaten des ForeverDataCollector.

Liest data/collected/ForeverDataCollector.lua (als Daten) und leitet ab:
- seconds_per_kill: typische Zeit pro Kill im Spiel, inklusive Laufen zwischen den Mobs, Looten, Pausen
  (Median des Abstands zwischen aufeinanderfolgenden Kills mit XP).
- Pruefung der Kill-XP-Formel gegen die beobachteten XP (nur wenn das Mob-Level bekannt ist).

Aufruf: python -m pipeline.collected.calibrate [--write]
Mit --write entsteht pipeline/config/calibrated.json, das die Annahmen aus params.json uebersteuert.
Graue Mobs (XP = 0) zaehlen nicht mit, ihre Kill-Zeit sagt nichts ueber das Leveln aus.
"""
import argparse
import json
import statistics
from collections import defaultdict
from datetime import date
from pathlib import Path

from pipeline.collected.summarize import DEFAULT, load, lst
from pipeline.derive.derive import mob_base_xp

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "pipeline/config/calibrated.json"
MIN_KILLS = 15  # darunter ist ein Median kaum aussagekraeftig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--file", default=str(DEFAULT))
    a = ap.parse_args()
    db = load(a.file)
    kills = [k for k in lst(db.get("kills")) if isinstance(k.get("xp"), (int, float)) and k["xp"] > 0
             and isinstance(k.get("t"), (int, float))]
    kills.sort(key=lambda k: k["t"])
    print(f"Kills mit XP: {len(kills)} (Kills ohne XP, also graue Mobs, werden ignoriert)")
    result = {}

    if len(kills) >= 2:
        gaps = [b["t"] - a_["t"] for a_, b in zip(kills, kills[1:])]
        med = statistics.median(gaps)
        print(f"Abstand zwischen Kills: Median {med:.1f} s, Mittel {statistics.mean(gaps):.1f} s, "
              f"25 %-Quantil {sorted(gaps)[len(gaps)//4]:.1f} s, 75 %-Quantil {sorted(gaps)[3*len(gaps)//4]:.1f} s")
        fight = [k["combatSecs"] for k in kills if isinstance(k.get("combatSecs"), (int, float))]
        if fight:
            print(f"Kampfdauer: Median {statistics.median(fight):.1f} s (n={len(fight)})")
        if len(kills) >= MIN_KILLS:
            result["seconds_per_kill"] = round(med, 1)
        else:
            print(f"Zu wenige Kills fuer eine belastbare Kalibrierung (mindestens {MIN_KILLS}).")

    # Kill-XP-Formel pruefen
    ratios, by_diff = [], defaultdict(list)
    for k in kills:
        pl, ml = k.get("level"), k.get("mobLevel")
        if isinstance(pl, int) and isinstance(ml, int):
            exp = mob_base_xp(pl, ml)
            if exp > 0:
                ratios.append(k["xp"] / exp)
                by_diff[ml - pl].append(k["xp"] / exp)
    if ratios:
        print(f"Kill-XP beobachtet / Formel: Median {statistics.median(ratios):.2f} (n={len(ratios)}); "
              + ", ".join(f"Level-Diff {d:+d}: {statistics.median(v):.2f} (n={len(v)})" for d, v in sorted(by_diff.items())))
    else:
        print("Keine Kills mit bekanntem Mob-Level, die Kill-XP-Formel kann nicht geprueft werden "
              "(Ziel anvisieren, bevor man es toetet).")

    if a.write and result:
        result["_hinweis"] = f"Aus Spieldaten abgeleitet am {date.today().isoformat()} (n={len(kills)} Kills). Uebersteuert params.json."
        OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
        print("Geschrieben:", OUT, result)
    elif a.write:
        print("Nichts geschrieben: keine belastbaren Werte.")


if __name__ == "__main__":
    main()
