# Recherche: WoW Forever und Leveling-Add-ons

Stand: 2026-11-07. Erste Recherche per Websuche. Vieles stammt von **Fan- und Kommerzseiten**, die sich teils widersprechen und zum Teil vor dem Launch geprüft wurden. Aussagen mit **(unbestätigt)** sind nicht aus offiziellen Quellen verifiziert. Vor Entscheidungen CurseForge und die GitHub-Seiten der Add-ons direkt prüfen.

## Was ist WoW Forever?

- **Eine eigene, offizielle dritte Version** neben Retail und Classic, kein Classic-Server und keine Season. Quelle: [Blizzard-Launch-News](https://news.blizzard.com/en-us/article/24315820/world-of-warcraft-forever-now-live) (laut Suchergebnis).
- **Launch: 4. November 2026.** Im normalen Abo enthalten.
- **Level 1–60**, Cap bleibt 60. Eastern Kingdoms und Kalimdor mit **neuen und überarbeiteten Zonen und über 1.000 neuen Quests**, neun neue Dungeons (Level 13–60), neue Rasse. Raids ab 9. Dezember (laut Blizzard-Post).
- **Realmless:** Man wählt ein Regelset (Normal, PvP, Roleplay, Hardcore später) statt eines Realms.
- Fanseiten nennen Client-Version **1.60.1**, Interface **16001**, interner Name „Camelot" **(unbestätigt)**. Läuft auf modernem Client mit eingebautem Damage-Meter, Edit Mode usw.

**Folge für uns:** Die Datenbasis ist *nicht* einfach Classic. Neue Quests, neue Zonen und überarbeitete Gebiete bedeuten, dass reine Classic-Daten **lückenhaft oder falsch** sind. Das ist der wichtigste Befund dieser Recherche.

## Bestehende Add-ons

| Add-on | Forever-Stand | Eigene Guides? | Einschätzung |
|---|---|---|---|
| **Questie** | Forever-Version vorhanden (v12.x), bekannte Lücken (laut Fanseiten 17 offene Forever-Issues, fehlende Questlinien) | nein, ist Questdaten und Kartenmarker | Datenquelle und Marker, aber Daten für neue Quests unvollständig |
| **Guidelime** | Forever-Version vorhanden (v6.01x), braucht Questie | Editor für eigene Guides laut Fanseite, auf Forever **nicht verifiziert** | Guide-Engine mit Anzeige und Quest-Tracking |
| **RestedXP** | Forever-Version vorhanden, Guides kostenpflichtig, 1–35 fertig, 35–60 pending **(unbestätigt)** | geschlossen | nicht erweiterbar, nicht nutzbar als Basis |
| **Zygor** | eigener Client, kostenpflichtiges Abo, teilweise Forever-Abdeckung | geschlossen | nicht nutzbar als Basis |
| **WoW-Pro** | keine Forever-Version gefunden | – | irrelevant |

Fertige Guide-Packs für Guidelime auf Forever: **TUGs** und **Sage** (Letzteres nur Allianz). Die Teile für Level 30–60 sind laut Fanseite während der Beta entstanden und passen evtl. nicht zur Live-Version **(unbestätigt)**.

## Guidelime: was kann man damit?

Belegt ist das nur für die **GuidelimeVanilla-Fork-Dokumentation** (Interface 1.12, TurtleWoW), nicht für das Forever-Build. Sie zeigt aber das Konzept, das vermutlich verwandt ist ([Guide Pack API](https://github.com/JeromeM/GuidelimeVanilla/wiki/Guide-Pack-API), [Creating a Guide](https://github.com/JeromeM/GuidelimeVanilla/wiki/Creating-a-Guide)):

- Ein **separates Add-on** kann Guides registrieren: `GLV:RegisterGuide(guideText, groupName, addonName)`, `.toc` mit Abhängigkeit auf Guidelime.
- Guides sind **Text mit Tags**: Quest annehmen/abgeben/erledigen (`[QA id]`, `[QT id]`, `[QC id]`), Koordinaten, NPC-Ziele, optionale Schritte, Klassen-/Rassenfilter, Verkettung von Guides.
- `RegisterGuide` nimmt einen String. Ein Add-on **könnte** Guide-Text zur Ladezeit per Lua erzeugen. Das ist eine Schlussfolgerung, nicht dokumentiert.
- **Nicht dokumentiert:** Guides nachträglich ändern oder entfernen, Schritte dynamisch umsortieren oder bedingt überspringen (außer Klasse/Rasse/Fraktion), Bewertung nach XP/h. Auch eine Lizenz stand auf den gelesenen Seiten nicht.

## Fazit zu deiner Vermutung

Du hast im Kern recht. Es gibt **kein brauchbares Skelett für die dynamische Logik**:

- Guidelime ist eine **Engine für starre, textbasierte Guides** mit Anzeige, Pfeil und Questverfolgung. Dynamische Neubewertung, Bündel-Synergien und XP/h-Optimierung sind darin nicht vorgesehen.
- RestedXP und Zygor sind geschlossen, kostenpflichtig und scheiden aus.
- Questie ist wertvoll als **Datenquelle und Referenz**, aber nicht als Routenlogik.

Offen bleibt, ob Guidelime als **Anzeigeschicht** taugt (Pfeil, Kartenmarker, Questtracking), während unsere eigene Logik darüber entscheidet, welcher Schritt als Nächstes kommt. Ob das auf dem Forever-Build technisch geht, ist ungeprüft.

## Datenquellen für Forever (erste Funde)

- **Wowhead Forever**, **ForeverDB** (foreverdb.net, wird per Spieler-Upload und Add-on befüllt), **QuestieDB für Forever** und die **Client-Tabellen (Build 1.60.1)** tauchen als Quellen in Forever-Add-ons auf, z. B. beim Add-on „Forever Guide" **(unbestätigt)**.
- Lizenz und Nutzungsbedingungen aller dieser Quellen sind **ungeklärt**.

## Nächste Recherche-Schritte

1. Guidelime auf Forever: Gibt es eine Guide-Pack-API im Forever-Build, welche Tags, welche Lizenz? Quelltext auf GitHub/CurseForge lesen.
2. Questie-Datenbank für Forever: Format, Lizenz, Vollständigkeit bei neuen Quests.
3. Wie kommen wir an XP-Tabellen, Quest-XP und Mob-Daten für Forever (Client-Tabellen, Wowhead Forever, ForeverDB)? Was ist erlaubt?
4. Offizielle Add-on-API-Doku für Forever: Interface-Nummer, Unterschiede zu Classic, verfügbare Funktionen (Questlog, Position, Karte).
5. Offizielle Quelle für Level-Anforderungen und XP-Kurve in Forever (ob identisch mit Classic).
