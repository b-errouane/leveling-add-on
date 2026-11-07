# Spike-Ergebnisse (Meilenstein 0, ohne ForeverDB-Key)

Stand: 2026-11-07. Code: `pipeline/spike/`. Rohdaten: `data/raw/` (nicht im Repo, siehe `.gitignore`).

## Was geprüft wurde

- Python 3.15.0 ist vorhanden, Node v18.16.0 ebenfalls. Ein Lua-Interpreter ist **nicht** installiert.
- QuestieDB (GPL-3.0) wurde per `git clone` geladen (642 Dateien).
- Ein eigener kleiner Parser (`pipeline/spike/luatable.py`) liest die Lua-Datentabellen von QuestieDB.

## Befunde

1. **Die Roh-Datei `data/Forever/foreverQuestDB.lua` enthält dieselben 4.244 Quest-IDs wie die Classic-Datei.** Neue Forever-Quests stehen dort nicht.
2. **Die Forever-Änderungen liegen in Korrekturschichten** (`src/corrections/Forever/`): eine generierte Delta-Basis (`generated/`, laut Zählung ca. 960 Quest-Einträge), Trace-Dateien und handgepflegte `forever*Fixes.lua` (ca. 646 Quest-Einträge). QuestieDB wendet sie beim Laden oder beim Erzeugen der Artefakte auf die Rohdaten an.
   Reihenfolge laut Doku: Rohdaten → geerbte Classic-Korrekturen → generierte Delta-Basis → Traces → handgepflegte Forever-Fixes.
3. **Die Doku von QuestieDB sagt selbst**, dass die Delta-Basis keine vollständigen Ziele, Einschränkungen oder anderes Spielverhalten liefert und dass Forever-Inhalte nicht vollständig sind. Die Aussage „neue Quests sind die schwache Stelle" aus [07-recherche-wow-forever.md](07-recherche-wow-forever.md) bestätigt sich damit.
4. **Rohdaten Quest-Felder (alle 4.244 Quests):** Annahme-NPC bei 98 %, Abgabe-NPC bei 98 %, Ziele bei 59 %, Vorquests bei 54 %, Questlevel bei 99,7 %.
5. **Quest-XP steht nicht in der Quest-Tabelle** (es gibt Reputation, aber keine XP-Spalte). Sie muss aus den Client-Tabellen oder ForeverDB kommen.
6. **Mob-Drop-Raten** sind in dieser Tabelle ebenfalls nicht enthalten (Kreaturen und Items liegen in eigenen Dateien, Drop-Raten noch nicht geprüft).

## Folgen für den Plan

- Wir können die Roh-Dateien nicht allein nehmen. Wir brauchen die **zusammengeführten Forever-Daten** (Roh + Korrekturschichten).
- Zwei Wege dafür:
  - **A:** Den Generator von QuestieDB (`generate.lua`) mit einem Lua-Interpreter laufen lassen und dessen Ausgabe weiterverarbeiten. Das Repo bringt nach eigener Doku einen Windows-Lua mit (`tools/lua-binary/lua.exe`). Ein fremdes, im Repo mitgeliefertes Programm wird nicht ohne Zustimmung ausgeführt.
  - **B:** Die Korrekturschichten in Python selbst anwenden. Die Dateien sind Lua-Code mit Ausdrücken (z. B. `raceIDs.A + raceIDs.B`), das ist aufwendiger und fehleranfälliger.
- Alternativ oder ergänzend liefert **ForeverDB** die neuen Quests, sobald der Key da ist.

## Update: zusammengeführte Forever-Daten

Stand: 2026-11-07. Der Export `tools/export-forever.lua --include-authored` des QuestieDB-Repos wurde vom Nutzer selbst ausgeführt, mit dem im Repo mitgelieferten Lua 5.1 (`tools/lua-binary/lua.exe`). Lua 5.5 scheiterte an der Syntax, LuaJIT am Konstanten-Limit (65.536). Vorher wurde der beteiligte Lua-Code per Muster-Scan geprüft (kein Netzwerkzugriff, kein `require`, Schreibzugriff nur auf den Ausgabeordner). Das war kein vollständiges Code-Review.

Ausgabe: `data/raw/QuestieDB/src/corrections/Forever/combined/` mit 5.233 Quests, 13.417 NPCs, 21.442 Items und 7.045 Objekten. Auswertung: `pipeline/spike/forever_combined_stats.py`.

