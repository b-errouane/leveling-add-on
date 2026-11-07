# Forever Leveler (Prototyp)

Kleines Add-on, das den **nächsten Schritt** eines vorberechneten Leveling-Plans anzeigt und den **TomTom-Pfeil** darauf setzt. Es zeigt nur an und liest den Questlog, es automatisiert nichts.

**Status:** Prototyp, im Spiel noch nicht getestet. Die Auswahl-Logik ist offline mit einem nachgebauten WoW-Gerüst geprüft (`addon/tests/test_leveler.lua`), die echten Schnittstellen des Forever-Clients sind es nicht.

**Umfang des Plans:** Nur Mensch, nur Northshire Valley und Elwynn Forest, Level 1 bis 10. Zeitwerte sind geraten und nicht kalibriert (siehe `09-spike-ergebnisse.md`).

## Installieren

1. Ordner `addon/ForeverLeveler` in den AddOns-Ordner des Forever-Clients kopieren.
2. TomTom sollte installiert sein (optional, ohne TomTom gibt es nur die Anzeige).
3. Im Spiel erscheint `FL geladen`. Die Anzeige hängt oben mittig und lässt sich mit der Maus verschieben.

## Bedienung

| Befehl / Knopf | Wirkung |
|---|---|
| `/fl` | Befehle anzeigen und Anzeige aktualisieren |
| `/fl list` | die nächsten Schritte im Chat |
| `/fl why` | empfohlene Abfolge mit XP, Zeit und Rate; Vergleich mit dem Plan-Schritt |
| `/fl plan` | zwischen Neubewertung und strikt nach Plan umschalten |
| `/fl side` | Nebenbei-Quests (im Log lassen) und Quests, die am Planende offen bleiben |
| `/fl skip` oder Knopf „Skip" | aktuellen Schritt überspringen (z. B. wenn die Quest nicht angeboten wird) |
| `/fl back` | zuletzt übersprungenen Schritt zurückholen |
| `/fl arrow` | TomTom-Pfeil an/aus |
| `/fl show` / `/fl hide` | Anzeige ein-/ausblenden |
| `/fl scale <0.6–1.8>` | Größe des Fensters |
| `/fl lock` | Fenster fixieren / wieder verschiebbar machen |
| `/fl reset` | alle Überspringungen löschen |
| `/fl about` | Stand des Plans und Quellen |

## Oberfläche

- **Kopfzeile:** Schrittnummer, bei Abweichung vom Plan „(Plan: N)", Level und Modus („Neubewertung" oder „Plan").
- **Farbakzent und Icon** je Schritt-Art: Annehmen gold, Abgeben grün, Töten rot, Grinden orange, Ziel erledigen blau, Ruhestein/Heimat blau-violett, Lehrer violett.
- **Fortschrittsleiste:** erledigte Schritte im Verhältnis zum ganzen Plan, im Farbton des aktuellen Schritts.
- **Hauptzeile mit Icon**, rechts die **Entfernung** zum Ziel in Yards (aus der Spielerposition, wenn du auf der Plan-Karte bist).
- **Hinweiszeile** mit Begründung (Belohnung, „für: Quest", Umweg, Nebenbei-Quest, geschätzte Rate) und **„danach"-Zeile** mit dem folgenden Schritt.
- **Flache Knöpfe** oben rechts: „Skip" und „Pfeil: an/aus".
- **Fenster:** ziehbar, auf den Bildschirm begrenzt, mit `/fl scale 0.6–1.8` skalierbar und mit `/fl lock` fixierbar.

Die Gestaltung ist nur offline gegen ein nachgebautes Gerüst geprüft, das Aussehen im Spiel nicht gesehen. Icons nutzen Standard-Texturen der Spieldateien; fehlt eine, erscheint ein einfarbiges Quadrat.

## Schritt-Arten im Plan

| Art | Anzeige | Wann erledigt |
|---|---|---|
| annehmen / abgeben | Quest und NPC | Quest im Log bzw. abgegeben |
| töten, Ziel erledigen | Mob und Menge, bei Schlenkern mit Umweg | die zugehörigen Quests sind fertig |
| grinden | Mob und Menge, „bis Level N" | Spielerlevel hat das Plan-Level erreicht |
| Heimat setzen, Lehrer, Flugpunkt | Name | Spielerlevel hat das Plan-Level erreicht (kein Dauerblocker, mit Skip überspringbar) |

Schritte mit **„Ruhestein benutzen, dann: …"** bedeuten, dass der Plan den Weg per Ruhestein vorsieht, weil er schneller ist als zu Fuß. Ob der Ruhestein bereit ist, prüft das Add-on noch nicht (der Plan geht vom Normalzustand aus). Ist er in Abklingzeit, gehst du zu Fuß.

## Live-Neubewertung (neu)

Der Plan ist offline für einen typischen Zustand berechnet. Im Spiel weicht der echte Zustand ab (Position, Level, früher oder gar nicht erledigte Quests, Ruhestein in Abklingzeit). Deshalb rechnet das Add-on alle paar Sekunden und bei Ereignissen eine **kleine Vorausschau** über die verbleibenden Schritte (`Reeval.lua`, reine Logik ohne WoW-Aufrufe):

- **Bewertung einer Abfolge:** `XP − λ · Sekunden`, mit λ = XP pro Sekunde des Referenzplans (Opportunitätskosten der Zeit). Es gibt keine festen Schwellen: Ein Schritt wird nur vorgezogen oder weggelassen, weil eine andere Abfolge im aktuellen Zustand besser abschneidet.
- **Eingaben aus dem Spiel:** Level, Position (wenn auf der Plan-Karte, sonst die letzte bekannte), Questlog (angenommen, erledigt, Ziele fertig, Zahl der Quests), Ruhestein-Abklingzeit.
- **Eingaben aus dem Plan:** pro Schritt Arbeitszeit, Ort, XP-Bausteine (Moblevel, Menge, Quest-XP und Quest-Level) und Abhängigkeiten. Die XP werden mit dem **aktuellen** Level neu berechnet (Quest-XP sinkt, wenn man der Quest entwachsen ist, Kill-XP hängt vom Level-Unterschied ab).
- **Abhängigkeiten:** Annehmen vor Erledigen vor Abgeben, Vorquests, freie Questlog-Plätze.
- **Plan-Reihenfolge bleibt** für Schritte, deren Nutzen offline bestimmt wurde (Heimat setzen, Lehrer, Flugpunkt entdecken), und als Rückfall, wenn nichts passt.
- **Anzeige:** Weicht die Empfehlung vom Plan ab, steht in der Kopfzeile „(Plan: N)" und in der Hinweiszeile die geschätzte Rate („Neubewertung: ca. X XP/h").
- **Rechenzeit:** etwa 3 ms pro Aufruf in LuaJIT, im Spiel-Lua vermutlich ein Vielfaches (nicht gemessen). Gehäufte Quest-Ereignisse werden auf eine Neuberechnung pro Sekunde begrenzt.

