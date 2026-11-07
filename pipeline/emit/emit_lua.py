"""Stufe 6: Ausgeben. Erzeugt die Lua-Plandatei fuer das Add-on aus dem Plan des Routenplaners.

Ausgabe: addon/ForeverLeveler/Plan.lua (Tabelle ForeverLevelerPlan) und data/reports/plan_emit.md.
Aufruf: python -m pipeline.emit.emit_lua [--target-level 10] [--beam 150]

Hinweis zur Sicherheit: Alle Texte stammen aus Fremddaten und werden vollstaendig als Lua-Strings
maskiert (Anfuehrungszeichen, Backslash, Steuerzeichen), damit die erzeugte Datei nur Daten enthaelt.
"""
import argparse
import datetime
from pathlib import Path

from pipeline.derive.derive import load, yards
from pipeline.derive.planner import EPS, World, plan_refined, trace
from pipeline.derive.route import qxp_at

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "addon/ForeverLeveler/Plan.lua"
MAP_ID = 1429  # UiMap Elwynn Forest (Forever-Build 1.60.1.70862, UiMapAssignment)
ZONE = 12


def lua_str(s):
    out = ['"']
    for ch in str(s):
        o = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == "\\":
            out.append("\\\\")
        elif ch == "\n":
            out.append("\\n")
        elif o < 32 or o == 127:
            out.append("\\%d" % o)
        else:
            out.append(ch)
    out.append('"')
    return "".join(out)


def lua_val(v, indent=0):
    pad = "  " * indent
    if v is None:
        return "nil"
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, (int, float)):
        return repr(round(v, 2)) if isinstance(v, float) else str(v)
    if isinstance(v, str):
        return lua_str(v)
    if isinstance(v, (list, tuple)):
        if not v:
            return "{}"
        inner = ",\n".join(pad + "  " + lua_val(x, indent + 1) for x in v)
        return "{\n" + inner + "\n" + pad + "}"
    if isinstance(v, dict):
        inner = ",\n".join(f"{pad}  [{lua_str(k)}] = {lua_val(x, indent + 1)}" if not str(k).isidentifier()
                           else f"{pad}  {k} = {lua_val(x, indent + 1)}" for k, x in v.items())
        return "{\n" + inner + "\n" + pad + "}"
    raise TypeError(type(v))


def npc_name(w, ids, objects):
    for i in ids:
        n = w.npcs.get(str(i))
        if n:
            return n["name"]
    for i in ids:
        o = objects.get(str(i))
        if o:
            return o["name"]
    return None


