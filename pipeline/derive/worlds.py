"""Welten (Zonen-Konfigurationen) fuer Planer und Ausgabe.

Eine Welt beschreibt, fuer welches Gebiet geplant wird: Zonen-IDs der Quests, Koordinatenrahmen (Questie-Spawns sind
je Zone gespeichert), Karten-ID fuer TomTom, Start (Ort, Level) und Ziel.

Kartengroessen stehen in params.json (zone_size_yards), abgeleitet aus UiMapAssignment (wago.tools).
"""

WORLDS = {
    "elwynn": {
        "title": "Northshire Valley und Elwynn Forest",
        "zones": {9, 12},          # zone_or_sort der Quests
        "frame": 12,               # Zone, in deren Koordinaten Questie die Positionen speichert
        "uimap": 1429,             # Karte fuer TomTom (Elwynn Forest)
        "start_npc": 197,          # Marshal McBride, Northshire Abbey
        "start_level": 1,
        "start_xp": 0.0,
        "target_level": 10,
        "outside_done": False,     # Vorquests ausserhalb der Zone zaehlen NICHT als erledigt (Startgebiet)
        "home_npc": None,          # Ruhestein am Start nicht gesetzt (Nutzer)
    },
    "redridge": {
        "title": "Redridge Mountains (Rotkammgebirge)",
        "zones": {44},
        "frame": 44,
        "uimap": 1433,
        "start_npc": 6727,         # Innkeeper Brianna, Lakeshire (Annahme: Spieler beginnt in Lakeshire)
        "start_level": 16,
        "start_xp": 0.0,
        "target_level": 20,
        "outside_done": True,      # Vorquests ausserhalb der Zone gelten als erledigt (Annahme)
        "home_npc": None,
    },
}
