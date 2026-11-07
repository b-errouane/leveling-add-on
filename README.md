# Leveling-Add-on – Ideensammlung

Status: **Ideenphase**, noch kein Code. Hier werden lose Gedanken strukturiert, bevor etwas gebaut wird.

## Kurzbeschreibung

Ein World-of-Warcraft-Add-on, das beim Leveln hilft. Es kennt die Position des Spielers im Guide, optimiert die Route und beachtet Quest-Abhängigkeiten. Das Add-on soll **vollständig KI-erstellt** sein, also nicht von Hand geschrieben oder kuratiert, und auf **öffentlichen Datenbanken** basieren.

## Dateien

| Datei | Inhalt |
|---|---|
| [01-vision-und-ziele.md](01-vision-und-ziele.md) | Was soll das Add-on können, was ist Prinzip, was ist ausdrücklich nicht Ziel |
| [02-offene-fragen.md](02-offene-fragen.md) | Alles, was noch geklärt werden muss (inkl. Entscheidungsbedarf) |
| [03-datenquellen.md](03-datenquellen.md) | Welche Daten werden gebraucht und woher könnten sie kommen |
| [04-routenlogik.md](04-routenlogik.md) | Gedanken zu Routenoptimierung, Quest-Abhängigkeiten, XP-Rechnung |
| [05-ansaetze-und-risiken.md](05-ansaetze-und-risiken.md) | Eigenbau vs. bestehendes Add-on erweitern, Unsicherheiten |
| [06-datenmodell.md](06-datenmodell.md) | Entwurf des Datenmodells (Ziele, Quellen, Überlappungen, Vorberechnung) |

| [08-datenpipeline.md](08-datenpipeline.md) | Plan der Datenpipeline: Quellen holen, normalisieren, zusammenführen, prüfen, ableiten, als Lua ausgeben, mit Meilensteinen |
| [07-recherche-wow-forever.md](07-recherche-wow-forever.md) | Recherche: Was ist WoW Forever, welche Add-ons gibt es, was taugt als Basis |

Zielversion: **WoW Forever** (offizielle dritte WoW-Version seit 4.11.2026, Level 1–60, über 1.000 neue Quests, Datenbasis daher nur teilweise Classic).

## Getroffene Entscheidungen

- Zielversion: WoW Forever
- Optimierungsziel: XP pro Stunde, alles dynamisch bewertet, keine starren Skip-Regeln
- Projekt bleibt **privat**
- **GPL-3.0 ist akzeptiert** (QuestieDB-Daten nutzbar)
- Komplett KI-erstellt, datengetrieben
- Guidelime ist auf Forever nutzbar (laut Nutzer), als **Navigationsanzeige** wird aber **TomTom (CrazyArrow)** bevorzugt

## Konventionen

- Aussagen mit **(zu prüfen)** sind Annahmen aus dem Gedächtnis und noch nicht verifiziert.
- Neue lose Gedanken zuerst in `02-offene-fragen.md` oder `01-vision-und-ziele.md` ergänzen, dann bei Bedarf in eine eigene Datei auslagern.
