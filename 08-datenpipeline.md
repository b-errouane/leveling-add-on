# Datenpipeline (Plan)

Ziel: Aus öffentlichen Quellen automatisch ein kompaktes Daten-Paket für das Add-on erzeugen, inklusive Vorberechnungen für die XP/h-Bewertung (siehe [04-routenlogik.md](04-routenlogik.md), [06-datenmodell.md](06-datenmodell.md)). Alles läuft **offline auf dem PC**, nicht im Spiel. Die Pipeline muss **wiederholbar** sein: neuer Patch oder neue Daten, Pipeline neu laufen lassen, neues Paket.

Annahmen: Projekt privat, GPL-3.0 akzeptiert (siehe [02-offene-fragen.md](02-offene-fragen.md)). Quellen und ihr Stand: [03-datenquellen.md](03-datenquellen.md).

## Überblick

```
 Quellen                Stufe 1          Stufe 2         Stufe 3        Stufe 4          Stufe 5
 ───────                ───────          ───────         ───────        ───────          ───────
 QuestieDB (Lua)  ─┐
 ForeverDB (API)  ─┼─►  Holen   ─►  Normalisieren ─► Zusammenführen ─► Prüfen ─► Ableiten ─► Ausgeben
 Client-Tabellen  ─┤    (roh,       (einheitliches    (Priorität,      (Regeln,   (Zeiten,     (Lua-Pakete
 Eigene Messdaten ─┘    unverändert) JSON)             Herkunft)       Berichte)  Index, Plan)  pro Zone)
```

Jede Stufe liest nur die Ausgabe der vorherigen und schreibt in einen eigenen Ordner. So lässt sich jede Stufe einzeln wiederholen und prüfen.

## Stufe 1: Holen (roh)

| Quelle | Wie | Besonderheit |
|---|---|---|
| **QuestieDB** | GitHub-Repo klonen oder Forever-Release von CurseForge laden | Lua-Tabellen, Version im Dateinamen merken (z. B. v1.0.11) |
| **ForeverDB** | JSON-API mit Key (Header `X-API-Key`) | **Key muss der Nutzer beantragen** (Battle.net-Login auf foreverdb.net/developers, Zweck angeben). Höfliche Rate, Antworten cachen. |
| **Client-Tabellen** | DB2-Dateien über die wago.tools-API laden, mit WoWDBDefs/DBCD o. ä. lesen | Welche Tabellen für XP, Quests, Kreaturen in Forever existieren, ist offen (Spike in Meilenstein 0). |
| **Eigene Messdaten** (später) | Export aus dem Spiel (z. B. per Hilfs-Add-on SavedVariables) | Für Drop-Raten, Laufzeiten, Kill-Zeiten. Optional. |

Regeln:
- Rohdaten werden **unverändert** abgelegt, mit **Abrufdatum, Quelle, Version/Build** in einer Metadatei.
- Nichts im Rohordner wird von Hand bearbeitet.
- Der Rohordner ist nicht Teil des endgültigen Pakets.

## Stufe 2: Normalisieren

Jede Quelle wird in dasselbe **Zwischenformat** gebracht (JSON), getrennt nach Entitäten:

- `quests` (Id, Name, Level, Mindestlevel, Voraussetzungen, Vor-/Folgequests, Exklusivität, Fraktion/Rasse/Klasse, Annahme-/Abgabe-NPC oder -Objekt, XP-Belohnung, Objectives)
- `objectives` (Typ, Menge, Quelle(n) als Verweise)
- `creatures` (Id, Name, Level-Bereich, Spawns/Positionen, Fraktion, Loot-Verweis)
- `objects` (Id, Position, Respawn)
- `items` (Id, Name, Quellen mit Drop-Rate)
- `zones` (Id, Name, Hierarchie, Levelbereich)
- `xp_tables` (XP pro Level, Quest-XP-Skalierung, Kill-XP-Parameter)
- `travel` (Flugpunkte, Verbindungen, ggf. Portale/Zeppeline)

Wichtig: **Jedes Feld behält seine Herkunft** (`source`: questie / foreverdb / client / manual). So bleibt später nachvollziehbar, woher ein Wert kommt und wo Widersprüche liegen.

