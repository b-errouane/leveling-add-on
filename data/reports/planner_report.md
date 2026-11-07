# Routenplanung (Strahlsuche + Monte Carlo), Mensch, Level 1 -> 10

ANNAHMEN (nicht gemessen): `pipeline/config/params.json`. Buendelung, Schlenker, Ruhestein und Grinden ergeben sich aus der Suche, es gibt keine Gruppen oder Schwellen.
Suchparameter: Strahlbreite 150, Zeit-Eimer 20 s. Zufall: 300 Nachspielungen mit gewuerfelten Drops.
Questlog-Plaetze: 20. Ruhestein-Heimat am Start: ja. Errands: keine.

## frei (beliebig viele Quests offen)
Plan (Erwartungswerte): Level 10 nach **72.9 min**, 19 Quests abgegeben, bis zu 6 gleichzeitig offen, geteilte Kills: 3
Handlungen: {'accept': 21, 'turnin': 19, 'grind': 6, 'misc': 5, 'kill': 7}. Wegarten: {'walk': 57, 'hearth': 1}
Mit gewuerfelten Drops (gleicher Plan): Mittel 79.4 min, Median 79.4 min, 10 %-Quantil 74.8 min, 90 %-Quantil 85.0 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 0.6 | 1 | 1 | annehmen Rest and Relaxation |
| 1.2 | 1 | 0 | abgeben Rest and Relaxation [hearth] |
| 2.8 | 2 | 0 | grinden Murloc x5 |
| 6.0 | 3 | 0 | grinden Murloc x14 |
| 10.5 | 4 | 0 | grinden Murloc x20 |
| 11.6 | 4 | 1 | annehmen The Fargodeep Mine |
| 11.9 | 4 | 0 | abgeben The Fargodeep Mine |
| 12.2 | 4 | 1 | annehmen Kobold Candles |
| 12.4 | 4 | 2 | annehmen The Jasperlode Mine |
| 12.7 | 4 | 1 | abgeben The Jasperlode Mine |
| 13.3 | 4 | 2 | annehmen A Net Disaster |
| 13.6 | 4 | 2 | erledigen A Net Disaster |
| 13.9 | 4 | 3 | annehmen Bottles and Baubles |
| 14.2 | 4 | 2 | abgeben A Net Disaster |
| 14.3 | 4 | 3 | annehmen Slimy Menace |
| 15.1 | 5 | 3 | toeten Murloc Streamrunner x2 (hilft 1 Quests) |
| 16.6 | 5 | 3 | toeten Murloc x7 (hilft 1 Quests) |
| 17.9 | 5 | 4 | annehmen Rough Wolf Pelts |
| 18.3 | 5 | 3 | abgeben Slimy Menace |
| 18.4 | 5 | 4 | annehmen A Man About a Murloc |
| 19.2 | 5 | 3 | abgeben A Man About a Murloc |
| 19.4 | 5 | 4 | annehmen Gold Dust Exchange |
| 22.8 | 6 | 4 | toeten Kobold Tunneler x12 (hilft 2 Quests) |
| 27.2 | 6 | 5 | annehmen An Enticing Offer |
| 27.6 | 6 | 4 | abgeben Kobold Candles |
| 27.8 | 6 | 5 | annehmen Shipment to Stormwind |
| 28.0 | 6 | 4 | abgeben Shipment to Stormwind |
| 28.4 | 6 | 3 | abgeben Gold Dust Exchange |
| 30.1 | 7 | 3 | grinden Young Forest Bear x5 |
| 30.8 | 7 | 4 | annehmen An Enchanting Lesson |
| 31.2 | 7 | 4 | erledigen An Enchanting Lesson |
| 31.4 | 7 | 3 | abgeben An Enchanting Lesson |
| 32.4 | 7 | 4 | annehmen Protect the Frontier |
| 34.7 | 7 | 4 | toeten Prowler x8 (hilft 2 Quests) |
| 34.9 | 7 | 5 | annehmen A Bundle of Trouble |
| 36.5 | 7 | 5 | erledigen A Bundle of Trouble |
| 38.4 | 7 | 6 | annehmen Downstream |
| 40.5 | 7 | 6 | erledigen Downstream |
| 42.2 | 7 | 5 | abgeben Downstream |
| 42.7 | 7 | 4 | abgeben Protect the Frontier |
| 43.3 | 8 | 4 | grinden Prowler x2 |
| 43.7 | 8 | 3 | abgeben A Bundle of Trouble |
| 57.2 | 9 | 3 | grinden Young Forest Bear x54 |
| 58.8 | 9 | 2 | abgeben Rough Wolf Pelts |
| 59.3 | 9 | 3 | annehmen Report to Gryan Stoutmantle |
| 59.6 | 9 | 2 | abgeben Report to Gryan Stoutmantle |
| 59.7 | 9 | 3 | annehmen Westbrook Garrison Needs Help! |
| 61.7 | 9 | 4 | annehmen An Apple Treat |
| 62.0 | 9 | 3 | abgeben Westbrook Garrison Needs Help! |
| 62.2 | 9 | 3 | erledigen An Apple Treat |
| 62.4 | 9 | 4 | annehmen WANTED: "Hogger" |
| 62.8 | 9 | 3 | abgeben An Apple Treat |
| 63.0 | 9 | 4 | annehmen Riverpaw Gnoll Bounty |
| 64.7 | 9 | 4 | toeten Hogger x1 (hilft 1 Quests) |
| 64.8 | 9 | 4 | toeten Hogger x0 (hilft 1 Quests) |
| 70.3 | 9 | 4 | toeten Riverpaw Outrunner x21 (hilft 1 Quests) |
| 70.9 | 9 | 3 | abgeben WANTED: "Hogger" |
| 72.9 | 10 | 2 | abgeben Riverpaw Gnoll Bounty |

