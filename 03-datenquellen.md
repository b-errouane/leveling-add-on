# Datenquellen

Das Add-on soll auf öffentlichen Datenbanken beruhen. Hier steht, was gebraucht wird und welche Quellen infrage kommen. Alle Quellenangaben sind **(zu prüfen)**, da sie aus dem Gedächtnis kommen.

## Benötigte Daten

| Datenpunkt | Wozu | Verlässlichkeit |
|---|---|---|
| Quests je Gebiet/Zone | Welche Quests gibt es überhaupt, wo werden sie angenommen und abgegeben | meist gut |
| Quest-XP | Wert einer Quest | gut, aber abhängig von Spielerlevel (Skalierung) |
| Quest-Abhängigkeiten | Vor-/Folgequests, Level-, Ruf-, Klassen-, Rassen-Anforderungen | gut, einzelne Lücken möglich |
| XP pro Level | Wie viel XP bis zum nächsten Level | sehr gut (feste Tabelle) |
| Mob-XP | Wert eines Kills, abhängig von Mob-Level vs. Spielerlevel | Formel bekannt, je Version leicht verschieden |
| Mob-Spawns und Positionen | Wo gekämpft/gegrindet wird | gut, Dichte schwer messbar |
| Drop-Raten | Wie lange dauert es, Questitems zu bekommen | **unsicher**: meist Stichproben aus der Community |
| Wegpunkte, Flugpunkte, Reisezeiten | Laufwege in die Routenoptimierung | muss teils berechnet oder geschätzt werden |

## Mögliche Quellen

- **Wowhead** (inkl. Classic-Varianten): sehr umfangreich, Daten aus Spielersammlung. Nutzungsbedingungen und Scraping-Regeln prüfen.
- **Questie-Datenbank**: das Add-on Questie enthält eine aufbereitete Datenbank (Quests, NPCs, Objekte) als Lua-Dateien. Lizenz prüfen. Könnte die einfachste maschinenlesbare Quelle sein.
- **Server-Emulator-Datenbanken** (z. B. CMaNGOS, AzerothCore, TrinityCore): offene Dumps mit Quests, Kreaturen, Loot-Tabellen. Gute Kandidaten für strukturierte Daten, aber Qualität variiert je Projekt und Version.
- **Offizielle Blizzard-API / Game-Client-Daten (DBC/DB2)**: verlässlichste Quelle für Konstanten wie XP-Tabellen. Zugriff und Extraktion prüfen.
- **Community-Wikis** (Wowpedia, Warcraft Wiki): ergänzend für Formeln und Erklärungen.

## Recherche zu WoW Forever (Stand 2026-11-07)

Ergebnis einer ersten Websuche. Es wurden nur Suchergebnisse gelesen, keine Lizenztexte oder API-Bedingungen im Volltext. **Vor jeder Nutzung die Originalseiten prüfen.**

