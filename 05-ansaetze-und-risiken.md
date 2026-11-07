# Ansätze und Risiken

## Zwei grundsätzliche Wege

### A: Bestehendes Leveling-Add-on nutzen, nur Guides liefern

Wir erzeugen KI-basiert Guide-Dateien im Format eines vorhandenen Add-ons (z. B. Guidelime) und lassen dessen Engine Position, Anzeige und Quest-Tracking übernehmen.

- **Pro:** wenig Code, Positionsbestimmung und Kartenmarker schon vorhanden, schneller Prototyp.
- **Contra:** Funktionsumfang (Routenoptimierung, dynamische Anpassung) durch das fremde Add-on begrenzt. Abhängig von dessen Pflege und Lizenz.
- **Zu klären:** Gibt es ein dokumentiertes Guide-Format oder eine API zum Registrieren eigener Guides? Passt es zur gewählten WoW-Version?

### B: Eigenes Add-on schreiben

Komplett eigener Code (Lua), eigene Datenstruktur, eigene Anzeige.

- **Pro:** volle Kontrolle, Routenlogik frei gestaltbar.
- **Contra:** deutlich mehr Aufwand (UI, Quest-Tracking, Karte, Persistenz), mehr Testbedarf im Spiel.

### Auswirkung der neuen Anforderung (Live-Anpassung)

Die gewünschte dynamische Neubewertung (Ist gegen Soll, automatisches Überspringen, Cluster-Logik) geht über einen starren Guide hinaus. Ein reines Guide-Format wie bei einem fremden Add-on bildet das vermutlich nicht ab. Wahrscheinlich braucht es mindestens eine **eigene Logik-Schicht im Spiel**, die entweder als eigenes Add-on läuft oder ein bestehendes Add-on ergänzt. **(zu prüfen: ob Guidelime o. ä. Erweiterungspunkte für so etwas bieten)**

### Ergebnis der ersten Recherche

Es gibt für Forever **kein brauchbares Skelett für die dynamische Logik**. Guidelime (mit Questie) ist eine Engine für starre Textguides, RestedXP und Zygor sind geschlossen. Realistisch sind zwei Wege: **eigenes Add-on** oder **eigenes Add-on mit Guidelime/Questie nur als Anzeige- und Datenhilfe**. Details in [07-recherche-wow-forever.md](07-recherche-wow-forever.md).

### Navigation: TomTom CrazyArrow statt Guidelime-Pfeil

Entscheidung des Nutzers: Guidelime läuft auf Forever, aber der **CrazyArrow von TomTom** gefällt besser. Plan: Unsere Logik wählt den nächsten Schritt, TomTom zeigt den Weg.

- **Forever-Unterstützung (unbestätigt):** Eine Fanseite nennt eine Forever-Version von TomTom (4.3.13, Interface 16001, laut Changelog auf Wago), eine andere Seite sagt „nicht bestätigt". Im Spiel prüfen, zum Beispiel mit `/run print(TomTom and TomTom.SetCrazyArrow)`.
- **API (aus älteren Versionen, für Forever ungeprüft):** `TomTom:AddWaypoint(...)`, `TomTom:SetCrazyArrow(...)`, `TomTom:ClearCrazyArrowPoint(remove)` (neu in 4.0.12) sowie Callbacks wie `WaypointAdded`/`WaypointRemoved`. Signaturen vor dem Bauen im aktuellen Quelltext nachlesen.
- **Folge:** Eine eigene Pfeil-Anzeige entfällt. Guidelime wird für Navigation nicht gebraucht. Ob wir es für etwas anderes brauchen (Schritt-Liste, Questtracking), ist offen.

### Mischform

Datenpipeline und Routenoptimierung offline (A-ähnlich: erzeugt Guides), später bei Bedarf eigenes Add-on für dynamische Funktionen. Empfehlung vorläufig: **mit A anfangen, B als Option offenhalten**. Hängt von der Antwort zu den Add-on-Fragen ab.

## Unsicherheitsfaktoren

| Risiko | Auswirkung | Mögliche Gegenmaßnahme |
|---|---|---|
| Drop-Raten sind Schätzungen | Zeitschätzung schwankt stark | Erwartungswert nutzen, Spanne anzeigen, konservativ planen |
| XP-Werte ändern sich mit Patches oder Skalierung | Falsche Bewertung der Quests | Daten pro Version halten, Regeneration automatisieren |
| Datenquelle fehlerhaft oder lückenhaft | Quest fehlt oder Abhängigkeit falsch | Automatische Konsistenzprüfung, Abgleich mehrerer Quellen |
| Lizenz/Nutzungsbedingungen der Quelle | Darf evtl. nicht automatisiert genutzt werden | Vorab klären, offene Dumps bevorzugen |
| Laufzeiten und Mobdichte schwer zu messen | Routenqualität begrenzt | Vereinfachte Annahmen, später Feedback aus echten Läufen |
| Falsche Zeitmodelle (Reisezeit, Kampfzeit) | XP/h-Bewertung stimmt nicht, falsche Quests werden übersprungen | Modelle einfach halten, über Parameter einstellbar machen, später mit echten Läufen kalibrieren |
| Bewertung unterschätzt Quests | Wertvolle Ketten oder Synergien werden verpasst | Folgequests und Überlappungen einrechnen, Spieler kann überstimmen |
| Synergieberechnung explodiert kombinatorisch | Zu langsam im Spiel | Überlappungen vorab indizieren, Näherungen statt vollständiger Suche |
| „WoW Forever" weicht von Classic ab (über 1.000 neue Quests, neue Zonen) | Classic-Daten sind lückenhaft, Questie-Daten für neue Quests unvollständig | Forever-eigene Quellen nutzen (Client-Tabellen, ForeverDB, Wowhead Forever), Lücken automatisch erkennen |
| Frisch gelaunchte Version, Daten und Add-ons ändern sich schnell | Veraltete Annahmen, Datenfehler | Pipeline automatisiert und wiederholbar halten, Stand dokumentieren |
| Live-Berechnung zu teuer im Spiel | Ruckler oder Verzögerungen | Schwere Arbeit offline vorberechnen, live nur leichte Neubewertung |
| Spieler weicht vom Guide ab | Guide „verliert" den Spieler | Robuste Wiedereinstiegslogik anhand Questlog |
| Komplett KI-erstellt, wenig manuelle Prüfung | Fehler bleiben unentdeckt | Automatische Tests, Validierung der Daten, Stichproben im Spiel |
| Regeln/Terms of Service des Spiels | Add-on könnte unzulässig sein | Nur Anzeige und Hinweise, keine Automatisierung von Aktionen |

## Mögliche nächste Schritte

1. WoW-Version festlegen (siehe [02-offene-fragen.md](02-offene-fragen.md)).
2. Recherche: Welche Leveling-Add-ons gibt es für diese Version, und erlauben sie eigene Guides?
3. Recherche: Welche Datenquelle liefert Quests, XP, Abhängigkeiten und Drops in brauchbarer Form, und was erlauben die Lizenzen?
4. Kleinen Prototyp planen: eine Startzone, eine Fraktion, Level 1–10.
5. Entscheidung A oder B anhand der Rechercheergebnisse.