## Vergleich: immer nur eine Quest offen
Plan (Erwartungswerte): Level 10 nach **77.5 min**, 11 Quests abgegeben, bis zu 1 gleichzeitig offen, geteilte Kills: 0
Handlungen: {'grind': 18, 'accept': 11, 'turnin': 11, 'misc': 2, 'kill': 5}. Wegarten: {'walk': 46, 'hearth': 1}
Mit gewuerfelten Drops (gleicher Plan): Mittel 79.1 min, Median 78.6 min, 10 %-Quantil 77.5 min, 90 %-Quantil 82.1 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 2.1 | 2 | 0 | grinden Kobold Worker x8 |
| 5.6 | 3 | 0 | grinden Kobold Laborer x15 |
| 10.6 | 4 | 0 | grinden Kobold Laborer x22 |
| 11.3 | 4 | 1 | annehmen The Fargodeep Mine [hearth] |
| 11.5 | 4 | 0 | abgeben The Fargodeep Mine |
| 12.2 | 4 | 1 | annehmen A Net Disaster |
| 12.5 | 4 | 1 | erledigen A Net Disaster |
| 12.9 | 4 | 0 | abgeben A Net Disaster |
| 13.5 | 4 | 1 | annehmen The Jasperlode Mine |
| 13.8 | 4 | 0 | abgeben The Jasperlode Mine |
| 14.0 | 4 | 1 | annehmen Kobold Candles |
| 14.7 | 5 | 1 | grinden Stonetusk Boar x2 |
| 21.6 | 5 | 1 | toeten Kobold Tunneler x28 (hilft 1 Quests) |
| 23.9 | 6 | 1 | grinden Kobold Miner x9 |
| 25.0 | 6 | 0 | abgeben Kobold Candles |
| 25.1 | 6 | 1 | annehmen Shipment to Stormwind |
| 25.4 | 6 | 0 | abgeben Shipment to Stormwind |
| 25.9 | 6 | 1 | annehmen Slimy Menace |
| 27.2 | 6 | 1 | toeten Murloc Streamrunner x4 (hilft 1 Quests) |
| 28.8 | 6 | 1 | toeten Murloc x7 (hilft 1 Quests) |
| 29.7 | 6 | 0 | abgeben Slimy Menace |
| 29.8 | 6 | 1 | annehmen A Man About a Murloc |
| 30.6 | 6 | 0 | abgeben A Man About a Murloc |
| 30.8 | 6 | 1 | annehmen Westbrook Garrison Needs Help! |
| 32.1 | 7 | 1 | grinden Stonetusk Boar x4 |
| 33.6 | 7 | 0 | abgeben Westbrook Garrison Needs Help! |
| 33.8 | 7 | 1 | annehmen An Apple Treat |
| 36.6 | 7 | 1 | grinden Longsnout x9 |
| 39.0 | 7 | 1 | grinden Longsnout x9 |
| 41.5 | 7 | 1 | grinden Longsnout x9 |
| 43.9 | 7 | 1 | grinden Longsnout x9 |
| 44.7 | 7 | 1 | erledigen An Apple Treat |
| 44.9 | 7 | 0 | abgeben An Apple Treat |
| 45.2 | 7 | 1 | annehmen WANTED: "Hogger" |
| 45.7 | 8 | 1 | grinden Longsnout x1 |
| 48.1 | 8 | 1 | grinden Longsnout x9 |
| 50.5 | 8 | 1 | grinden Longsnout x9 |
| 53.0 | 8 | 1 | grinden Longsnout x9 |
| 55.4 | 8 | 1 | grinden Longsnout x9 |
| 57.9 | 8 | 1 | grinden Longsnout x9 |
| 59.0 | 8 | 1 | toeten Hogger x1 (hilft 1 Quests) |
| 59.1 | 8 | 1 | toeten Hogger x0 (hilft 1 Quests) |
| 74.4 | 9 | 1 | grinden Riverpaw Outrunner x58 |
| 75.0 | 9 | 0 | abgeben WANTED: "Hogger" |
| 75.2 | 9 | 1 | annehmen Report to Gryan Stoutmantle |
| 75.4 | 9 | 0 | abgeben Report to Gryan Stoutmantle |
| 77.5 | 10 | 0 | grinden Young Forest Bear x6 |

Vergleich (Erwartungswerte): frei 72.9 min, eine Quest zur Zeit 77.5 min (6 % weniger). Ohne Gewaehr, siehe Annahmen.