# Routen-Simulation (Prototyp), Mensch, Level 1 -> 10

ANNAHMEN (nicht gemessen): siehe `pipeline/config/params.json`. Nur Quests aus Northshire/Elwynn. Buendel ohne feste Gruppen: lokale Suche aus jeder verfuegbaren Quest heraus.
Neue Quests ohne XP-Angabe sind mit der typischen Stufe geschaetzt (siehe derived_report.md).

## mit Buendeln
Erreicht: Level 10 nach 63 min (33 Quests, 10 Schritte)

| # | Level | Quests | XP | Zeit (s) | Gesamt (min) |
|---|---|---|---|---|---|
| 1 | 1->2 | Wolves Across the Border; Rest and Relaxation | 1024 | 258 | 4.3 |
| 2 | 2->2 | Give Gerard a Drink; A Threat Within | 120 | 89 | 5.8 |
| 3 | 2->4 | Brotherhood of Thieves; Kobold Camp Cleanup | 2356 | 499 | 14.1 |
| 4 | 4->5 | Red Linen Goods; A Net Disaster; The Fargodeep Mine; Bounty on Garrick Padfoot | 3565 | 378 | 20.4 |
| 5 | 5->6 | The Jasperlode Mine; WANTED: "Hogger"; An Enchanting Lesson | 2551 | 209 | 23.9 |
| 6 | 6->8 | Riverpaw Gnoll Bounty; A Bundle of Trouble; Princess Must Die!; Slimy Menace; Bottles and Baubles | 6499 | 697 | 35.5 |
| 7 | 8->8 | A Man About a Murloc; An Apple Treat | 1470 | 97 | 37.1 |
| 8 | 8->9 | Protect the Frontier; Downstream; Delicate Instruments; Good Steel; Stolen Enchanting Supplies; Rough Wolf Pelts | 7332 | 746 | 49.6 |
| 9 | 9->9 | Report to Gryan Stoutmantl; Delicate Instruments | 2230 | 271 | 54.1 |
| 10 | 9->10 | Young Lovers; Gold Dust Exchange; Kobold Candles; Westbrook Garrison Needs H; Lost Necklace | 2887 | 544 | 63.1 |

## ohne Buendel (je Quest einzeln)
Erreicht: Level 10 nach 82 min (24 Quests, 24 Schritte)

| # | Level | Quests | XP | Zeit (s) | Gesamt (min) |
|---|---|---|---|---|---|
| 1 | 1->2 | Wolves Across the Border | 914 | 241 | 4.0 |
| 2 | 2->2 | Rest and Relaxation | 110 | 93 | 5.6 |
| 3 | 2->2 | Give Gerard a Drink | 80 | 84 | 7.0 |
| 4 | 2->3 | Applejack Still | 239 | 314 | 12.2 |
| 5 | 3->4 | Kobold Candles | 2442 | 502 | 20.6 |
| 6 | 4->4 | Shipment to Stormwind | 790 | 25 | 21.0 |
| 7 | 4->5 | A Net Disaster | 630 | 59 | 21.9 |
| 8 | 5->5 | Slimy Menace | 1444 | 198 | 25.2 |
| 9 | 5->5 | A Man About a Murloc | 630 | 44 | 26.0 |
| 10 | 5->6 | Gold Dust Exchange | 2771 | 448 | 33.5 |
| 11 | 6->6 | An Enchanting Lesson | 630 | 108 | 35.2 |
| 12 | 6->7 | Red Linen Goods | 2249 | 364 | 41.3 |
| 13 | 7->7 | Downstream | 840 | 103 | 43.0 |
| 14 | 7->7 | Protect the Frontier | 1792 | 220 | 46.7 |
| 15 | 7->8 | Delicate Instruments | 1376 | 221 | 50.4 |
| 16 | 8->8 | Delicate Instruments | 1592 | 199 | 53.7 |
| 17 | 8->8 | An Apple Treat | 840 | 139 | 56.0 |
| 18 | 8->8 | WANTED: "Hogger" | 1114 | 202 | 59.4 |
| 19 | 8->9 | Rough Wolf Pelts | 2580 | 457 | 67.0 |
| 20 | 9->9 | Report to Gryan Stoutmantl | 630 | 39 | 67.6 |
| 21 | 9->9 | Bottles and Baubles | 630 | 140 | 70.0 |
| 22 | 9->9 | The Fargodeep Mine | 475 | 126 | 72.1 |
| 23 | 9->9 | The Jasperlode Mine | 840 | 146 | 74.5 |
| 24 | 9->10 | Riverpaw Gnoll Bounty | 2849 | 447 | 82.0 |

Vergleich: Buendel 63 min, einzeln 82 min (23 % weniger).

Nicht gemachte Quests (Mindestlevel <= 10) bei Variante mit Buendeln: 35 von 70