| Quelle | Was sie liefert | Zugang | Lizenz / Bedingungen | Einschätzung |
|---|---|---|---|---|
| **QuestieDB** ([GitHub](https://github.com/Questie/QuestieDB), [CurseForge](https://www.curseforge.com/wow/addons/questiedb)) | Quests, NPCs, Objekte, Items, auch Forever (v1.0.11 vom 5.11.2026) | Lua-Dateien öffentlich, Generator im Repo | **GPL-3.0** | Beste maschinenlesbare Basis. GPL gilt vermutlich auch für abgeleitete Daten und Code, das beeinflusst die Lizenz unseres Add-ons. |
| **ForeverDB** ([API](https://foreverdb.net/developers)) | Quests, Items und weitere Forever-Daten als JSON | Lesender API-Zugang mit Key (Battle.net-Login, Zweck angeben) | **Quellenangabe Pflicht** (sichtbarer Link zu foreverdb.net), weitere Bedingungen nicht gelesen. Daten aus dem Client gehören Blizzard. | Gute Ergänzung für neue Quests. Kein Bulk-Download gefunden, Rate-Limits unbekannt. |
| **tyler3497/forever-quests** ([GitHub](https://github.com/tyler3497/forever-quests)) | Quest-Datenbank für Forever, Hauptteil aus QuestieDB, getrennter Teil aus der ForeverDB-API | öffentlich | GPL-3.0 | Vorlage, wie man beides trennt. Vollständigkeit unbekannt. |
| **Sempson/ForeverQuestDB** ([GitHub](https://github.com/Sempson/ForeverQuestDB)) | Quest-DB aus Spieler-Exporten (Addon „Forever Quest Sort") | öffentlich | **CC0-1.0** | Lizenzmäßig am freiesten. Qualität und Abdeckung unbekannt. |
| **Client-Tabellen (DB2)** via [wago.tools](https://wago.tools) | Konstanten wie XP-Tabellen, ggf. Quest- und Kreaturendaten | wago.tools-Dateien/API, lokale Tools (z. B. wow.tools.local, WoWDBDefs) | Daten gehören Blizzard. robots.txt von wago.tools sperrt laut einem Projekt die CSV-Downloads, die API liefert Rohdateien. | Verlässlichste Quelle für feste Werte. Ob `QuestXP`/Kreaturentabellen in Forever vorliegen und was sie enthalten, ist offen. Rechtlich siehe unten. |
| **Wowhead Forever** | umfangreiche Daten, auch Drop-Raten | nur Webseite, keine offizielle API gefunden | Nutzungsbedingungen **nicht gelesen**. Wowhead wehrt laut Forendiskussion Scraping ab. | Nicht automatisiert abziehen, bevor die Bedingungen geklärt sind. |

**ForeverDB-Pflicht:** Überall, wo ForeverDB-Daten gesehen werden (Add-on, Dokumente, Berichte, Auszüge), muss https://foreverdb.net als Quelle genannt und verlinkt werden. Umsetzung in [08-datenpipeline.md](08-datenpipeline.md).

### Was daraus folgt

- **Fest-Werte** (XP pro Level, Quest-XP-Skalierung, Kill-XP-Formel) sollten aus den Client-Tabellen kommen, nicht aus Fremdseiten.
- **Quests, NPCs, Positionen** am besten aus QuestieDB (Forever-Version) plus ForeverDB für Lücken. Neue Quests sind laut Fanseiten die schwache Stelle.
- **Drop-Raten** bleiben die unsicherste Größe. Kandidaten: Wowhead-Werte (rechtlich offen), ForeverDB, eigene Auswertung aus Spielerdaten.
- **Lizenzfolge:** Wer GPL-3.0-Daten übernimmt, muss sein Ergebnis voraussichtlich ebenfalls unter GPL stellen. Das ist für ein privates Projekt unkritisch, für eine Veröffentlichung eine bewusste Entscheidung. **(zu prüfen, keine Rechtsberatung)**

### Rechtliche Punkte und Add-on-Regeln

- **Blizzard-Developer-API-Bedingungen** enthalten laut Forum die Klausel „You May Not Data Mine Blizzard Products Or Services". Ob das Auslesen der Client-Dateien oder die Nutzung von wago.tools darunter fällt, ist **ungeklärt**.
- **Add-on-Regeln:** Blizzard erlaubt Add-ons, die Informationen anzeigen, die dem Spieler ohnehin zugänglich sind. Add-ons, die Gameplay **automatisieren**, gelten als Verstoß. Unser Add-on gibt nur Anweisungen und steuert nichts, bleibt also auf der sicheren Seite. Die Regeln ändern sich aber (Berichte über neue Einschränkungen in „Midnight"), also die aktuelle offizielle Policy prüfen. Quellen waren überwiegend Kommentar- und Forenseiten.

## Fragen

- Welche Quelle liefert **alle** Felder in einem Format? Eine Mischung erhöht Aufwand und Widersprüche.
- Wie gehen wir mit **Widersprüchen** zwischen Quellen um (Priorität definieren)?
- Wie oft müssen Daten aktualisiert werden (Patches)?
- Lizenz und Nutzungsbedingungen jeder Quelle klären, bevor wir etwas automatisiert abziehen.

## Idee: Daten-Pipeline

1. Rohdaten aus der gewählten Quelle holen und unverändert ablegen.
2. In ein einheitliches Zwischenformat überführen (z. B. JSON/Lua-Tabellen).
3. Automatisch prüfen: Referenzen vollständig, keine zyklischen Quest-Abhängigkeiten, XP-Werte plausibel.
4. Daraus Guides und Add-on-Daten generieren.
