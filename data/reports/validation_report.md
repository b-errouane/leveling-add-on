# Qualitaetsbericht (Normalisierung und Pruefung)

Erzeugt aus `data/normalized/` (Stand 2026-11-07).
Quellen: Daten: QuestieDB (GPL-3.0), Wowhead-basierte Drop-Tabelle von Questie, Blizzard-Client-Tabellen via wago.tools. ForeverDB-Daten sind (noch) nicht enthalten.

Quests 5233, NPCs 13417, Objekte 7045, Items 21442.

## Harte Fehler
- keine

## Warnungen
- Fehlende Referenzen: quest_ref:prequest_single = 1
- Fehlende Referenzen: quest_ref:prequest_group = 2

## Kennzahlen
- finisher_ohne_position: 15
- ohne_abgabe: 287
- ohne_annahme: 174
- placeholder: 6
- quests_im_zyklus: 0
- required_level_ueber_quest_level: 32
- starter_ohne_position: 10
- vorquest_kanten_bei_exklusiven_ignoriert: 12
- vorquest_selbstverweise_entfernt: 2
- xp_level_nicht_in_client_tabelle: 2
- xp_level_ungleich_quest_level: 14
- xp_wert_in_client_zeile: 3492

## Platzhalter-Quests (6)
5691:<NYI> <TXT> In the Dark it was Created, 5692:<NYI> In the Dark It was Created, 5693:<NYI> In the Dark It was Created, 5704:<NYI> <TXT> Undead Priest Robe, 5705:<NYI> No Longer a Shadow, 5706:<NYI> No Longer a Shadow

## Zonenbericht (Zonen [9, 12])
{
  "quests": 74,
  "mit_xp": 45,
  "level_min": 1,
  "level_max": 12,
  "xp_summe": 19060,
  "mit_ziel_kill": 7,
  "mit_ziel_item": 33,
  "mit_vorquest": 42
}