Befehle: `/fl why` zeigt die empfohlene Abfolge mit XP, Zeit und Rate. `/fl plan` schaltet zwischen Neubewertung und strengem Plan um.

**Grenzen:** Nur ein Horizont von 6 Schritten (Suchhilfe, keine Spielregel). Flugpunkte sind nicht eingebunden. Ob der Ruhestein bereit ist, wird über den Gegenstand 6948 abgefragt (aus dem Classic-Gedächtnis, im Forever-Client nicht geprüft); ist die Abfrage nicht möglich, geht die Neubewertung vom Gehen aus. Die Heimat des Spielers kennt das Add-on nicht, es nimmt die Heimat aus dem Plan an.

## Wie die Schritt-Auswahl funktioniert (Plan-Reihenfolge)

Der Plan ist eine **Referenz**. Als Rückfall und für `/fl plan` nimmt das Add-on den **ersten Schritt, dessen Ziel noch nicht erreicht ist**:

- *Annehmen:* erreicht, wenn die Quest im Log ist oder schon erledigt wurde.
- *Töten / Ziel erledigen:* erreicht, wenn alle Quests, für die der Schritt gedacht ist, abgeschlossen oder nicht (mehr) im Log sind.
- *Abgeben:* erreicht, wenn die Quest erledigt ist oder nicht im Log steht.

Wer vom Plan abweicht (etwas früher macht, eine Quest nicht annimmt), landet dadurch automatisch beim nächsten sinnvollen Schritt. Eine **Live-Neubewertung nach XP/h** (Quests streichen, Reihenfolge ändern) gibt es noch nicht, das ist der nächste Ausbauschritt.

## Daten

`Plan.lua` wird von `python -m pipeline.emit.emit_lua` erzeugt (nicht von Hand ändern). Quellen: QuestieDB (GPL-3.0), Questie-Support-Tabellen, Blizzard-Client-Tabellen via wago.tools. **Es sind keine ForeverDB-Daten enthalten.** Sobald solche eingehen, muss die Quellenangabe (https://foreverdb.net) im Add-on sichtbar sein (siehe `08-datenpipeline.md`).

## Bekannte Grenzen

- Plan ist für Mensch erstellt, andere Völker bekommen nur einen Hinweis.
- Quest-XP der neuen Forever-Quests ist im Plan geschätzt.
- Nicht jede Funktion der Schnittstelle ist im Forever-Client gesichert vorhanden (`C_QuestLog.IsOnQuest` usw. sind abgesichert aufgerufen, fehlen sie, bleibt die Anzeige im Zweifel auf einem Schritt stehen).
- Ziel-Schritte setzen den Pfeil auf den nächsten Spawn, nicht auf einen bestimmten Mob.
