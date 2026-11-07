# Routenlogik

Gedanken dazu, wie aus Daten eine gute Route wird. Noch nichts davon ist entschieden.

## Zielfunktion: XP pro Stunde

Das zentrale Optimierungsziel ist **maximale XP pro Stunde** (Gesamtzeit, nicht nur Kampfzeit). Alles andere (Loot, Ruf, Berufe) ist zweitrangig, solange es nicht ausdrücklich gewünscht wird.

Daraus folgt für jede mögliche Aktion:

```
Wert einer Aktion = erwartete XP / erwartete Zeit
```

Eine Aktion lohnt sich, wenn sie die durchschnittliche XP/h der Route nicht nach unten zieht. Das ist eine **Bewertung, keine feste Regel** (siehe unten).

## Grundsatz: alles dynamisch, keine starren Regeln

Es gibt keine fest einprogrammierten Regeln wie „Quest unter X XP/h wird gestrichen". Das Überspringen einer Quest ist nur ein **Ergebnis der laufenden Bewertung**, nicht ein eigener Mechanismus. Beispiel: wenig Quest-XP, keine Folgequests, sehr schlechte Drop-Rate, also lange Dauer für wenig Ertrag. Dann schneidet die Quest in der Bewertung schlecht ab und fällt raus. Ändert sich der Kontext (anderes Level, andere Nachbarquests, ein Mob-Gebiet liegt sowieso auf dem Weg), kann dieselbe Quest plötzlich gut abschneiden und kommt wieder rein.

Das Add-on liefert dafür **Vorberechnungen** frei Haus (Erwartungswerte für XP und Dauer je Quest, Mob-XP, Drop-Zeiten). Die Bewertung setzt daraus live den aktuellen Kontext zusammen.

Wichtig dabei:

- **Folgequests zählen mit.** Eine schwache Quest kann sich lohnen, wenn sie eine ertragreiche Kette freischaltet. Der Wert einer Quest ist ihr eigener Ertrag plus der Wert der freigeschalteten Nachfolger (abzüglich deren Zeit).
- **Keine feste Schwelle:** Verglichen wird immer mit der besten aktuellen Alternative (andere Quest, Grind, Hub weiter weg).
- **Synergien zählen mit:** Der Wert einer Quest hängt davon ab, was sonst gerade erledigt wird (siehe nächster Abschnitt).
- **Drop-Raten gehen in die Zeit ein:** erwartete Kills bis zum Drop mal Zeit pro Kill. Bei sehr niedriger Rate und Streuung ist das Risiko hoch, das sollte die Bewertung konservativ machen (siehe [05-ansaetze-und-risiken.md](05-ansaetze-und-risiken.md)).
- **Mob-XP nebenbei:** Beim Sammeln und Töten fallen zusätzlich Kill-XP an. Das verbessert die XP/h einer Quest und muss mit eingerechnet werden.

## Reisezeit und Quest-Hubs

Reisezeit ist Teil der Zeit jeder Aktion, aber sie wirkt **nicht pro Quest, sondern pro Cluster**:

- Eine weit entfernte einzelne Quest, auch eine ergiebige, lohnt sich oft nicht, weil der Weg die XP/h drückt.
- Ein weit entfernter **Quest-Knoten (Hub)** mit vielen guten Quests kann sich lohnen, weil sich die Reisezeit auf viele Quests verteilt.

Daraus folgt: Die Bewertung muss auf **Cluster** (Hub, Gebiet) erfolgen, nicht nur auf einzelne Quests.

```
Wert eines Clusters = Summe XP aller sinnvollen Quests + Mob-XP
                      ----------------------------------------
                      Reisezeit hin/zurück + Summe der Aktionszeiten
```

Zu klären: Wie werden Cluster gebildet (nach Quest-Geber, räumlicher Nähe, Zone)? Wie werden Reisezeiten geschätzt (Luftlinie, Wegenetz, Flugpunkte, Hearthstone, Reittier)?

## Synergien (Verstärkungseffekte)

Quests sind nicht unabhängig. Die Zeit einer Quest sinkt oft, wenn andere Quests parallel erledigt werden. Beispiele:

- **Gleiche Mobs:** Zwei Quests verlangen Kills oder Drops vom selben Mob. Die Kills zählen für beide, die Kampfzeit fällt nur einmal an.
- **Gleiches Gebiet:** Mobs sollen gefarmt werden, und im selben Gebiet liegt ein Objekt zum Looten oder ein Questziel. Laufweg und Aufenthalt werden geteilt.
- **Gemeinsamer Questgeber oder Hub:** Annahme und Abgabe mehrerer Quests am selben Ort.
- **Drops teilen sich Kills:** Ein Mob liefert mehrere benötigte Items gleichzeitig, die Dauer richtet sich nach dem langsamsten Item, nicht nach der Summe.
- **Nebenbei-XP:** Kill-XP auf dem Weg erhöht die XP/h aller beteiligten Quests.

Folge für die Bewertung: Der Wert einer Quest ist **nicht fest**, sondern hängt von der Menge der gleichzeitig geplanten Quests ab. Bewertet werden deshalb **Quest-Mengen (Bündel)**, nicht einzelne Quests. Die Gesamtzeit eines Bündels ist meist kleiner als die Summe der Einzelzeiten. Das Datenmodell muss das darstellen können (siehe [06-datenmodell.md](06-datenmodell.md)).

## Harte Regeln: Quest-Abhängigkeiten

Das sind die einzigen festen Regeln. Sie sind keine Optimierungsfrage, sondern Spielmechanik.

Eine Quest darf nur eingeplant werden, wenn:

- alle **Vorquests** abgeschlossen sind (Ketten, Folgequests),
- das **Mindestlevel** erreicht ist,
- Klasse, Rasse, Fraktion und ggf. Beruf passen,
- ggf. **Ruf** oder andere Bedingungen erfüllt sind,
- exklusive Quests (entweder/oder) beachtet werden.

Der Abhängigkeitsgraph muss zyklenfrei und auflösbar sein.

## Hybrid: Vorberechnung plus Live-Anpassung

Der gewünschte Ansatz hat zwei Teile.

### 1. Vorberechnung (offline, im Daten-Paket)