### Abdeckung

**989 neue Quest-IDs** gegenüber Classic (4.244 Basis-Quests bleiben alle erhalten). Das passt zur Blizzard-Angabe „über 1.000 neue Quests".

| Merkmal | Classic-Basis (4.244) | Neue Forever-Quests (989) |
|---|---|---|
| Name | 100 % | 100 % |
| Questlevel | 100 % | 99,7 % |
| Zone | 100 % | 93,4 % |
| Annahme-Ort (NPC/Objekt/Item) | 98,0 % | 90,9 % |
| Abgabe-Ort | 98,2 % | 78,7 % |
| Annahme-NPC mit Spawn-Position | 87,5 % | 69,0 % |
| Abgabe-NPC mit Spawn-Position | 93,3 % | 75,1 % |
| Ziele (Objectives) | 61,3 % | 65,2 % |
| Vorquest-Eintrag | 53,2 % | 32,2 % |

Neue Quests je Level-Band (Questlevel): 0–9: 246, 10–19: 221, 20–29: 142, 30–39: 131, 40–49: 53, 50–59: 2, 60+: 191.

### Einordnung

- Die Daten sind **brauchbar als Grundlage**, aber für die neuen Quests spürbar lückenhafter: gut ein Viertel der Abgabe-NPCs ohne bekannte Position, rund ein Drittel der Annahme-NPCs. Ohne Position kann TomTom keinen Pfeil setzen, und die Reisezeit lässt sich nicht schätzen.
- Einige neue Quests sind Platzhalter (z. B. Namen mit `<NYI>` oder `<TXT>`). Sie müssen in der Pipeline erkannt und ausgeschlossen werden.
- Der niedrige Anteil an Vorquests bei neuen Quests heißt entweder, dass viele wirklich keine haben, oder dass die Daten fehlen. Das lässt sich ohne Zweitquelle nicht unterscheiden.
- Das Ergebnis sagt noch nichts über die **Richtigkeit** der Werte. Dafür braucht es Stichproben (ForeverDB, im Spiel).
- Quest-XP und Drop-Raten fehlen weiterhin (siehe oben).

## Client-Tabellen (DB2) für Forever

Stand: 2026-11-07. Abruf über die von der `robots.txt` von wago.tools ausdrücklich erlaubten Routen (`/api/builds`, `/db2/<Tabelle>/csv?build=…`) mit einem beschreibenden User-Agent, nacheinander mit einer Sekunde Pause. Die HTML-Seiten sind laut `robots.txt` für Crawler gesperrt und werden nicht abgerufen. Rohdaten: `data/raw/wago/` (nicht im Repo). Die Nutzungsbedingungen von wago.tools habe ich nicht gefunden; die Daten gehören Blizzard (siehe Klausel-Hinweis in [03-datenquellen.md](03-datenquellen.md)).

- **Produkt:** Forever heißt bei wago.tools `wowf`. Neuester Build zum Abrufzeitpunkt: **1.60.1.70862** (7.11.2026). Es gibt 12 Builds seit 13.10.2026, aktuell mehrere neue pro Woche.
- **Geladen (alle vorhanden):** QuestXP, QuestMoneyReward, QuestV2, QuestInfo, QuestSort, AreaTable, Map, UiMap, TaxiNodes, TaxiPath, TaxiPathNode, ExpectedStat, ExpectedStatMod, ContentTuning, ContentTuningXExpected, CreatureDifficulty.
- **Nicht gefunden unter den geratenen Namen:** `XpBase`, `PlayerXp`, `Exp` (HTTP 400). Die XP-Kurve pro Level steht also nicht unter diesen Namen. Der richtige Tabellenname ist unbekannt.

### Was die Tabellen liefern

