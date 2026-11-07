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

## Offene Punkte

- Wie werden Synergien effizient berechnet? Alle Bündel durchzuprobieren explodiert kombinatorisch, also braucht es Näherungen oder vorberechnete Überlappungen.
- Wie genau müssen Reisezeitmodelle sein (Wegenetz vs. Luftlinie mal Faktor)?
- Wie viele Daten sind im Add-on realistisch speicherbar (Größe der Vorberechnung)?
- Soll der Spieler überstimmen können (Quest trotzdem machen oder ausblenden)?
- Wie wird die Zielfunktion mit Nebenzielen kombiniert (z. B. Flugpunkte freischalten, Berufe)?
