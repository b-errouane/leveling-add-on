# Datenmodell (Entwurf)

Das Datenmodell muss die dynamische Bewertung und die Synergien aus [04-routenlogik.md](04-routenlogik.md) tragen können. Dieser Entwurf sammelt nur die Anforderungen, noch kein festes Schema.

## Grundprinzip: Ziele statt Quests

Der Kern ist, dass eine Quest nicht als einzelner Klotz mit fester Dauer modelliert wird, sondern als **Menge von Zielen (Objectives)**. Erst dadurch lassen sich Überlappungen zwischen Quests erkennen.

```
Quest
 ├─ Voraussetzungen   (Vorquests, Level, Klasse/Rasse/Fraktion, Ruf)
 ├─ Annahme-Ort / Abgabe-Ort
 ├─ XP-Belohnung      (abhängig vom Spielerlevel)
 └─ Objectives[]
      ├─ Typ          (töte Mob, sammle Item, nutze Objekt, erkunde Ort, ...)
      ├─ Menge
      ├─ Quelle(n)    (welche Mobs / Objekte / Orte liefern das Ziel)
      └─ Erwartete Dauer (Basiswert aus Vorberechnung)
```

## Quellen und Orte als eigene Entitäten

Damit Synergien erkennbar sind, müssen Dinge, die mehrere Quests gemeinsam haben, **als gemeinsame Einträge** vorliegen, nicht als Kopien:

- **Mob (Kreatur):** Level, Kill-XP, Spawns/Positionen, Loot-Tabelle
- **Objekt:** Position, Respawn, Looten
- **Item:** Welche Quellen liefern es, mit welcher Drop-Rate
- **Ort / Gebiet / Cluster:** räumlicher Bezug, Hub-Zugehörigkeit
- **Wege:** Reisezeit zwischen Orten

Zwei Quests, die denselben Mob als Quelle haben, verweisen auf denselben Mob-Eintrag. Daraus lässt sich ableiten: Kills können geteilt werden.

## Was vorberechnet wird (im Daten-Paket)

- Erwartete Dauer je Objective (Kills bis Drop, Zeit pro Kill, Respawn)
- Kill-XP je Mob in Abhängigkeit vom Spielerlevel
- Quest-XP je Spielerlevel
- Reisezeiten zwischen Orten/Clustern
- **Überlappungsinformation:** Welche Quests teilen Mobs, Items, Orte, Hubs (als Index, damit live nicht alles neu gesucht werden muss)
- Abhängigkeitsgraph der Quests
- Optional: ein Referenzplan mit Soll-Level und Soll-XP über der Zeit

## Was live berechnet wird (im Spiel)

- Gesamtzeit und -XP für ein Bündel von Quests, unter Berücksichtigung der Überlappungen (z. B. gemeinsame Kills nur einmal zählen)
- Neubewertung nach Levelwechsel oder Abweichung vom Plan
- Auswahl des nächsten Schritts

## Anforderungen an das Modell

- **Überlappung ausdrückbar:** gleiche Mobs, gleiche Gebiete, gemeinsame Items.
- **Zeit nicht additiv:** Die Dauer eines Bündels ist nicht die Summe der Einzeldauern. Das Modell muss dafür eine Rechenvorschrift ermöglichen, z. B. „parallele Objectives teilen Kills, Dauer = Maximum statt Summe".
- **Parametrisierbar:** Werte wie Kampfgeschwindigkeit, Lauftempo, Reittier sollen als Parameter einstellbar sein.
- **Kompakt:** Das Add-on hat Speicher- und Ladezeitgrenzen **(zu prüfen)**.
- **Neu generierbar:** Das Paket entsteht automatisch aus den Rohdaten (siehe [03-datenquellen.md](03-datenquellen.md)).

## Offene Fragen

- Wie fein sind Objectives (jeder Kill einzeln oder Gruppen)?
- Wie wird Unsicherheit ausgedrückt (Erwartungswert plus Streuung, z. B. Drop-Raten)?
- Wie wird ein Bündel effizient bewertet, ohne alle Kombinationen durchzuprobieren?
- In welchem Format ist das Paket am besten (Lua-Tabellen, kompaktes Binärformat, Sharding pro Zone)?