## Stufe 3: Zusammenführen

Ziel: pro Entität ein Datensatz aus mehreren Quellen.

- **Schlüssel:** Quest-, NPC-, Objekt- und Item-IDs sind der gemeinsame Nenner. Wo IDs nicht passen, gelten Name plus Ort als Notbehelf und wird als Warnung gemeldet.
- **Priorität pro Feldtyp** (Vorschlag, anpassbar):
  - Feste Werte (XP-Tabellen, Level): Client-Tabellen vor allem anderen
  - Quest-Struktur, NPCs, Positionen: QuestieDB, ergänzt durch ForeverDB
  - Neue Forever-Quests: ForeverDB, wenn QuestieDB sie nicht kennt
  - Drop-Raten: ForeverDB oder Messdaten, bei Unsicherheit mit Streuung markieren
- **Widersprüche** werden nicht stillschweigend aufgelöst, sondern in einen Bericht geschrieben (Quelle A sagt X, Quelle B sagt Y, gewählt wurde Z).
- **Lücken** (z. B. Quest ohne Koordinaten) werden gelistet und im Paket als „unvollständig" markiert, damit die Bewertung sie vorsichtig behandelt oder ausschließt.

## Stufe 4: Prüfen

Automatische Prüfungen, die die Pipeline abbrechen oder Warnungen erzeugen:

- Alle Verweise gültig (jede Quest-Quelle existiert als Kreatur/Objekt/Item)
- Quest-Abhängigkeitsgraph **zyklenfrei**, jede Quest grundsätzlich erreichbar
- Level-Werte plausibel (Quest-Level nahe Mindestlevel, XP wächst mit Level)
- Positionen liegen in der angegebenen Zone
- Keine Quest ohne Annahme- und Abgabeort
- Stichproben gegen eine zweite Quelle (z. B. Quest-XP laut ForeverDB gegen Client-Tabelle)
- Berichte: Anzahl Quests je Zone, Anteil unvollständiger Datensätze, Anzahl Quellenwidersprüche

Ergebnis ist ein **Qualitätsbericht** pro Lauf. Er zeigt auch, wie gut die neuen Forever-Quests abgedeckt sind.

## Stufe 5: Ableiten (Vorberechnung)

Aus den bereinigten Daten werden die Größen berechnet, die das Add-on frei Haus mitbringt:

1. **Quest-XP je Spielerlevel** (mit Skalierung gegen niedrigere Level)
2. **Kill-XP je Mob und Spielerlevel** (Formel und Parameter aus Client-Tabellen bzw. Prüfung gegen Messwerte, **nicht aus dem Gedächtnis übernehmen**)
3. **Erwartete Dauer je Objective:** Kills bis Drop, Zeit pro Kill, Respawn, Laufzeit im Gebiet. Parameter wie Kampftempo und Lauftempo stehen in einer **Konfigurationsdatei** und sind einstellbar.
4. **Reisezeiten** zwischen Orten/Clustern (Wegenetz, Flugpunkte, Luftlinie mal Faktor als Näherung)
5. **Cluster/Hubs** (Gruppen von Questgebern und Zielen nach Nähe)
6. **Überlappungsindex:** Welche Quests teilen Mobs, Items, Objekte, Orte, Hubs (siehe [06-datenmodell.md](06-datenmodell.md))
7. **Abhängigkeitsgraph** in kompakter Form (Vorquests, Folgequests, Level, Exklusivität)
8. **Referenzplan:** Eine vorberechnete Soll-Route mit erwartetem Level/XP über der Zeit, die das Add-on live mit dem Ist-Stand vergleicht
9. **Unsicherheit:** Wo Werte geschätzt sind (Drop-Raten), wird neben dem Erwartungswert eine Streuung oder ein Vertrauensgrad abgelegt.

Die Schätzmodelle (3 und 4) sind bewusst einfach und über Parameter einstellbar. Sie werden später mit echten Läufen nachkalibriert.

## Stufe 6: Ausgeben

