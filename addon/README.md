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
| `/fl side` | Nebenbei-Quests (im Log lassen) und Quests, die am Planende offen bleiben |
| `/fl skip` oder Knopf „Skip" | aktuellen Schritt überspringen (z. B. wenn die Quest nicht angeboten wird) |
| `/fl back` | zuletzt übersprungenen Schritt zurückholen |
| `/fl arrow` | TomTom-Pfeil an/aus |
| `/fl show` / `/fl hide` | Anzeige ein-/ausblenden |
| `/fl reset` | alle Überspringungen löschen |
| `/fl about` | Stand des Plans und Quellen |

## Schritt-Arten im Plan

| Art | Anzeige | Wann erledigt |
|---|---|---|
| annehmen / abgeben | Quest und NPC | Quest im Log bzw. abgegeben |
| töten, Ziel erledigen | Mob und Menge, bei Schlenkern mit Umweg | die zugehörigen Quests sind fertig |
| grinden | Mob und Menge, „bis Level N" | Spielerlevel hat das Plan-Level erreicht |
| Heimat setzen, Lehrer, Flugpunkt | Name | Spielerlevel hat das Plan-Level erreicht (kein Dauerblocker, mit Skip überspringbar) |

Schritte mit **„Ruhestein benutzen, dann: …"** bedeuten, dass der Plan den Weg per Ruhestein vorsieht, weil er schneller ist als zu Fuß. Ob der Ruhestein bereit ist, prüft das Add-on noch nicht (der Plan geht vom Normalzustand aus). Ist er in Abklingzeit, gehst du zu Fuß.

## Wie die Schritt-Auswahl funktioniert

Der Plan ist eine **Referenz**. Das Add-on nimmt immer den **ersten Schritt, dessen Ziel noch nicht erreicht ist**:

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
