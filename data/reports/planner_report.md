# Routenplanung (Strahlsuche + Monte Carlo), Mensch, Level 1 -> 10

ANNAHMEN (nicht gemessen): `pipeline/config/params.json`. Buendelung, Schlenker, Ruhestein und Grinden ergeben sich aus der Suche, es gibt keine Gruppen oder Schwellen.
Suchparameter: Strahlbreite 100, Zeit-Eimer 20 s. Zufall: 300 Nachspielungen mit gewuerfelten Drops.
Questlog-Plaetze: 20. Ruhestein-Heimat am Start: nicht gesetzt, Gastwirte in der Zone: 1. Errands: ['Lehrer'].

## frei (beliebig viele Quests offen)
Plan (Erwartungswerte): Level 10 nach **74.9 min**, 15 Quests abgegeben, bis zu 4 gleichzeitig offen, geteilte Kills: 3
Handlungen: {'accept': 16, 'turnin': 15, 'grind': 11, 'misc': 3, 'sethome': 1, 'kill': 6, 'errand': 1}. Wegarten: {'walk': 52, 'hearth': 1}
Mit gewuerfelten Drops (gleicher Plan): Mittel 80.0 min, Median 79.3 min, 10 %-Quantil 74.9 min, 90 %-Quantil 85.5 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 0.6 | 1 | 1 | annehmen Rest and Relaxation |
| 1.9 | 1 | 0 | abgeben Rest and Relaxation |
| 3.5 | 2 | 0 | grinden Murloc x5 |
| 6.6 | 3 | 0 | grinden Murloc x14 |
| 11.1 | 4 | 0 | grinden Murloc x20 |
| 11.9 | 4 | 1 | annehmen A Net Disaster |
| 12.2 | 4 | 1 | erledigen A Net Disaster |
| 12.6 | 4 | 0 | abgeben A Net Disaster |
| 12.8 | 4 | 1 | annehmen Slimy Menace |
| 13.3 | 4 | 2 | annehmen Kobold Candles |
| 13.6 | 4 | 3 | annehmen The Fargodeep Mine |
| 13.8 | 4 | 2 | abgeben The Fargodeep Mine |
| 14.0 | 4 | 3 | annehmen The Jasperlode Mine |
| 14.5 | 4 | 3 | Heimat setzen: Innkeeper Farley |
| 14.9 | 4 | 2 | abgeben The Jasperlode Mine |
| 15.1 | 4 | 3 | annehmen Gold Dust Exchange |
| 16.1 | 5 | 3 | toeten Kobold Tunneler x2 (hilft 2 Quests) |
| 20.3 | 5 | 4 | annehmen Lost Necklace |
| 22.6 | 5 | 4 | toeten Kobold Tunneler x9 (hilft 2 Quests) |
| 23.2 | 5 | 3 | abgeben Kobold Candles [hearth] |
| 23.6 | 6 | 2 | abgeben Gold Dust Exchange |
| 23.9 | 6 | 3 | annehmen Shipment to Stormwind |
| 24.1 | 6 | 2 | abgeben Shipment to Stormwind |
| 24.7 | 6 | 3 | annehmen Bottles and Baubles |
| 26.6 | 6 | 3 | toeten Murloc x7 (hilft 1 Quests) |
| 27.5 | 6 | 3 | erledigen Bottles and Baubles |
| 29.3 | 6 | 2 | abgeben Bottles and Baubles |
| 29.6 | 6 | 1 | abgeben Slimy Menace |
| 29.8 | 6 | 2 | annehmen A Man About a Murloc |
| 30.5 | 7 | 1 | abgeben A Man About a Murloc |
| 32.2 | 7 | 2 | annehmen An Apple Treat |
| 32.4 | 7 | 2 | erledigen An Apple Treat |
| 35.1 | 7 | 2 | grinden Longsnout x9 |
| 37.6 | 7 | 2 | grinden Longsnout x9 |
| 40.0 | 7 | 2 | grinden Longsnout x9 |
| 40.9 | 7 | 1 | abgeben An Apple Treat |
| 41.1 | 7 | 2 | annehmen WANTED: "Hogger" |
| 41.3 | 7 | 3 | annehmen Riverpaw Gnoll Bounty |
| 43.0 | 7 | 3 | toeten Hogger x1 (hilft 1 Quests) |
| 43.1 | 7 | 3 | toeten Hogger x0 (hilft 1 Quests) |
| 48.6 | 8 | 3 | toeten Riverpaw Outrunner x21 (hilft 1 Quests) |
| 49.2 | 8 | 2 | abgeben WANTED: "Hogger" |
| 49.4 | 8 | 3 | annehmen Westbrook Garrison Needs Help! |
| 50.3 | 8 | 3 | Lehrer besuchen (3 neue Stufe(n)) |
| 52.0 | 8 | 2 | abgeben Westbrook Garrison Needs Help! |
| 52.2 | 8 | 1 | abgeben Riverpaw Gnoll Bounty |
| 54.8 | 8 | 1 | grinden Longsnout x9 |
| 57.1 | 8 | 1 | grinden Longsnout x9 |
| 59.4 | 9 | 1 | grinden Longsnout x9 |
| 73.8 | 9 | 1 | grinden Riverpaw Outrunner x58 |
| 74.3 | 9 | 2 | annehmen Report to Gryan Stoutmantle |
| 74.5 | 9 | 1 | abgeben Report to Gryan Stoutmantle |
| 74.9 | 10 | 1 | grinden Stonetusk Boar x1 |