- Das Add-on liefert Grunddaten, in denen viele Berechnungen schon gemacht sind.
- Mögliche Routen und Cluster werden vorab ermittelt, inklusive XP-, Zeit- und Abhängigkeitswerten.
- Ergebnis: ein **Referenzplan** (eine Art „Soll-Route") mit erwarteter Zeit und erwartetem Level/XP-Stand an jedem Punkt.

### 2. Live-Anpassung (im Spiel)

Das Add-on verfolgt nicht stur den Guide, sondern vergleicht ständig **Ist gegen Soll**:

- Wo wäre ich laut Referenzplan (Level, XP, Zeit)? Wo bin ich tatsächlich?
- Beispiel: Laut Plan wäre ich jetzt Mitte Level 15, tatsächlich bin ich schon bei Level 16.
- Konsequenz: Quests, die für das niedrigere Level gedacht waren, bringen jetzt weniger relative XP (niedrigere Quests, Level-Skalierung) und schneiden in der Bewertung schlechter ab. Sie fallen heraus oder werden durch bessere Alternativen ersetzt.
- Umgekehrt (hinter dem Plan): Es können Quests aufgenommen werden, die ursprünglich übersprungen wurden, oder es kann ein Grind-Block eingeschoben werden.

Ablauf in Schleife:

1. Aktuellen Zustand lesen (Level, XP, Questlog, Position, abgeschlossene Quests).
2. Verbleibende Aktionen neu bewerten (XP/h mit aktuellem Level).
3. Bündel und Reihenfolge neu bewerten (inkl. Synergien), Abhängigkeiten prüfen.
4. Nächsten Schritt anzeigen.

Die Vorberechnung macht den teuren Teil, die Live-Phase nur leichte Neubewertung. Das ist wichtig, weil im Spiel nur begrenzt Rechenzeit zur Verfügung steht. **(zu prüfen)**

## Algorithmus-Ideen

- Greedy mit Lookahead: nach jeder Aktion die Aktion/den Cluster mit bester XP/h wählen, Abhängigkeiten als Filter.
- Vorberechnete Rangliste von Clustern je Level, die live nur neu gewichtet wird.
- Offline: Suche über die Reihenfolge der Cluster (z. B. Beam-Search oder TSP-Variante mit Vorrangbedingungen), Ergebnis als Referenzplan.
- Online: lokale Verbesserung (Quest streichen/einfügen), keine volle Neuberechnung.

## Position im Guide bestimmen

- Questlog auslesen (angenommene, erledigte, abgegebene Quests)
- Level und aktuelle XP, daraus Abweichung vom Referenzplan
- Zone und Position
- Wiedereinstieg nach Logout, Tod oder größerer Abweichung

## Nebenbei-Quests und Schlenker (Wunsch des Nutzers vom 7.11.2026)

Der Plan soll „Nebenbei"-Dinge ausdrücken und vom Routing erzeugen lassen können. Beispiel: Ein Gegner hat eine sehr schlechte Drop-Rate, die Quest hat keine Folgequest. Dann bleibt sie lange im Log und wird immer erledigt, wenn man an den Gegnern vorbeikommt. Das spart das Warten auf Respawns. Ein Schritt kann so aussehen: „Wir wollen eigentlich zu A, machen aber erst einen Schlenker zu B, töten dort X und gehen dann weiter zu A."

**Was der Planer schon hergibt:** Offene Quests teilen sich Kills automatisch, Spawns benötigter Mobs im Korridor entlang jeder Strecke werden mitgenommen, und Respawn-Wartezeiten sind im Modell. Ob eine Quest nur nebenbei läuft, ergibt sich allein aus der Zeitbewertung. Es gibt keine Regel „Drop-Rate unter X ist Nebenbei".

**Was in der Ausgabe dazugekommen ist (Stand 7.11.2026):**
- **Schlenker:** Jeder Kill-Schritt trägt den Umweg in Yards (`detour`), also wie viel länger der Weg über den Kill-Ort ist als der direkte Weg zum Ziel des nächsten Schritts. Es gibt keine Schwelle, der Wert wird immer angezeigt. Das Add-on schreibt dann „Schlenker (+N yd): … töten" und „dann weiter: …". Im aktuellen Plan haben alle 12 Kill-Schritte einen Wert (12 bis 655 yd).
- **Nebenbei-Quests:** Quests mit Kill-/Drop-Zielen, die nie gezielt bearbeitet werden, sind im Plan mit `side` markiert (aktuell 2). Quests, die am Planende noch offen sind, stehen in `meta.background` (aktuell 4 Einträge). `/fl side` listet sie im Spiel.

**Auffälligkeit:** Zwei Quests („Wolves Across the Border", „Brotherhood of Thieves") werden angenommen und bleiben am Ende offen. Das Modell bewertet den Fortschritt durch Kills unterwegs, die erwartete Fertigstellung kommt aber im Planzeitraum nicht zustande. Das kostet nur wenige Sekunden fürs Annehmen, ist aber ein Hinweis, dass die Nebenbei-Bewertung noch ungenau ist.

**Offen:** Gezieltes Erzeugen von „Schlenker, um Respawns zu umgehen" als eigene Handlung (der Planer teilt Kills bisher nur in zwei Größen auf, kleinste und größte Menge), und Erwartungswerte statt Würfeln bei sehr seltenen Drops (Streuung bestimmt, wie lange eine Nebenbei-Quest im Log bleibt).

## Lehrer-Besuche (geplant, Wunsch des Nutzers vom 7.11.2026)

Beim Levelaufstieg soll der Plan Besuche beim Klassenlehrer einplanen, um neue Fähigkeiten zu lernen. Das gehört in die Routenplanung als **eigene Handlung**, nicht als feste Regel („bei jedem Level zum Lehrer"):

- **Handlung „Lehrer besuchen":** kostet Weg zum Lehrer plus Dialogzeit. Nutzen: Neue Fähigkeiten machen Kämpfe schneller und sicherer, das senkt die Kill-Zeit und das Risiko für alle folgenden Kills. Der Planer entscheidet über die Zeit, ob und wann sich der Besuch lohnt (zum Beispiel, wenn der Lehrer ohnehin auf dem Weg liegt oder sich mehrere Fähigkeiten angesammelt haben). Der Nutzen als Kill-Zeit-Faktor ist eine **Annahme je Klasse**, die mit den Sammeldaten kalibriert werden kann (Kampfdauer pro Level vor und nach einem Besuch).
- **Die Klasse ist nicht fest (Entscheidung des Nutzers, 8.11.2026).** Klassenlehrer sitzen meist in Hubs: In Northshire/Elwynn sind es genau zwei (Northshire-Abtei und Goldshire), und in jedem stehen die Lehrer aller Klassen nur etwa 100 yd auseinander. Der Plan bleibt daher **klassenunabhängig**. Ein Lehrer-Besuch kostet im Plan den **erwarteten Weg über alle Klassen** (Mittel der Wege zum jeweils nächsten Lehrer jeder Klasse). Das ist im Planer umgesetzt (Errand mit `class_trainers`).
- **Im Spiel (noch zu bauen):** Das Add-on kennt die Klasse und löst den Besuch auf den konkreten Lehrer auf. Außerdem kann es dynamisch erkennen, ob beim Lehrer etwas zu holen ist (Zauber der Klasse mit erreichtem Mindestlevel, noch nicht gelernt), und den Besuch als **Einfügung** vorschlagen: „Lehrer liegt nur +N yd Umweg, dort neue Fähigkeiten". Das ist derselbe Einfügekosten-Gedanke wie beim Schlenker.
- **Offene Annahme:** Der Nutzen pro erlernter Stufe (aktuell 3 % kürzere Kampfzeit) und die Fähigkeitsstufen (4, 6, 8, 10) sind geraten und klassenübergreifende Durchschnitte. Im Testlauf plant der Planer deshalb nur einen späten Sammelbesuch (Minute 50, drei Stufen auf einmal). Ob und wann sich ein Besuch lohnt, hängt direkt an dieser Annahme.

**Datenlage (geprüft am 7.11.2026):**

| Benötigt | Quelle | Stand |
|---|---|---|
| Lehrer-NPCs mit Position | QuestieDB, NPC-Flag „Lehrer" (Bit 16) | vorhanden, 28 Lehrer-NPCs mit Position in Northshire/Elwynn (Klassen- und Berufslehrer gemischt) |
| Mindestlevel der Zauber | Client-Tabelle `SpellLevels` | vorhanden |
| Zauber je Klasse | Client-Tabelle `SkillLineAbility` (Klassenmaske, Art des Erwerbs) | vorhanden |
| Welcher Lehrer welche Zauber lehrt | Client-Tabellen `Trainer`/`TrainerSpell` | **nicht vorhanden** (Tabelle nicht gefunden) |
| Lehrer → Klasse | Untertitel der NPCs („Mage Trainer", „Warrior Trainer" …) in QuestieDB | **vorhanden und ausgewertet** (13 Lehrer-Typen in Northshire/Elwynn, 7 Klassen) |

Die fehlende Zauber-Zuordnung ist nicht kritisch: Ein Klassenlehrer der passenden Klasse lehrt die Klassenzauber.

**Offene Fragen dazu:** Welche Fähigkeiten sind für das Tempo wirklich relevant (je Klasse sehr unterschiedlich)? Wie viel Kill-Zeit spart ein Level-Schub an Fähigkeiten? Wie wird der Besuch bei Klassen ohne Lehrer in der Startzone behandelt (Lehrer in einer Hauptstadt, weiter Weg)?

## Offene Punkte

- Wie werden Synergien effizient berechnet? Alle Bündel durchzuprobieren explodiert kombinatorisch, also braucht es Näherungen oder vorberechnete Überlappungen.
- Wie genau müssen Reisezeitmodelle sein (Wegenetz vs. Luftlinie mal Faktor)?
- Wie viele Daten sind im Add-on realistisch speicherbar (Größe der Vorberechnung)?
- Soll der Spieler überstimmen können (Quest trotzdem machen oder ausblenden)?
- Wie wird die Zielfunktion mit Nebenzielen kombiniert (z. B. Flugpunkte freischalten, Berufe)?
