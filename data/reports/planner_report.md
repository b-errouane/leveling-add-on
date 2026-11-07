# Routenplanung (Strahlsuche + Monte Carlo), Mensch, Level 1 -> 10

ANNAHMEN (nicht gemessen): `pipeline/config/params.json`. Buendelung ergibt sich aus der Suche, es gibt keine Gruppen oder Schwellen.
Suchparameter: Strahlbreite 150, Zeit-Eimer 20 s. Zufall: 300 Nachspielungen mit gewuerfelten Drops.

## frei (beliebig viele Quests offen)
Plan (Erwartungswerte): Level 10 nach **82.4 min**, 28 Quests abgegeben, bis zu 8 gleichzeitig offen, geteilte Kills: 0
Mit gewuerfelten Drops (gleicher Plan): Mittel 87.0 min, Median 86.7 min, 10 %-Quantil 82.4 min, 90 %-Quantil 91.2 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 0.6 | 1 | 1 | annehmen Rest and Relaxation |
| 1.1 | 1 | 2 | annehmen A Threat Within |
| 1.5 | 1 | 1 | abgeben A Threat Within |
| 1.7 | 1 | 2 | annehmen Wolves Across the Border |
| 2.2 | 1 | 3 | annehmen Kobold Camp Cleanup |
| 4.6 | 2 | 3 | toeten Kobold Vermin x10 (hilft 1 Quests) |
| 6.0 | 2 | 4 | annehmen Brotherhood of Thieves |
| 6.2 | 2 | 5 | annehmen Eagan Peltskinner |
| 6.8 | 2 | 4 | abgeben Eagan Peltskinner |
| 7.3 | 2 | 3 | abgeben Kobold Camp Cleanup |
| 10.2 | 3 | 2 | abgeben Rest and Relaxation |
| 10.4 | 3 | 3 | annehmen Kobold Candles |
| 17.9 | 4 | 3 | toeten Kobold Tunneler x28 (hilft 1 Quests) |
| 19.0 | 4 | 4 | annehmen The Fargodeep Mine |
| 19.2 | 4 | 3 | abgeben The Fargodeep Mine |
| 19.6 | 4 | 2 | abgeben Kobold Candles |
| 19.9 | 4 | 3 | annehmen The Jasperlode Mine |
| 20.1 | 5 | 2 | abgeben The Jasperlode Mine |
| 20.4 | 5 | 3 | annehmen Shipment to Stormwind |
| 20.9 | 5 | 4 | annehmen A Net Disaster |
| 21.2 | 5 | 4 | erledigen A Net Disaster |
| 21.6 | 5 | 3 | abgeben A Net Disaster |
| 21.8 | 5 | 4 | annehmen Slimy Menace |
| 23.1 | 5 | 4 | toeten Murloc Streamrunner x4 (hilft 1 Quests) |
| 24.6 | 5 | 4 | toeten Murloc x7 (hilft 1 Quests) |
| 25.5 | 5 | 3 | abgeben Slimy Menace |
| 25.7 | 5 | 4 | annehmen A Man About a Murloc |
| 26.3 | 6 | 3 | abgeben Shipment to Stormwind |
| 26.6 | 6 | 4 | annehmen Westbrook Garrison Needs Help! |
| 26.9 | 6 | 3 | abgeben A Man About a Murloc |
| 28.6 | 6 | 4 | annehmen Riverpaw Gnoll Bounty |
| 28.9 | 6 | 3 | abgeben Westbrook Garrison Needs Help! |
| 34.8 | 6 | 3 | toeten Riverpaw Outrunner x21 (hilft 1 Quests) |
| 35.3 | 6 | 4 | annehmen Gold Dust Exchange |
| 42.9 | 7 | 4 | toeten Kobold Tunneler x29 (hilft 1 Quests) |
| 44.3 | 7 | 5 | annehmen WANTED: "Hogger" |
| 44.6 | 7 | 6 | annehmen An Apple Treat |
| 44.9 | 7 | 5 | abgeben Riverpaw Gnoll Bounty |
| 45.1 | 7 | 5 | erledigen An Apple Treat |
| 45.3 | 7 | 4 | abgeben An Apple Treat |
| 47.4 | 7 | 4 | toeten Hogger x1 (hilft 1 Quests) |
| 49.6 | 7 | 5 | annehmen A Fishy Peril |
| 49.9 | 7 | 4 | abgeben A Fishy Peril |
| 50.2 | 8 | 3 | abgeben WANTED: "Hogger" |
| 50.5 | 8 | 2 | abgeben Gold Dust Exchange |
| 50.7 | 8 | 3 | annehmen Further Concerns |
| 51.3 | 8 | 4 | annehmen Rough Wolf Pelts |
| 51.6 | 8 | 5 | annehmen Bottles and Baubles |
| 58.8 | 8 | 5 | toeten Prowler x20 (hilft 1 Quests) |
| 59.7 | 8 | 4 | abgeben Further Concerns |
| 59.8 | 8 | 5 | annehmen Protect the Frontier |
| 60.2 | 8 | 6 | annehmen Downstream |
| 62.3 | 8 | 6 | erledigen Downstream |
| 63.1 | 8 | 6 | toeten Young Forest Bear x3 (hilft 1 Quests) |
| 63.8 | 8 | 7 | annehmen An Enchanting Lesson |
| 64.2 | 8 | 7 | erledigen An Enchanting Lesson |
| 64.4 | 8 | 8 | annehmen Delicate Instruments |
| 64.7 | 8 | 7 | abgeben An Enchanting Lesson |
| 67.6 | 8 | 7 | toeten Kobold Geomancer x8 (hilft 1 Quests) |
| 69.2 | 9 | 7 | toeten Prowler x4 (hilft 1 Quests) |
| 69.9 | 9 | 6 | abgeben Downstream |
| 70.3 | 9 | 7 | annehmen Find the Lost Guards |
| 70.5 | 9 | 6 | abgeben Protect the Frontier |
| 71.5 | 9 | 5 | abgeben Delicate Instruments |
| 71.7 | 9 | 6 | annehmen Delicate Instruments |
| 73.3 | 9 | 6 | erledigen Bottles and Baubles |
| 74.3 | 9 | 5 | abgeben Bottles and Baubles |
| 74.6 | 9 | 4 | abgeben Rough Wolf Pelts |
| 75.2 | 9 | 5 | annehmen Report to Gryan Stoutmantle |
| 75.4 | 9 | 4 | abgeben Report to Gryan Stoutmantle |
| 79.2 | 9 | 4 | toeten Defias Rogue Wizard x8 (hilft 1 Quests) |
| 80.3 | 9 | 3 | abgeben Delicate Instruments |
| 81.3 | 9 | 2 | abgeben Find the Lost Guards |
| 81.5 | 9 | 3 | annehmen Discover Rolf's Fate |
| 82.4 | 10 | 2 | abgeben Discover Rolf's Fate |