| Tabelle | Inhalt | Nutzen für uns |
|---|---|---|
| `QuestXP` | 100 Zeilen (Level) × 10 Schwierigkeitsstufen (`Difficulty_0..9`). Beispiel Level 60: Stufe 1 = 660, Stufe 4 = 4.950, Stufe 7 = 9.950 | Quest-XP **pro Level und Schwierigkeitsstufe**. Welche Stufe eine bestimmte Quest hat, steht hier nicht. |
| `TaxiNodes`, `TaxiPath` | 101 Flugpunkte mit Position, 328 Verbindungen mit Kosten | Reisezeit-Modell (Flugwege) |
| `TaxiPathNode` | Wegpunkte der Flugrouten (ca. 768 KB) | Flugzeit-Schätzung |
| `AreaTable`, `Map`, `UiMap` | Gebiete und Karten | Zonen- und Koordinatenzuordnung |
| `ExpectedStat`, `ExpectedStatMod` | Erwartete Werte pro Level (Kreaturen-Leben, Schaden, Spieler-Leben usw.) | Näherung für Kampfdauer pro Mob-Level |
| `ContentTuning` | Skalierungsdaten, Spalte `XpMultQuest` | evtl. Quest-XP-Multiplikator |
| `CreatureDifficulty` | nur 189 Zeilen | zu klein, Kreaturen kommen aus der Questie-Tabelle |
| `QuestV2`, `QuestInfo`, `QuestSort`, `QuestMoneyReward` | Hilfstabellen | Quest-Kategorien, Gold-Belohnung nach Stufe |

### Wichtigster Befund

**Die Quest-XP einer einzelnen Quest steht nicht im Client.** `QuestXP` enthält nur die Tabelle „Level × Schwierigkeitsstufe". Welche Stufe eine Quest hat, kommt vom Server und steht weder in diesen Tabellen noch in der QuestieDB. Für **Quest-XP pro Quest** brauchen wir daher ForeverDB, Wowhead oder Messwerte aus dem Spiel. Ein Rückgriff auf Classic-Werte ist für die ~1.000 neuen Quests nicht möglich und für alte Quests unsicher, weil Blizzard laut Beta-Notizen einzelne XP-Quellen (z. B. in Dungeons) geändert hat.

### XP-Kurve und Kill-XP (Fremdquellen, noch nicht gegen den Client geprüft)

- Mehrere Fanseiten nennen dieselbe XP-Tabelle: Level 1→2 braucht 400 XP, 10→11 braucht 7.600, 40→41 braucht 90.700. Insgesamt 4.084.700 XP bis Level 60. Ein Blizzard-Entwickler wird mit „we did not change the experience curve" zitiert **(unbestätigt)**.
- Kill-XP für einen Mob auf eigenem Level: `5 × Level + 45` (Classic-Formel, vom Wowhead-Rechner bestätigt). In einer vollen Gruppe wird sie durch 5 geteilt und mit 1,4 multipliziert. Die Abweichungen für Mob-Level über und unter dem eigenen Level müssen noch aus einer verlässlichen Quelle kommen.
- Zum Prüfen im Spiel taugt `UnitXPMax("player")` auf dem jeweiligen Level.
- **Messwert aus dem Spiel (Nutzer, 2026-11-07):** Auf Level 16 liefert `UnitXPMax("player")` **16.000**. Das passt zur Classic-Kurve (16→17 = 16.000, aus dem Gedächtnis, nicht gegen die Fan-Tabelle geprüft). Ein einzelner Punkt, weitere Level stehen aus.

## Quest-XP und Drop-Raten in den QuestieDB-Support-Daten

Auswertung: `pipeline/spike/xp_drop_coverage.py`. Quelle: `data/raw/QuestieDB/support/Forever/`.

- **`QuestXP/xpDB-classic.lua`:** Zuordnung Quest-ID → {Quest-Level, XP} für **3.494 Quests**. Der Name sagt „classic": Die Werte stammen aus Classic und wurden nicht für Forever neu gemessen. Der Kopfkommentar der Datei vergleicht Classic-, TBC- und Wrath-Werte.
- **`DropTables/classicItemDrops.lua`:** Drop-Raten in Prozent als Item → NPC → Rate, laut Datei automatisch aus Wowhead-Daten erzeugt. **1.219 Items, 15.355 Einträge.** Dazu `itemDropCorrections.lua` für manuelle Korrekturen. Auch das ist Classic-Stand.
- **NPC-Tabelle:** 11.511 von 13.417 NPCs haben Level-Angaben, 9.673 haben Spawn-Positionen.

| | Classic-Basis (4.244) | Neue Forever-Quests (989) |
|---|---|---|
| Quest-XP vorhanden | 3.494 (82,3 %) | **0** |
| Quests mit Item-Ziel | 2.131 | 444 |
| …davon alle Items mit Drop-Daten | 1.139 | **13** |
| …davon mindestens ein Item mit Drop-Daten | 1.335 | **21** |

### Einordnung

