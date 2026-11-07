# Routing-Konzepte aus echten Leveling-Guides

Stand: 2026-11-07. Ziel: Konzepte finden, die in unserem Modell (siehe [04-routenlogik.md](04-routenlogik.md)) noch fehlen, ähnlich wie der „Schlenker". Die Auswertung stützt sich auf frei lesbare Guides für WoW Forever. Es sind **Fan-Guides** mit teils beta-nahem Stand, keine offiziellen Quellen.

## Quellenlage (ehrlich)

| Quelle | Wie gelesen | Einschränkung |
|---|---|---|
| [ForeverWisp, Night-Elf-Guide 1–20](https://www.foreverwisp.com/guides/wow-forever-night-elf-leveling-guide) | Anfang und Ende wörtlich, die Mitte (~100.000 Zeichen) nicht | Eigene Angabe: Level-Bänder sind „Planungs-Checkpoints", die XP-Reichweite sei „nicht gemessen" |
| [wowhandbook.com Leveling](https://wowhandbook.com/leveling/) | vollständig | Zonen- und Level-Bänder, wenig Schritt-Details |
| [wowforeverguides.com Leveling](https://wowforeverguides.com/leveling) | ca. 40 von 73 Tausend Zeichen wörtlich, Rest als Zusammenfassung | Zeilen über Level 30 als „geplant"/Vorab-Stand gekennzeichnet |
| [wow4ever.quest 1–20](https://wow4ever.quest/en/articles/guia-subida-1-20-wow-forever) | 40 von 115 Tausend Zeichen wörtlich, Rest Zusammenfassung | Horde und spätere Schritte nicht wörtlich gelesen |
| [Journey](https://getjourney.gg/) | nur Startseite | eigentlicher Guide kostenpflichtig, Inhalt unbekannt |
| [WoW-Pro Guides (GitHub)](https://github.com/Ludovicus-Maior/WoW-Pro-Guides) | README und Parser | Tag-Vokabular **nicht** gefunden (`Notes.md` und Guide-Dateien wurden nicht geladen) |

Nicht verfügbar waren die klassischen Guide-Formate (WoW-Pro-Tags, Guidelime-Code). Das wäre der nächste Recherche-Schritt, um das Vokabular der Schritt-Typen zu bekommen.

## Was die Guides tun, und wie unser Modell dazu steht

Spalte „Stand" bedeutet: **ja** = ergibt sich im Planer, **teils** = ansatzweise, **fehlt** = nicht im Modell.

| Konzept | Beleg (kurz) | Stand | Allgemeines Muster |
|---|---|---|---|
| Schlenker / „nebenbei erledigen" | „Combine this with …", „Finish the other work on this outing before returning" | ja (Einfügekosten, `detour`) | Gelegenheit mit Einfügekosten |
| Nächste erreichbare Aufgabe, nach Ort gruppieren | „always the nearest task you can already do", „group objectives by location" | ja | Wegoptimierung |
| Vor der Reise annehmen / außerhalb abgeben | „Before you come, accept these quests", „Turn in outside this zone" | teils (nur eine Zone) | Mehrere Zonen, Abgabe-Orte außerhalb |
| Kette zu Ende bringen, bevor man den Hub wechselt | „continue a quest chain you have already started …" | teils (Folgequests ja, Hubwechsel-Kosten nur über Wege) | Pfadabhängigkeit |
| Level-Reihenfolge, Zonen überspringen | „penalty for ones you have outgrown", „You can skip …" | teils (nur Quest-XP-Abschlag, nur 1 Zone) | Mehr-Zonen-Planung |
| **Grinden bis zu einem Level** | „If you are below 20, gain the rest here first", „about seven kills for every 1,000 XP" | **fehlt** (Mobs werden nur für Quests getötet) | Reine Grind-Handlung als Auffüller |
| **Empfohlenes Level / Gefahr** | „Skip it if you are below 18", „Recommended level 20 before approaching Alther's Mill" | **fehlt** (nur Mindestlevel) | Risiko je Quest und Level |
| **Ruhestein: Heimat setzen, zurückkehren** | „make Dolanaar your home", „Use your hearthstone to get back to Goldshire" | **fehlt** | Teleport mit Abklingzeit, Heimat als Zustand |
| **Flugpunkte entdecken, Schiffe, Zeppeline** | „Learn this flight path if needed", „Take the boat to Darkshore" | **fehlt** (Daten da, nicht im Planer) | Wegenetz mit Investition (Flugpunkt entdecken) |
| **Questlog-Platz als Ressource** | („Keep unfinished quests through each crossing", Abandon-Tipp bei Journey) | **fehlt** (bei uns bis zu 8 offen, real begrenzt, im Classic 20 bzw. 25 je Client) | Begrenzte Ressource |
| **Taschenplatz, Items mitführen** | „leave bag space", „Keep quest vessels and delivery items until the named hand-in" | **fehlt** | Ressource, Besorgungen |
| **Lehrer-/Berufs-/Händler-Stopps mit Stadtbesuch bündeln** | „Combine a trainer or profession visit with a planned town stop" | **fehlt** (geplant, siehe 04) | Alltags-Gelegenheiten, bündelbar |
| **Ausgeruht-Bonus, Schlafsack, Essen** | „Sit at … campfire … until Boosted Rest", Schlafsack +1 % XP/min bis 3 %, „Well Fed" | **fehlt** | Zustand mit Bonus (Zeit-Investition) |
| **Gruppen- und Dungeon-Schritte** | „take every dungeon quest first", „Attempt this with help; it is not required" | **fehlt** (Planer ist solo) | Optionale Gruppeninhalte, Gesamtreise bewerten |
| **Zeitlimit-Quests, Eskorten** | „five-minute limit", „escort has a 25-minute timer" | **fehlt** | Frist als Bedingung |
| **Sich ausschließende Quests / Auswahl** | „Choose Escape Through Stealth … do not take … Force as well" | teils (`exclusive_to` ist drin) | Entscheidung mit Folgen |
| **Quest-Belohnung / Ausrüstung** | „Check rewards before you skip an old chain", Spalte „quests with gear" | **fehlt** | Belohnungswahl beeinflusst spätere Kämpfe |
| **Quest „nicht verfügbar" aufschieben** | „use Quest unavailable? to defer it" | teils (Add-on: Skip) | Laufzeit-Abweichung |
| **Pull-Kontrolle / vorsichtig** | „Pull them one at a time", „Do not push through higher-level spiders" | **fehlt** | Risiko, Sicherheit |
| **Neue, ungeplante Quests anhängen** | „New Forever quests (Questie hasn't placed them yet)" | teils (Daten ohne Position) | Datenlücken im Plan abbilden |

## Allgemeines Muster dahinter

Fast jede Zeile oben lässt sich auf wenige Bausteine zurückführen. Eine Verallgemeinerung des Planers sollte daher **nicht** Schlenker, Grind oder Lehrer einzeln einbauen, sondern diese Bausteine:

1. **Gelegenheit:** Ort (oder Gebiet), Dauer als Funktion des Zustands, Voraussetzungen, Wirkungen. Quest annehmen, Mobs töten, Lehrer, Händler, Grinden, Ruhestein setzen sind alles Gelegenheiten.
2. **Zustand mit Ressourcen:** Position, Level und XP, Questlog-Platz, Taschenplatz, Ruhestein (Heimat, Abklingzeit), entdeckte Flugpunkte, Ausgeruht-Bonus, Buffs, Respawn-Uhren.
3. **Wegenetz statt Luftlinie:** Zu Fuß, Flugpunkte, Ruhestein, Schiffe und Zeppeline als Kanten mit Zeit und Voraussetzungen. Der Schlenker ist dann der Einfügeaufwand in diesem Netz.
4. **Passive Wirkungen entlang des Wegs:** Kills unterwegs, Erkundung, Ausgeruht-Bonus.
5. **Risiko und Streuung:** Gefahr je Quest und Level, Streuung bei Drops, Zeitlimits.
6. **Dynamische Neubewertung:** Der Plan ist eine Referenz, im Spiel ändert sich der Zustand (Pech bei Drops, Tod, Abweichung), und die Route wird entsprechend angepasst.

## Festgehaltene Ideen (Nutzer, 7.11.2026)

### Reisen, Ruhestein und bekannte Flugpunkte gehören ins Routing

Reisen mit Routen, der Ruhestein und die **bekannten Flugpunkte** müssen in die Planung eingehen. Daraus folgt eine wichtige Eigenschaft:

> **Zwei Spieler mit exakt gleichem Level und denselben abgeschlossenen Quests können eine unterschiedliche beste Route haben**, wenn einer von beiden einen Flugpunkt kennt und der andere nicht (oder wenn ihr Ruhestein an anderen Orten gesetzt ist oder noch Abklingzeit hat).

Konsequenzen:

- **Der Plan hängt vom ganzen Spielerzustand ab**, nicht nur von Level und Questfortschritt. Zustand umfasst mindestens: bekannte Flugpunkte, Heimatort des Ruhesteins samt Abklingzeit, Position. Ein einmal vorberechneter Plan ist deshalb nur eine Referenz für einen typischen Zustand. Das Add-on muss den echten Zustand lesen und bei Abweichung neu bewerten.
- **Flugpunkte sind eine Investition:** Einen Flugpunkt zu entdecken kostet Weg, spart aber später Zeit. Ob sich ein Umweg zum Entdecken lohnt, entscheidet das Zeitmodell, nicht eine Regel („immer alle Flugpunkte mitnehmen").
- **Ruhestein ist ein Teleport mit Abklingzeit und mit Heimat als Zustand.** „Heimat setzen" ist selbst eine Gelegenheit (zum Beispiel an einem Ort, an den man später oft zurückkehrt).
- **Technische Machbarkeit im Spiel (zu prüfen):** Das Add-on kann den Zustand vermutlich lesen (Flugpunkt-Status über die Taxi-Karten-Schnittstelle, Heimatort und Ruhestein-Abklingzeit über die Standard-Funktionen). Ob diese Schnittstellen im Forever-Client wie erwartet vorhanden sind, ist nicht geprüft.
- **Datenlage:** Flugpunkte (`TaxiNodes`) und Verbindungen samt Kosten (`TaxiPath`) liegen aus den Client-Tabellen vor. Es fehlen die Position von Ruhestein-Zielorten und Schiffs-/Zeppelin-Verbindungen.

### Architektur-Entscheidung (Nutzer, 8.11.2026): beides

Der Plan braucht **ein vorberechnetes Gerüst für den typischen Zustand und eine leichte Neubewertung im Spiel** für die Abweichung. Das Gerüst (Strahlsuche, offline) liefert die Referenz, das Add-on liest den echten Zustand (Questlog, Level, bekannte Flugpunkte, Ruhestein) und wählt daraus den nächsten Schritt. Eine Neuberechnung des vollen Plans im Spiel ist wegen der Rechenzeit nicht vorgesehen.

### Alltags-Stopps sind Gelegenheiten

Lehrer, Händler (Verkaufen, Reparieren, Nahrung und Wasser), Taschenplatz und ähnliche Stopps werden als **normale Gelegenheiten** im Planer geführt, mit Kosten (Weg und Dauer) und Nutzen. Sie sind nicht fest vorgeschrieben und können mit anderen Wegen gebündelt werden (die Guides raten: „trainer or profession visit with a planned town stop"). Der Nutzen ist je nach Stopp anders: Lehrer verkürzt künftige Kämpfe, Händler schafft Platz oder Vorräte, Reparatur erhält die Kampfstärke.

## Umsetzungsstand im Planer (8.11.2026)

`pipeline/derive/planner.py` ist auf dieses Konzept umgebaut. Getestet in `pipeline/tests/test_planner_concepts.py` (6 Tests).

| Baustein | Stand |
|---|---|
| Zustand mit Ressourcen: Questlog-Plätze (Parameter `quest_log_slots`, Annahme 20), Heimat und Abklingzeit des Ruhesteins, bekannte Flugpunkte, erlernte Fähigkeitsstufen | umgesetzt |
| Wegenetz: zu Fuß, Ruhestein, Flug; je Ziel der schnellste Weg im aktuellen Zustand | umgesetzt. Der Ruhestein wird im Plan genutzt. Flüge sind mit künstlichen Daten getestet, in den echten Daten gibt es für diese Zonen keine nutzbaren Flugverbindungen |
| Gleicher Level und gleiche Quests, aber anderer Flugpunkt-Zustand → anderer Weg | umgesetzt und getestet |
| Grind-Handlung (Mobs ohne offenen Questbedarf) | umgesetzt |
| „Heimat setzen" und „Flugpunkt entdecken" als Gelegenheiten | umgesetzt (Gastwirt-Erkennung am Namen). Flugpunkt-Entdecken nur im Test, keine echten Daten |
| Lehrer als Errand (Parameter, Beispiel in `params.json`) | umgesetzt als Gerüst: Stufen und Speedup sind Annahmen, keine Klasse gewählt, standardmäßig aus |
| Kill-Portionen aus dem Zustand abgeleitet (kleinste/größte Menge, Spawn-Anzahl, bis zum Level-Up) | umgesetzt (Suchhilfe, kein Spielregel) |
| Gefahr / empfohlenes Level, Ausgeruht-Bonus, Zeitlimit-Quests, Gruppeninhalte, Händler/Taschen | noch offen |

**Wichtiger Befund aus dem Umbau (Empfindlichkeit):** Das Ergebnis hängt stark von der Kill-Zeit ab, weil sie entscheidet, ob Quests oder Grinden besser sind (Level 1 → 10, Strahlbreite 30, Erwartungswerte):

| Sekunden pro Kill | Level 10 nach | Quests abgegeben | Grind-Handlungen |
|---|---|---|---|
| 12 | 73 min | 21 | wenige Portionen |
| 20 | 100 min | 13 | sehr viele kleine Portionen |
| 30 | 124 min | 33 | 1 |

Die Kill-Zeit ist bisher eine **Annahme** (12 s) und für deinen übermächtigen Charakter nicht messbar. Sie ist der wichtigste Parameter zum Kalibrieren. Ohne Messwert ist die Aussage „Quests vs. Grinden" nicht belastbar.

## Folgerungen für die Reihenfolge der Arbeit

Nach Wirkung auf die Zeit und Aufwand geschätzt, vor dem Ausbau auf weitere Zonen:

1. **Grind-Handlung** (einfach, schließt eine echte Lücke: Level-Auffüller und Füllzeit, wenn gerade keine gute Quest verfügbar ist).
2. **Questlog-Platz als Ressource** (einfach, verändert Pläne mit vielen offenen Quests spürbar).
3. **Ruhestein und Flugpunkte im Wegenetz** (Daten liegen vor, wirkt sich ab Mehr-Zonen-Plänen stark aus).
4. **Alltags-Gelegenheiten** (Lehrer, Händler, Taschen) als Gelegenheiten mit Nutzen-Funktion.
5. **Gefahr/Empfohlenes Level** (braucht Daten oder Messwerte aus dem Spiel).
6. **Ausgeruht-Bonus und Buffs**, **Zeitlimits**, **Gruppen-Inhalte** zuletzt.

## Offene Fragen

- Welche Schritt-Typen und Modifikatoren kennen etablierte Guide-Formate (WoW-Pro, Guidelime)? Die Rohdateien und `Notes.md` des WoW-Pro-Repos sind noch nicht gelesen.
- Wie groß ist das Questlog in Forever (Zahl der Plätze)? Muss im Spiel oder in einer verlässlichen Quelle geprüft werden.
- Welche Wegverbindungen gibt es in den Startgebieten (Flugpunkte, Boote), und was kostet das Entdecken eines Flugpunkts?