## Vergleich: immer nur eine Quest offen
Plan (Erwartungswerte): Level 10 nach **78.0 min**, 8 Quests abgegeben, bis zu 1 gleichzeitig offen, geteilte Kills: 0
Handlungen: {'accept': 8, 'turnin': 8, 'grind': 8, 'misc': 1, 'sethome': 1, 'kill': 4, 'errand': 1}. Wegarten: {'walk': 30, 'hearth': 1}
Mit gewuerfelten Drops (gleicher Plan): Mittel 79.4 min, Median 78.0 min, 10 %-Quantil 78.0 min, 90 %-Quantil 81.4 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 0.6 | 1 | 1 | annehmen Rest and Relaxation |
| 1.9 | 1 | 0 | abgeben Rest and Relaxation |
| 3.5 | 2 | 0 | grinden Murloc x5 |
| 10.9 | 3 | 0 | grinden Murloc x33 |
| 11.4 | 4 | 0 | grinden Murloc x2 |
| 12.2 | 4 | 1 | annehmen A Net Disaster |
| 12.4 | 4 | 1 | erledigen A Net Disaster |
| 12.8 | 4 | 0 | abgeben A Net Disaster |
| 13.5 | 4 | 1 | annehmen The Fargodeep Mine |
| 13.7 | 4 | 0 | abgeben The Fargodeep Mine |
| 14.2 | 4 | 0 | Heimat setzen: Innkeeper Farley |
| 14.5 | 4 | 1 | annehmen The Jasperlode Mine |
| 14.7 | 4 | 0 | abgeben The Jasperlode Mine |
| 15.0 | 4 | 1 | annehmen Kobold Candles |
| 15.7 | 5 | 1 | grinden Stonetusk Boar x2 |
| 22.6 | 5 | 1 | toeten Kobold Tunneler x28 (hilft 1 Quests) |
| 23.2 | 5 | 0 | abgeben Kobold Candles [hearth] |
| 23.8 | 5 | 1 | annehmen Slimy Menace |
| 24.8 | 6 | 1 | toeten Murloc x3 (hilft 1 Quests) |
| 25.6 | 6 | 1 | toeten Murloc x4 (hilft 1 Quests) |
| 26.8 | 6 | 1 | toeten Murloc Streamrunner x4 (hilft 1 Quests) |
| 27.6 | 6 | 0 | abgeben Slimy Menace |
| 27.8 | 6 | 1 | annehmen A Man About a Murloc |
| 28.6 | 6 | 0 | abgeben A Man About a Murloc |
| 28.9 | 6 | 1 | annehmen Shipment to Stormwind |
| 29.1 | 6 | 0 | abgeben Shipment to Stormwind |
| 30.0 | 6 | 0 | Lehrer besuchen (2 neue Stufe(n)) |
| 33.3 | 7 | 0 | grinden Young Forest Bear x12 |
| 45.7 | 8 | 0 | grinden Young Forest Bear x53 |
| 77.4 | 9 | 0 | grinden Young Forest Bear x136 |
| 78.0 | 10 | 0 | grinden Young Forest Bear x3 |

Vergleich (Erwartungswerte): frei 74.9 min, eine Quest zur Zeit 78.0 min (4 % weniger). Ohne Gewaehr, siehe Annahmen.