- Für die **bekannten Classic-Quests** liegt brauchbares Material vor: bei 82 % Quest-XP und bei etwa zwei Dritteln der Item-Quests Drop-Raten. Das reicht für einen ersten XP/h-Prototyp.
- Für die **neuen Forever-Quests** gibt es weder XP noch Drop-Raten. Sie müssten aus ForeverDB oder Wowhead kommen. Der Nutzer schätzt, dass die neuen Quests nicht viel ausmachen. Bis zur Klärung können sie in der Bewertung mit einer vorsichtigen Schätzung geführt oder ausgeschlossen werden.
- **Annahme mit Risiko:** Dass die Classic-XP-Werte in Forever unverändert gelten, ist **nicht belegt**. Blizzard hat laut Beta-Notizen einzelne XP-Quellen geändert. Bei 14 Quests weicht schon das Quest-Level in den Forever-Daten von der Classic-XP-Tabelle ab.
- **Fehlende XP bei 750 Classic-Quests** (17,7 %): Ursache noch nicht untersucht (mögliche Gründe: Quests ohne Level, Dungeon- oder Spezialquests, unvollständige Tabelle).
- **Stichprobe im Spiel:** Eine Quest abgeben und die XP mit dem Eintrag vergleichen. So sieht man, ob die Classic-Werte stimmen.

## Meilenstein 1: Normalisierung und Prüfung (umgesetzt)

Code: `pipeline/normalize/normalize.py` (Stufe 2), `pipeline/validate/validate.py` (Stufe 4), gemeinsamer Lua-Tabellen-Parser in `pipeline/common/luatable.py`. Aufruf vom Repo-Root: `python -m pipeline.normalize.normalize`, dann `python -m pipeline.validate.validate --zones 9,12`. Laufzeit der Normalisierung rund 4 Sekunden. Ausgabe in `data/normalized/` (nicht im Repo), Bericht in `data/reports/validation_report.md`.

**Zwischenformat:** `quests.json`, `npcs.json`, `objects.json`, `items.json`, `drops.json`, `quest_xp_table.json`, `meta.json`. Jeder Datensatz trägt `source`. Quest-Ziele sind getrennt nach Kreatur, Objekt und Item.

**Prüfergebnis (alle 5.233 Quests):**