- **Lua-Datendateien** für das Add-on, **pro Zone oder Level-Band** aufgeteilt, damit nur das Nötige geladen wird.
- Kompakte Struktur (numerische IDs, flache Tabellen, wenig Text). Namen wenn möglich aus dem Spiel selbst holen statt zu speichern.
- `Manifest` mit Datenstand: Quellen, Versionen, Build-Nummer, Erzeugungsdatum, Prüfbericht-Zusammenfassung. Das Add-on kann den Datenstand anzeigen.
- Größe prüfen: Ladezeit und Speicher im Spiel messen **(offen, siehe [06-datenmodell.md](06-datenmodell.md))**.

## Ordnerstruktur (Vorschlag)

```
leveling-add-on/
├─ pipeline/            Code der Pipeline
│   ├─ fetch/           Stufe 1
│   ├─ normalize/       Stufe 2
│   ├─ merge/           Stufe 3
│   ├─ validate/        Stufe 4
│   ├─ derive/          Stufe 5
│   ├─ emit/            Stufe 6
│   └─ config/          Parameter (Tempo, Prioritäten, Quellen)
├─ data/
│   ├─ raw/             unverändert, mit Metadaten
│   ├─ normalized/
│   ├─ merged/
│   └─ reports/         Prüf- und Qualitätsberichte
├─ addon/               das eigentliche WoW-Add-on, enthält die erzeugten Datendateien
└─ docs/ oder *.md      diese Dokumente
```

## Werkzeuge

- **Sprache der Pipeline:** Python (gut für Daten, JSON, HTTP, Tests). Alternative Node/TypeScript. Empfehlung vorläufig Python, **zu klären: ist Python auf dem Rechner vorhanden?**
- **Lua-Dateien lesen:** QuestieDB-Tabellen sind Lua. Dafür einen Lua-Parser (z. B. Python-Bibliothek) oder ein eingebettetes Lua verwenden. Beides zu testen.
- **DB2 lesen:** WoWDBDefs mit einem vorhandenen Leser (DBCD/wow.tools.local oder Python-Leser). Zu testen.
- **Tests:** Pytest für die Prüfregeln und Stichproben. Add-on-seitig ein Lua-Test mit nachgebauter WoW-API für die Bewertungslogik, damit nicht alles im Spiel getestet werden muss.

## Meilensteine

| Nr. | Ziel | Ergebnis |
|---|---|---|
| **0** | **Spike (Machbarkeit)** | QuestieDB (Forever) einlesen, eine Startzone ausgeben. Prüfen, welche DB2-Tabellen verfügbar und lesbar sind. ForeverDB-Key beantragen und eine Quest abrufen. |
| **1** | Normalisierung einer Zone | Zwischenformat steht, Prüfbericht für diese Zone |
| **2** | Zusammenführen und Prüfen | Quellen gemischt, Widersprüche und Lücken berichtet |
| **3** | Ableitung für Level 1–10 | XP, Dauer, Reisezeit, Überlappungsindex, Referenzplan für den ersten Abschnitt |
| **4** | Ausgabe als Lua und Laden im Spiel | Add-on-Rohgerüst liest die Daten, zeigt den nächsten Schritt, TomTom-Pfeil gesetzt |
| **5** | Ausbau auf alle Zonen und Level 1–60 | Vollständiges Paket |

Der erste echte Prüfstein ist **Meilenstein 4**: Erst dort zeigt sich im Spiel, ob die vorberechneten Daten tragen.

## Was der Nutzer beisteuern muss

- **ForeverDB-API-Key** beantragen (Battle.net-Login auf foreverdb.net/developers, Zweck angeben, Quellenangabe zusagen).
- Angabe, ob **Python** (oder was sonst) auf dem Rechner installiert ist.
- Später: Spieldaten aus dem Client für Messwerte und Tests im Spiel.

## Offene Punkte

- Welche Client-Tabellen liefern in Forever tatsächlich Quest-XP, Kreaturen und Loot? (Spike)
- Wie vollständig sind die neuen Forever-Quests in QuestieDB und ForeverDB?
- Wie werden Drop-Raten sinnvoll geschätzt, wenn keine Quelle sie liefert?
- Wie fein muss das Reisezeitmodell sein, damit die Cluster-Bewertung stimmt?
- Wie groß wird das Paket, und wie lange dauert das Laden im Spiel?