def build_steps(w, end, objects):
    steps = []
    states = trace(end)[1:]
    for idx, s in enumerate(states):
        typ, qid, dt, events, kills_main, endpos, mode = s.rec
        parent = s.parent
        hint = ""
        if events:
            hint = "unterwegs: " + ", ".join(f"{w.npcs[str(m)]['name']} x{h:.0f}" for m, h in events)
        e = {"type": typ, "map": MAP_ID, "minute": round(s.t / 60, 1), "level": s.level, "hint": hint}
        if mode != "walk":
            e["via"] = mode  # Weg mit Ruhestein/Flug statt zu Fuss
        if typ == "accept":
            q = w.q[qid]
            nd = w.need[qid]
            e.update(quest=qid, name=q["name"], x=round(nd["giver"][0], 2), y=round(nd["giver"][1], 2),
                     npc=npc_name(w, q["started_by"]["npc"], objects) or npc_name(w, q["started_by"]["object"], objects),
                     qlevel=q["quest_level"])
        elif typ == "turnin":
            q = w.q[qid]
            nd = w.need[qid]
            dest = nd["ender"] or nd["giver"]
            e.update(quest=qid, name=q["name"], x=round(dest[0], 2), y=round(dest[1], 2),
                     npc=npc_name(w, q["finished_by"]["npc"], objects) or npc_name(w, q["finished_by"]["object"], objects),
                     xp=round(qxp_at(q, parent.level, w.table, w.est_tier)))
        elif typ == "misc":
            q = w.q[qid]
            e.update(quest=qid, name=q["name"], x=round(endpos[0], 2), y=round(endpos[1], 2))
        elif typ in ("sethome", "errand", "discover"):
            e.update(name=s.act, x=round(endpos[0], 2), y=round(endpos[1], 2))
        elif typ in ("kill", "grind"):
            m, k = kills_main[0]
            entry = w.nearest_spawn(parent.pos, m)
            for_q = [oq for oq, (kills, _) in parent.open.items() if dict(kills).get(m, 0) > EPS]
            e.update(mob=m, mobName=w.npcs[str(m)]["name"], count=round(k), x=round(entry[0], 2), y=round(entry[1], 2),
                     forQuests=for_q, forNames=[w.q[x]["name"] for x in for_q])
            # Schlenker: Umweg gegenueber dem direkten Weg von hier zum Ziel des naechsten Schritts.
            # Keine Schwelle: der Wert wird immer angegeben, der Spieler sieht, wie gross der Umweg ist.
            if idx + 1 < len(states):
                nxt = states[idx + 1].pos
                direct = yards(parent.pos, nxt, ZONE) or 0.0
                via = (yards(parent.pos, entry, ZONE) or 0.0) + (yards(entry, nxt, ZONE) or 0.0)
                e["detour"] = round(max(0.0, via - direct))
        steps.append(e)
    # Aufeinanderfolgende Grind-Schritte desselben Mobs zu einem Schritt zusammenfassen (die Suche zerlegt
    # Grinden in Portionen, fuer den Spieler ist es eine Handlung).
    merged = []
    for e in steps:
        if merged and e["type"] == "grind" and merged[-1]["type"] == "grind" and merged[-1]["mob"] == e["mob"]:
            prev = merged[-1]
            prev["count"] += e["count"]
            prev["minute"], prev["level"] = e["minute"], e["level"]
            if "detour" in e:
                prev["detour"] = e["detour"]
            elif "detour" in prev:
                del prev["detour"]
        else:
            merged.append(e)
    steps = merged
    # Nebenbei-Quests: Quests mit Kill-/Drop-Zielen, die nie gezielt bearbeitet werden (Fortschritt nur durch
    # Kills unterwegs oder fuer andere Quests). Sie bleiben im Log.
    dedicated = {q for s in steps if s["type"] == "kill" for q in s.get("forQuests", [])}
    for s in steps:
        if s["type"] == "accept" and w.need[s["quest"]]["kills"] and s["quest"] not in dedicated:
            s["side"] = True
    return steps


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-level", type=int, default=10)
    ap.add_argument("--beam", type=int, default=150)
    ap.add_argument("--bucket", type=float, default=20.0)
    a = ap.parse_args()
    objects = load("objects.json")
    w = World(load("quests.json"), load("npcs.json"), objects, load("items.json"),
              load("drops.json"), load("quest_xp_table.json"), 1)
    end = plan_refined(w, a.target_level, a.beam, a.bucket, single=False)
    if end is None:
        raise SystemExit("Kein Plan gefunden")
    steps = build_steps(w, end, objects)
    meta = {
        "generated": datetime.date.today().isoformat(),
        "race": "Human", "targetLevel": a.target_level, "plannedMinutes": round(end.t / 60, 1),
        "note": "Prototyp-Plan mit geratenen Zeitwerten, nicht kalibriert. Nur Northshire Valley und Elwynn Forest.",
        "sources": "QuestieDB (GPL-3.0), Questie-Support-Tabellen, Blizzard-Client-Tabellen via wago.tools. Keine ForeverDB-Daten enthalten.",
    }
    # Quests, die am Ende des Plans noch offen sind, bleiben als Hintergrund-Quests im Log.
    meta["background"] = [{"quest": qid, "name": w.q[qid]["name"]} for qid in sorted(end.open)]
    meta["sideQuests"] = [{"quest": s["quest"], "name": s["name"]} for s in steps if s.get("side")]
    body = lua_val({"meta": meta, "steps": steps})
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("-- AUTO-GENERATED by pipeline/emit/emit_lua.py. Do not edit.\nForeverLevelerPlan = " + body + "\n", encoding="utf-8")
    kinds = {}
    for s in steps:
        kinds[s["type"]] = kinds.get(s["type"], 0) + 1
    report = (f"# Plan-Ausgabe\n\nErzeugt: {meta['generated']}. Schritte: {len(steps)} ({kinds}). Geplante Zeit: {meta['plannedMinutes']} min bis Level {a.target_level}.\n"
              f"Datei: `addon/ForeverLeveler/Plan.lua` ({OUT.stat().st_size} Bytes).\n")
    (ROOT / "data/reports/plan_emit.md").write_text(report, encoding="utf-8")
    print(report)


if __name__ == "__main__":
    main()