- **Harte Fehler: keine**, nachdem zwei Datenfehler bereinigt wurden:
  - 2 Quests nennen sich selbst als Vorquest (Selbstverweis, wird entfernt).
  - 12 Vorquest-Kanten verlaufen zwischen sich gegenseitig ausschließenden Quests (Varianten derselben Kette, z. B. Schamanen-Quest „Call of Earth"). Sie erzeugten scheinbare Zyklen und werden ignoriert.
- **Kreuzprüfung zweier Quellen:** Bei 3.492 von 3.494 Quests mit XP-Angabe kommt der XP-Wert in der Zeile der Client-Tabelle `QuestXP` für das Quest-Level vor. Das stützt die Annahme, dass die Classic-XP-Werte in Forever grundsätzlich passen. Es beweist nicht, dass sie für jede Quest stimmen.
- **Warnungen:** 3 Vorquest-Verweise zeigen auf nicht vorhandene Quests. 32 Quests haben ein Mindestlevel über dem Quest-Level. Bei 14 Quests weicht das Quest-Level von dem der XP-Tabelle ab.
- **Lücken:** 287 Quests ohne Abgabeort und 174 ohne Annahmeort. 10 Annahme- und 15 Abgabeorte haben keine Position.
- **Platzhalter:** 6 Quests mit `<NYI>` im Namen werden markiert (`placeholder: true`).
- **Falschmeldung gefunden und behoben:** Die erste Fassung der Platzhalter-Erkennung markierte auch echte Quests wie „Test of Faith" wegen des Worts „Test". Das Muster wurde eingeschränkt.

**Zonenbericht (Northshire Valley und Elwynn Forest, Zonen 9 und 12):** 74 Quests, Level 1–12, davon 45 mit XP-Angabe (Summe 19.060 XP), 7 mit Kill-Zielen, 33 mit Item-Zielen, 42 mit Vorquest. Die XP-Lücke in dieser Zone ist größer als im Gesamtbestand und muss untersucht werden.

## Meilenstein 3 (Prototyp): Einzelquest-Bewertung

Code: `pipeline/derive/derive.py`, Parameter: `pipeline/config/params.json`. Aufruf: `python -m pipeline.derive.derive`. Ausgabe: `data/derived/quest_eval.json` (nicht im Repo) und `data/reports/derived_report.md`. Betrachtet werden die 74 Quests von Northshire Valley und Elwynn Forest bis Level 12.

**Was der Prototyp tut:** Für jede Quest einzeln: Quest-XP, Mob-XP durch Kills (inkl. Drop-Raten für Item-Ziele), Weg (Annahme → Zielgebiet → Abgabe) und Zeit. Daraus XP/h, so als würde die Quest allein gemacht.

**Wichtig: Die absoluten Zahlen sind noch nicht belastbar.** Alle Zeit- und Größenwerte sind Annahmen (siehe `params.json`):
- Laufgeschwindigkeit 7 yd/s, Zonenbreite 1.800 yd (geraten, bestimmt alle Wegzeiten), 12 s pro Kill, 8 s pro Objekt-Interaktion, 25 s Overhead pro Quest, 35 % Drop-Rate bei fehlenden Daten.
- Mob-XP: Bei gleichem Level `5 × Level + 45` (Wowhead-Rechner). Die Abhängigkeit vom Level-Unterschied stammt aus der Classic-Formel aus dem Gedächtnis.
- Stückzahlen kommen aus einer Heuristik über den Zieltext (erste Zahlen im Text). Bei 14 von 74 Quests ist die Menge geraten, bei einer wurde eine unplausible Zahl (>40) korrigiert.
- Das Spielerlevel wird gleich dem Quest-Level gesetzt.
- Die Bewertung ignoriert, dass man zum Quest-Geber erst hinkommen muss und dass Quests zusammen erledigt werden (Bündel, Synergien). Sie ist ein **Rauchtest**, kein Routenmodell.

**Ergebnisse (Median 17.007 XP/h, 90. Perzentil 40.496, 10. Perzentil 6.231):**
- Plausible Reihenfolge: Reine Lieferquests ohne Weg und Quests mit Kills auf kurzer Strecke vorne, weite Botengänge mit wenig XP hinten.
- Vorne stehen auch Quests mit **geschätzter** XP (Hinweis `g` in der Tabelle). Die Schätzung nimmt die typische Schwierigkeitsstufe 5 aus `QuestXP` und kann daneben liegen.
- Rund die Hälfte der Quests hat mindestens einen Konfidenz-Hinweis.

### Wichtiger Befund zu den neuen Quests

In Northshire Valley und Elwynn Forest hat **fast jede dritte Quest keine XP-Angabe** (29 von 74), und es sind fast alle neue Forever-Quests (IDs 91xxx–99xxx), dazu zwei Classic-Tauschquests. Der Nutzer hatte vermutet, dass die neuen Quests nicht viel ausmachen. Für die **Startgebiete** stimmt das offenbar nicht: Von den 989 neuen Quests liegen 246 auf Level 0–9 und 221 auf Level 10–19. Das spricht dafür, die ForeverDB-Anbindung für Quest-XP früh anzugehen.

### Nächste Verbesserungen am Modell

1. Kalibrieren: Zonenbreite und Lauftempo (z. B. Laufzeit von der Nordshire Abbey nach Goldshire im Spiel stoppen), Kill-Zeit pro Mob, Kill-XP an ein paar Mobs messen.
2. Echte Mengen für Ziele: ForeverDB oder Questie-Questlog-Daten statt Text-Heuristik.
3. Bündel und Routen statt Einzelquests: Überlappungsindex, Cluster, Reihenfolge, Vorquests (die Bewertung einer Quest hängt von dem ab, was vorher passiert).
4. Quest-XP-Faktor, wenn das Spielerlevel über dem Quest-Level liegt (graue Quests).

## Meilenstein 3 (Prototyp, Teil 2): Bündel und Routen-Simulation

Code: `pipeline/derive/route.py`. Aufruf: `python -m pipeline.derive.route --target-level 10`. Bericht: `data/reports/route_report.md`. Gilt für einen Menschen in Northshire Valley und Elwynn Forest, Start bei Marshal McBride.

**Was die Simulation tut:**
1. **Keine festen Gruppen und keine Schwellen** (Vorgabe des Nutzers, 7.11.2026). Die erste Fassung gruppierte Quests nach dem Quest-Geber-Ort mit festem Radius (150 yd). Das ist ersetzt worden.
2. Jede verfügbare Quest ist ein möglicher **Startpunkt** eines Bündels. Von dort sucht eine lokale Suche: Quest hinzufügen oder entfernen, solange die XP/h des Bündels steigen. Entfernung, gemeinsame Mobs und Zeit gehen allein über das Zeitmodell ein. Gleiche Mobs aus mehreren Quests zählen nur einmal (Maximum statt Summe, der Verstärkungseffekt).
3. Das Bündel mit den meisten XP/h über alle Startpunkte wird „gemacht". Dann Level-Ups und freigeschaltete Folgequests (Vorquests, Mindestlevel, Rasse, exklusive Quests) neu berechnen und wiederholen.
4. Quests, die nie gewählt werden, sind „übersprungen". Es gibt keine feste Regel dafür, es ergibt sich aus der Bewertung.
5. Quest-XP sinkt, wenn das Spielerlevel über dem Quest-Level liegt (Annahme-Tabelle in `params.json`). Mob-XP wird mit dem aktuellen Level berechnet.

**Ergebnis (unter den Annahmen aus `params.json`, Stand 7.11.2026):**

| Variante | Zeit bis Level 10 | Quests | Schritte |
|---|---|---|---|
| mit dynamischen Bündeln | **63 min** | 33 | 10 |
| jede Quest einzeln | 82 min | 24 | 24 |

(Die erste Fassung mit festem Hub-Radius lag bei 78 min bzw. 5 % Vorteil. Ohne feste Gruppen bündelt die Suche deutlich mehr und der Vorteil steigt auf etwa 23 %.)

Von 70 Quests mit Mindestlevel ≤ 10 wurden bei der Bündel-Variante 35 nicht gemacht.

**Vorsicht beim Bündel-Vorteil:** Das Modell vereinfacht Abgabe-Wege (es nimmt den Schwerpunkt aller Abgabeorte) und Annahme-Wege (Schwerpunkt der Quest-Geber). Große Bündel profitieren davon vermutlich zu stark. Der Wert von 23 % ist eine Obergrenze und kein Ergebnis. Das nächste Modell sollte Annahme- und Abgabewege einzeln als Route durch die Orte rechnen.

**Wie belastbar ist das?** Nicht belastbar, solange nichts kalibriert ist:
- Alle Zeitwerte, die Zonenbreite und die Level-Differenz-Faktoren sind Annahmen.
- Neue Quests ohne XP sind mit der typischen Stufe geschätzt.
- Die XP-pro-Level-Werte für Level 1–13 stammen zum Teil aus dem Gedächtnis (gesichert: Level 1, Level 16 und die Summe bis Level 10).
- Es wird nicht gleichzeitig mit mehreren Hubs geplant, und Rückwege zu Abgabe-NPCs an anderen Orten sind vereinfacht.
- Ein Vergleich mit echten Spielzeiten fehlt. Wie lange hast du bis Level 10 gebraucht? Das wäre der erste Plausibilitätstest.

## Meilenstein 3 (Prototyp, Teil 3): Routenplaner, Bündelung entsteht aus der Planung

Vorgabe des Nutzers (7.11.2026): Die Bündelung soll sich aus einer **schlauen Routenplanung ergeben**, nicht aus vorgegebenen Bündeln oder Gruppen. Deshalb ersetzt `pipeline/derive/planner.py` die Bündel-Logik aus `route.py` (die bleibt als Vergleich erhalten). Aufruf: `python -m pipeline.derive.planner --target-level 10`. Bericht: `data/reports/planner_report.md`.

**Funktionsweise:**
- Der Planer sucht eine **Abfolge von Handlungen**: Quest annehmen, Mobs töten, Objekt-/Erkundungsziel erledigen, Quest abgeben. Es gibt keine Gruppen, keinen Radius und keine Schwellenwerte.
- Alle offenen Quests teilen sich Kills automatisch. Ob mehrere Quests gleichzeitig offen sind, entscheidet allein die Zeit.
- Suche per Strahlsuche (Beam Search) nach Zeit-Eimern. Die Strahlbreite ist ein Suchparameter, keine Spielregel.
- Bewertung von Zwischenständen: bisherige XP plus der anteilige Fortschritt offener Quests, abzüglich der Zeit fürs Abgeben, umgerechnet in XP mit der bisherigen Rate des Plans (Opportunitätskosten). Die erste Fassung ohne diesen Abzug stapelte bis zu 24 offene Quests und war schlechter als „eine Quest zur Zeit".
- Als Gegenprobe läuft derselbe Planer mit der Einschränkung „immer nur eine Quest offen".

**Ergebnis (Mensch, Level 1 → 10, unter den geratenen Annahmen):**

| Strahlbreite | frei | eine Quest zur Zeit | Vorteil |
|---|---|---|---|
| 15 | 76,9 min | 85,8 min | 10 % |
| 40 | 77,4 min | 83,3 min | 7 % |
| 150 | 65,2 min | 72,6 min | 10 % |
| 600 | **64,0 min** | **72,6 min** | **12 %** |

- Die Gegenprobe (eine Quest zur Zeit) hat bei Breite 150 und 600 denselben Wert, die freie Suche ändert sich zwischen 150 und 600 nur um ca. 1 Minute. Das spricht dafür, dass die Suche bei Breite 150 weitgehend konvergiert ist. Bei kleiner Breite (15, 40) ist sie es nicht.
- Im freien Plan sind bis zu **8 Quests gleichzeitig offen**, und es gibt 2 Handlungen, bei denen ein Kill-Block mehreren Quests hilft. Bündelung entsteht also aus der Suche, ohne dass jemand sie vorgibt.
- Von 70 Quests im Pool teilen sich nur 5 Mob-Typen mehrere Quests (Murloc, Kobold Tunneler, Prowler, Kobold Vermin, Defias Rogue Wizard). Der Bündel-Vorteil kommt daher überwiegend aus gebündelten Wegen (annehmen und abgeben auf einem Rundgang), kaum aus echten Kill-Überschneidungen.
- Die frühere Aussage „23 % schneller durch Bündel" (feste Gruppen mit Schwerpunkt-Näherung bei den Wegen) war **zu optimistisch** und ist durch diesen Wert abgelöst: rund 10–12 %.

**Grenzen:** Alle Zeitwerte, die Zonenbreite und Level-Faktoren sind weiter Annahmen. Der Pool enthält nur Northshire und Elwynn. Der Planer rechnet die Zeit für Wege zwischen den Orten einzeln, aber Mobs werden im Schwerpunkt ihrer Spawns angelaufen. Die Laufzeit steigt mit der Strahlbreite (Breite 600: etwa 50 Sekunden für Level 1–10). Für ein Echtzeit-Add-on muss die Planung offline oder stark vereinfacht laufen.

## Kalibrierung ohne Messung: Kartengröße aus den Client-Tabellen

Die bisher geratene Zonenbreite (1.800 yd, quadratisch) ist durch Werte aus der Client-Tabelle `UiMapAssignment` (wago.tools, Build 1.60.1.70862) ersetzt. Für die Elwynn-Forest-Karte (UiMap 1429) ergibt sich:

- Weltkoordinaten-Bereich: X von −10.254,17 bis −7.939,58 (2.314,6 yd), Y von −1.935,42 bis 1.535,42 (3.470,8 yd).
- Karte horizontal = Welt-Y-Bereich = **3.470,8 yd**, Karte vertikal = Welt-X-Bereich = **2.314,6 yd**. Karten-Prozent werden mit getrennten Faktoren je Achse in Yards umgerechnet (`zone_size_yards` in `params.json`).

**Plausibilitätsprüfung:** Der Flugpunkt „Northshire Abbey" liegt umgerechnet bei (44,3 | 41,0) auf der Karte, Marshal McBride bei (48,9 | 41,6): vertikal fast deckungsgleich, horizontal rund 150 yd daneben (der Flugpunkt ist ein Platzhalter in der Nähe). Der Abstand zwischen Marshal McBride und Innkeeper Farley in Goldshire beträgt damit rund 590 yd, bei 7 yd/s etwa 85 Sekunden, was zur üblichen Erfahrung für diesen Weg passt. Das ersetzt keine Messung, ist aber ein unabhängiger Anker. Die Laufgeschwindigkeit von 7 yd/s ist weiter eine Annahme (Standard-Laufgeschwindigkeit).

**Auswirkung:** Die Wege sind länger als vorher angenommen. Level 10 ist im Plan nach **80 min** erreicht (frei) bzw. 89 min (immer nur eine Quest offen), der Vorteil durch parallele Quests beträgt rund 10 %. Der Median der Einzelquest-Bewertung sinkt auf rund 14.600 XP/h.

**Kill-Zeit:** Die Kill-Zeit (12 s pro Mob) bleibt eine Annahme. Eine Messung mit dem derzeitigen, übermächtigen Charakter ist nicht aussagekräftig. Möglichkeit: später mit einem neuen Charakter oder aus Daten, die das Hilfs-Add-on mitschreibt.

## Meilenstein 3 (Prototyp, Teil 4): Spieler-Simulation mit Spawns, Kills unterwegs und Zufall

Auslöser (Nutzer, 7.11.2026): Wege addieren sich nicht einfach (z. B. mehrere Abgaben beim selben NPC, Teilstrecken), und 80 Minuten bis Level 10 kommen dem Nutzer „extrem kurz" vor. `pipeline/derive/planner.py` wurde zu einem Spieler-Modell erweitert:

- **Position als Zustand**, Wege als Linienzug durch die Stationen. Zwei Quests beim selben NPC annehmen oder abgeben kostet für die zweite 0 Weg. Liegt ein Ziel auf dem Weg zu einem anderen, kostet der Umweg nur die Differenz.
- **Mobs als echte Spawn-Punkte:** Anlaufen des nächsten Spawns, Laufen zwischen den Kills (mittlerer Nachbarabstand der Spawns), Warten auf Respawns, wenn mehr Kills gebraucht werden als Spawns da sind (`mob_respawn_seconds` = 120 s, Annahme).
- **Kills auf dem Weg:** Auf jeder Strecke werden Spawns benötigter (nicht-elitärer) Mobs im Korridor mitgenommen (`corridor_yards` = 40 yd, Annahme). Das wirkt auf alle offenen Quests, die den Mob brauchen.
- **Zufall:** Der gefundene Plan wird 300-mal nachgespielt. Für Item-Ziele werden Kills bis zum Drop gewürfelt (Summe von geometrisch verteilten Versuchen). Fehlt am Ende etwas, kostet es Zusatz-Kills plus Hin- und Rückweg.

**Ergebnis (Level 1 → 10, Strahlbreite 150, geratene Zeitwerte, echte Kartengröße):**

| Variante | Plan (Erwartungswert) | Mit gewürfelten Drops (Mittel) | 10–90 %-Quantil |
|---|---|---|---|
| frei geplant (bis zu 8 Quests offen) | **82 min** | **87 min** | 82–91 min |
| immer nur eine Quest offen | 96 min | 102 min | 98–106 min |

- Der Vorteil durch paralleles Arbeiten an Quests liegt bei rund 14 % (Erwartungswert).
- Der Zufall verlängert den Plan im Mittel um etwa 5–6 %. Der Plan rechnet mit Erwartungswerten, deshalb ist das Mittel der Nachspielungen immer etwas länger: Fehlende Items kosten mehr Zeit, als überzählige sparen.

**Einordnung der Zeit:** 82 Minuten gelten für einen Spieler, der die Route kennt und fehlerfrei spielt. Das ist ein **Optimalfall** und nicht die Erfahrung eines normalen Spielers. Vermutlich fehlt außerdem noch einiges, das die Zeit real verlängert: Ausruhen und Heilen nach Kämpfen, langsamere Kämpfe eines Level-1-Charakters (12 s pro Kill sind geraten), Tode und Laufwege zurück, Händler-/Lehrer-Stopps, Taschen, Zielsuche, Konkurrenz um Mobs. Für die neuen Quests ohne XP ist die XP geschätzt und könnte zu hoch liegen. Ein Vergleichswert aus dem Spiel (tatsächliche Spielzeit bis Level 10, mit Angabe, wie routiniert gespielt wurde) fehlt noch.

## Noch offen

- Die Pipeline soll den QuestieDB-Export reproduzierbar anstoßen können. Dafür fehlt noch eine dauerhafte Lösung: Die Berechtigung zum Ausführen des Repo-Lua, oder ein von uns eingerichtetes Lua 5.1 (z. B. scoop-Bucket `versions`, `lua51`).
- **Quest-XP pro Quest:** Quelle klären (ForeverDB-API ist der beste Kandidat, siehe oben).
- Richtigen Tabellennamen für die XP-Kurve pro Level finden oder die Kurve im Spiel prüfen.
- ForeverDB-Key beantragen, damit Lücken (fehlende Abgabeorte, Positionen, Vorquests) geschlossen und Stichproben gemacht werden können.
- Items und Drop-Raten: Struktur der Item-Tabelle auswerten, prüfen, ob Drop-Raten enthalten sind.
