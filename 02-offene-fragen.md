# Offene Fragen

Alles, was geklärt werden muss, bevor oder während wir bauen. Punkte mit **[Entscheidung]** brauchen eine Antwort von dir.

## Grundlegend

- [x] **WoW-Version: „WoW Forever"** (offiziell, Launch 4.11.2026, Level 1–60, über 1.000 neue Quests, neue Zonen). Details in [07-recherche-wow-forever.md](07-recherche-wow-forever.md). Die Datenbasis ist **nicht** reines Classic, sondern um neue/überarbeitete Inhalte erweitert.
- [ ] Wo weichen XP-Kurve, Quest-XP und Mob-XP in Forever von Classic ab? (Client-Tabellen, offizielle Quelle)
- [ ] Falls sich Daten zwischen WoW Forever und Classic unterscheiden: Gibt es eine eigene Datenquelle, oder verwenden wir Classic-Daten als Näherung?
- [ ] Wie erkennen wir Abweichungen von Classic (Abgleich im Spiel, Patchnotes)?
- [ ] **[Entscheidung] Welche Spielerfraktion/Klassen zuerst?** Alle Klassen und Rassen oder erst ein Pfad (z. B. eine Fraktion, eine Startzone) als Prototyp?
- [ ] **[Entscheidung] Zielbereich:** Alle Level 1 bis Max oder zuerst nur ein Ausschnitt (z. B. 1–20)?
- [x] Wie wird „optimal" definiert? **Entschieden: XP pro Stunde.** Nebenziele (Loot, Ruf, Berufe) zweitrangig.
- [x] Überspringen: **kein fester Schwellenwert, alles dynamisch.** Quests fallen als Ergebnis der Bewertung heraus (siehe [04-routenlogik.md](04-routenlogik.md)).
- [ ] Wie bilden wir Synergien ab (gleiche Mobs, gleiche Gebiete, gemeinsame Drops)? Entwurf in [06-datenmodell.md](06-datenmodell.md).
- [ ] Soll der Spieler eine übersprungene Quest manuell wieder einblenden oder überstimmen können?
- [ ] Wie genau wird Reisezeit modelliert (Wegenetz, Luftlinie mal Faktor, Flugpunkte, Hearthstone, Reittier)?
- [ ] Wie werden Quest-Cluster/Hubs gebildet (Questgeber, räumliche Nähe, Zone)?
- [ ] Wie groß darf die Vorberechnung im Add-on sein (Dateigröße, Ladezeit, Speicher)?
- [ ] Wie viel Rechenzeit darf die Live-Neubewertung im Spiel brauchen? **(zu prüfen)**
- [ ] Ist es okay, wenn die Routen für Gruppenspiel nicht ausgelegt sind (Solo-Annahme)?

## Bestehendes Add-on nutzen oder selbst bauen?

Kernfrage: Müssen wir ein eigenes Add-on schreiben, oder können wir ein bestehendes Leveling-Add-on nehmen und nur eigene Guides einspeisen?

