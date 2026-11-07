# Vision und Ziele

## Grundidee

Ein Leveling-Add-on für WoW, das den Spieler von Level 1 bis zum Maximallevel auf einer möglichst effizienten Route führt. Das Add-on weiß jederzeit, wo der Spieler im Guide steht, und sagt, was als Nächstes zu tun ist.

## Hauptziel: XP pro Stunde maximieren

Das wichtigste Kriterium ist **XP pro Stunde**. Alles, was diesen Wert senkt, soll das Add-on automatisch vermeiden. Beispiel: Eine Quest mit wenig XP, ohne Folgequests und mit sehr schlechter Drop-Rate kostet viel Zeit für wenig Ertrag und wird übersprungen. Das geschieht automatisch, ohne dass der Spieler abwägen muss. Details in [04-routenlogik.md](04-routenlogik.md).

Zwei Kernideen dazu:

- **Live statt starrer Guide:** Das Add-on vergleicht den Ist-Zustand (Level, XP) mit dem, wo der Spieler laut Referenzroute wäre. Ist man schneller, werden nicht mehr lohnende Quests gestrichen. Ist man langsamer, passt sich die Route ebenfalls an.
- **Reisezeit zählt:** Eine weit entfernte einzelne Quest lohnt sich meist nicht. Ein weit entfernter Quest-Hub mit vielen guten Quests kann sich trotzdem lohnen.

## Leitprinzipien

1. **Komplett KI-erstellt.** Weder Code noch Guide-Inhalte werden von Hand geschrieben. Die KI erzeugt beides.
2. **Datengetrieben.** Die Guides entstehen aus öffentlichen Datenbanken, nicht aus abgeschriebenen Fremd-Guides.
3. **Reproduzierbar.** Wenn Daten oder Regeln sich ändern, lässt sich der Guide neu generieren.

## Gewünschte Funktionen

### Kern

- **Guide-Position kennen:** Das Add-on erkennt anhand von Questlog, Level, Zone und Position, an welcher Stelle des Guides der Spieler ist.
- **Routenoptimierung nach XP/h:** Reihenfolge von Quests, Grind und Laufwegen so wählen, dass die XP pro Stunde maximal sind.
- **Automatisches Überspringen:** Unrentable Quests (wenig XP, lange Dauer, keine lohnenden Folgequests) werden gestrichen.
- **Dynamische Anpassung:** Vergleich von Ist und Soll (z. B. „laut Plan Level 15, tatsächlich schon 16"), danach Route neu bewerten.
- **Reisezeit und Quest-Hubs:** Bewertung auf Cluster-Ebene, nicht nur pro Einzelquest.
- **Quest-Abhängigkeiten:** Folgequests und Vorquests berücksichtigen. Eine Quest darf erst eingeplant werden, wenn ihre Voraussetzungen erfüllt sind. Dazu gehören Vorquests, Level, Ruf, Klasse/Rasse/Fraktion und eventuell Berufe.
- **XP-Rechnung:** Wie viel XP braucht man pro Level, wie viel geben Quests und wie viel Mobkills. Daraus folgt, was sich lohnt.

### Daten, die einfließen sollen

- Welche Quests gibt es in welchem Gebiet?
- Wie viel XP gibt jede Quest?
- Wie viel XP braucht man für jedes Level?
- Wie viel XP geben Mobkills (abhängig vom Level-Unterschied)?
- Drop-Raten von Questitems, die von Gegnern kommen (beeinflusst, wie lange ein Questschritt dauert).

## Nicht-Ziele (vorläufig)

- Kein handgeschriebener Guide.
- Kein Bot und keine Automatisierung von Eingaben. Das Add-on gibt nur Anweisungen. **(zu prüfen: Was die Add-on-API ohnehin erlaubt)**
- Keine Endgame-Inhalte.

## Idealfall für den Nutzer

> Ich installiere das Add-on, wähle Charakter und ggf. Optionen, und sehe zu jeder Zeit: „Als Nächstes: Quest X in Zone Y abgeben, dann Z annehmen." Auch nach Tod, Logout oder einer Abkürzung findet das Add-on zurück in den Guide.