## Vergleich: immer nur eine Quest offen
Plan (Erwartungswerte): Level 10 nach **95.6 min**, 25 Quests abgegeben, bis zu 1 gleichzeitig offen, geteilte Kills: 0
Mit gewuerfelten Drops (gleicher Plan): Mittel 101.9 min, Median 102.1 min, 10 %-Quantil 97.6 min, 90 %-Quantil 106.1 min

| Min | Level | offen | Handlung |
|---|---|---|---|
| 2.6 | 1 | 1 | annehmen Give Gerard a Drink |
| 2.8 | 1 | 1 | erledigen Give Gerard a Drink |
| 3.0 | 1 | 0 | abgeben Give Gerard a Drink |
| 5.6 | 1 | 1 | annehmen A Threat Within |
| 5.9 | 1 | 0 | abgeben A Threat Within |
| 6.1 | 1 | 1 | annehmen Kobold Camp Cleanup |
| 8.6 | 2 | 1 | toeten Kobold Vermin x10 (hilft 1 Quests) |
| 9.1 | 2 | 0 | abgeben Kobold Camp Cleanup |
| 9.4 | 2 | 1 | annehmen Brotherhood of Thieves |
| 14.7 | 3 | 1 | toeten Defias Thug x21 (hilft 1 Quests) |
| 15.5 | 3 | 0 | abgeben Brotherhood of Thieves |
| 15.8 | 3 | 1 | annehmen Investigate Echo Ridge |
| 18.3 | 4 | 1 | toeten Kobold Worker x10 (hilft 1 Quests) |
| 18.9 | 4 | 0 | abgeben Investigate Echo Ridge |
| 19.5 | 4 | 1 | annehmen Rest and Relaxation |
| 20.8 | 4 | 0 | abgeben Rest and Relaxation |
| 21.1 | 4 | 1 | annehmen The Fargodeep Mine |
| 21.3 | 4 | 0 | abgeben The Fargodeep Mine |
| 22.0 | 4 | 1 | annehmen A Net Disaster |
| 22.3 | 4 | 1 | erledigen A Net Disaster |
| 22.7 | 4 | 0 | abgeben A Net Disaster |
| 23.3 | 4 | 1 | annehmen The Jasperlode Mine |
| 23.6 | 5 | 0 | abgeben The Jasperlode Mine |
| 23.8 | 5 | 1 | annehmen Kobold Candles |
| 31.4 | 5 | 1 | toeten Kobold Tunneler x28 (hilft 1 Quests) |
| 32.6 | 6 | 0 | abgeben Kobold Candles |
| 32.8 | 6 | 1 | annehmen Shipment to Stormwind |
| 33.0 | 6 | 0 | abgeben Shipment to Stormwind |
| 33.6 | 6 | 1 | annehmen Slimy Menace |
| 34.9 | 6 | 1 | toeten Murloc Streamrunner x4 (hilft 1 Quests) |
| 36.4 | 6 | 1 | toeten Murloc x7 (hilft 1 Quests) |
| 37.3 | 6 | 0 | abgeben Slimy Menace |
| 37.5 | 6 | 1 | annehmen A Man About a Murloc |
| 38.2 | 6 | 0 | abgeben A Man About a Murloc |
| 38.4 | 6 | 1 | annehmen Gold Dust Exchange |
| 46.0 | 7 | 1 | toeten Kobold Tunneler x29 (hilft 1 Quests) |
| 47.1 | 7 | 0 | abgeben Gold Dust Exchange |
| 49.2 | 7 | 1 | annehmen An Enchanting Lesson |
| 49.6 | 7 | 1 | erledigen An Enchanting Lesson |
| 49.8 | 7 | 0 | abgeben An Enchanting Lesson |
| 50.0 | 7 | 1 | annehmen Delicate Instruments |
| 52.8 | 7 | 1 | toeten Kobold Geomancer x8 (hilft 1 Quests) |
| 53.9 | 7 | 0 | abgeben Delicate Instruments |
| 55.0 | 7 | 1 | annehmen Downstream |
| 55.9 | 7 | 1 | erledigen Downstream |
| 56.6 | 8 | 0 | abgeben Downstream |
| 57.0 | 8 | 1 | annehmen Protect the Frontier |
| 59.3 | 8 | 1 | toeten Prowler x8 (hilft 1 Quests) |
| 60.8 | 8 | 1 | toeten Young Forest Bear x5 (hilft 1 Quests) |
| 62.2 | 8 | 0 | abgeben Protect the Frontier |
| 63.1 | 8 | 1 | annehmen A Bundle of Trouble |
| 64.5 | 8 | 1 | erledigen A Bundle of Trouble |
| 65.1 | 8 | 0 | abgeben A Bundle of Trouble |
| 65.5 | 8 | 1 | annehmen Red Linen Goods |
| 72.2 | 8 | 1 | toeten Defias Rogue Wizard x16 (hilft 1 Quests) |
| 73.9 | 9 | 0 | abgeben Red Linen Goods |
| 75.3 | 9 | 1 | annehmen Delicate Instruments |
| 79.0 | 9 | 1 | toeten Defias Rogue Wizard x8 (hilft 1 Quests) |
| 80.1 | 9 | 0 | abgeben Delicate Instruments |
| 81.8 | 9 | 1 | annehmen Bottles and Baubles |
| 83.3 | 9 | 1 | erledigen Bottles and Baubles |
| 84.3 | 9 | 0 | abgeben Bottles and Baubles |
| 85.0 | 9 | 1 | annehmen Report to Gryan Stoutmantle |
| 85.2 | 9 | 0 | abgeben Report to Gryan Stoutmantle |
| 86.9 | 9 | 1 | annehmen Riverpaw Gnoll Bounty |
| 92.9 | 9 | 1 | toeten Riverpaw Outrunner x21 (hilft 1 Quests) |
| 95.0 | 9 | 0 | abgeben Riverpaw Gnoll Bounty |
| 95.2 | 9 | 1 | annehmen An Apple Treat |
| 95.3 | 9 | 1 | erledigen An Apple Treat |
| 95.6 | 10 | 0 | abgeben An Apple Treat |

Vergleich (Erwartungswerte): frei 82.4 min, eine Quest zur Zeit 95.6 min (14 % weniger). Ohne Gewaehr, siehe Annahmen.