- [x] Welche Leveling-Add-ons gibt es für Forever? **Questie** und **Guidelime** haben Forever-Versionen, RestedXP und Zygor sind geschlossen/kostenpflichtig. Siehe [07-recherche-wow-forever.md](07-recherche-wow-forever.md).
- [x] Guidelime läuft auf Forever (laut Nutzer). Als Navigation wird **TomTom CrazyArrow** bevorzugt, siehe [05-ansaetze-und-risiken.md](05-ansaetze-und-risiken.md).
- [x] TomTom läuft auf Forever: `TomTom.SetCrazyArrow` existiert (vom Nutzer im Spiel bestätigt). Signaturen noch im Quelltext prüfen.
- [ ] Brauchen wir Guidelime noch für etwas (Schrittliste, Questtracking), oder übernimmt das ein eigenes kleines UI?
- [ ] Wie zeigt das Add-on den aktuellen Schritt und die Begründung an (z. B. „Quest X, weil XP/h = …")?
- [ ] Erlaubt das Add-on **eigene Guides**? Wie ist das Format (Textdatei, Lua-Tabelle, eigenes Markup)? Gibt es eine API zum Registrieren von Guides aus einem separaten Add-on? **(zu prüfen, Guidelime scheint dies zu können)**
- [ ] Lizenz des Add-ons: Dürfen wir darauf aufbauen, es erweitern oder weitergeben? Bei Closed-Source-Add-ons (Zygor, RestedXP) wohl eher nicht.
- [ ] Reicht die Funktionalität des bestehenden Add-ons (Abhängigkeiten, Positionsbestimmung im Guide), oder fehlt die Routenoptimierung ohnehin?

## Daten

- [ ] Welche öffentliche Datenbank ist die verlässlichste Grundlage? Erste Kandidaten für Forever: QuestieDB (GPL-3.0), ForeverDB-API (Quellenangabe), Client-Tabellen. Siehe [03-datenquellen.md](03-datenquellen.md).
- [x] **Lizenz: GPL-3.0 ist akzeptiert.** QuestieDB und davon abgeleitete Quellen dürfen verwendet werden. Falls das Projekt je veröffentlicht wird, steht es dann unter GPL-3.0.
- [x] **Projekt bleibt privat.** Lizenz- und Bedingungsfragen sind dadurch entspannter. Quellenangabe bei ForeverDB trotzdem im Blick behalten, falls Daten irgendwo angezeigt werden.
- [ ] Ist das Auslesen der Client-Tabellen (DB2) erlaubt, und wie kommen wir sauber heran (wago.tools-API, lokale Tools)?
- [ ] Ist Forever-Datenabdeckung für neue Quests in QuestieDB und ForeverDB ausreichend, oder braucht es eigene Datensammlung?
- [ ] Hat ForeverDB einen Bulk-Zugang, welche Rate-Limits und Bedingungen gelten?
- [x] **Pflicht: ForeverDB-Quellenangabe** (https://foreverdb.net) überall, wo die Daten gesehen werden. Ist in README, [03-datenquellen.md](03-datenquellen.md) und [08-datenpipeline.md](08-datenpipeline.md) festgehalten.
- [ ] Wo genau zeigt das Add-on die Quellenangabe an (Info-Fenster, Schrittanzeige, Tooltip), und in welcher Form ohne klickbaren Link?
- [ ] Gibt es weitere Vorgaben der ForeverDB-Bedingungen zur Darstellung der Angabe (Wortlaut, Position)? Die vollständigen API-Bedingungen wurden noch nicht gelesen.
- [ ] Dürfen wir die Daten nutzen (Lizenz, Nutzungsbedingungen, Scraping erlaubt)? Gibt es offene Dumps?
- [ ] Wie aktuell und wie korrekt sind die Daten? Besonders XP-Werte und Drop-Raten sind teils geschätzt oder stammen aus Community-Beobachtungen.
- [ ] Wie gehen wir mit **Unsicherheit** um (Drop-Raten sind Stichproben, XP-Werte können sich pro Patch ändern)?

## KI-Erstellung

- [ ] Was genau soll die KI machen: Add-on-Code schreiben, Guides aus Daten erzeugen, beides?
- [ ] Wie prüfen wir die Ergebnisse, ohne alles von Hand zu testen? (Automatische Tests auf den Daten, Konsistenzprüfungen, Stichproben im Spiel)
- [ ] Wie testen wir das Add-on? Gibt es einen Weg außerhalb des Spiels (Lua-Tests, Mock der WoW-API), und wie sieht der Test im Client aus?

## Lehrer und Klassen (neu)

- [ ] **[Entscheidung] Welche Klasse zuerst?** Für Lehrer-Besuche (siehe [04-routenlogik.md](04-routenlogik.md)) und Kampftempo muss der Plan die Klasse kennen. Bisher gibt es nur einen Plan nach Volk (Mensch).
- [ ] Wie groß ist der Nutzen neuer Fähigkeiten pro Klasse und Level (Kill-Zeit), und wie wird er kalibriert (Sammeldaten ab niedrigem Charakter)?
- [ ] Soll das Add-on im Spiel dynamisch erkennen, dass beim Lehrer neue Zauber warten (Zauber mit erreichtem Mindestlevel, noch nicht gelernt)?
- [ ] Wie behandeln wir Klassen, deren Lehrer nicht in der Startzone sitzen?

## Reisen und Spielerzustand (neu)

- [x] **Plan hängt vom Zustand ab:** Bekannte Flugpunkte, Ruhestein-Heimat und Abklingzeit ändern die beste Route bei gleichem Level und gleichen Quests (siehe [10-routing-konzepte.md](10-routing-konzepte.md)). **Entschieden (8.11.2026): beides.** Vorberechnetes Gerüst für den typischen Zustand plus leichte Neubewertung im Spiel für die Abweichung.
- [ ] Welche Zustandsgrößen kann das Add-on im Forever-Client sicher lesen (bekannte Flugpunkte, Heimat, Ruhestein-Abklingzeit)?
- [ ] Welche Wegverbindungen fehlen in unseren Daten (Schiffe, Zeppeline, Portale, Ruhestein-Ziele)?
- [ ] Alltags-Stopps (Lehrer, Händler, Reparatur, Taschen) als Gelegenheiten mit Nutzen-Funktion: Welche Daten brauchen wir (Händlerliste, Preise, Haltbarkeit)?

## Technik und Betrieb

- [ ] Wie wird das Add-on verteilt (CurseForge, GitHub, nur privat)?
- [ ] Soll es nur privat genutzt werden oder öffentlich? Das beeinflusst Lizenz- und Datenfragen.
- [ ] Welche Regeln gelten für Add-ons (Terms of Service, keine automatisierte Steuerung)?

## Parkplatz für lose Gedanken

_(Hier neue Ideen ungefiltert ablegen, wir sortieren sie später ein.)_

-
