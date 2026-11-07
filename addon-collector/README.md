# Forever Data Collector (temporär)

Kleines Hilfs-Add-on, das beim normalen Spielen Daten für die Kalibrierung des Leveling-Planers mitschreibt. Es liest nur Informationen, die das Spiel dem Spieler ohnehin zeigt, und automatisiert nichts.

**Status:** Prototyp, im Spiel noch nicht getestet. Die Schnittstellen sind defensiv geschrieben (jede Abfrage ist abgesichert), aber nicht jede Funktion ist im Forever-Client gesichert vorhanden. Bitte Fehlermeldungen im Chat zurückmelden.

## Installieren

1. Den Ordner `ForeverDataCollector` (mit `.toc` und `.lua`) in den AddOns-Ordner des Forever-Clients kopieren, z. B. `…\World of Warcraft\<Forever-Ordner>\Interface\AddOns\`. Der genaue Ordnername hängt von deiner Installation ab.
2. Spiel starten (oder `/reload`). Im Chat erscheint `FDC 0.1.0 loaded`.
3. Falls das Add-on als „veraltet" markiert ist, im Add-on-Menü „Veraltete Add-ons laden" aktivieren.

## Befehle

| Befehl | Wirkung |
|---|---|
| `/fdc status` | zeigt, wie viele Einträge gesammelt wurden |
| `/fdc scan` | schreibt alle Quests im Questlog mit XP-Belohnung auf |
| `/fdc pause` / `/fdc resume` | Aufzeichnung anhalten oder fortsetzen |
| `/fdc note <Text>` | Notiz mit Zeitstempel (z. B. „Auf Abbey-Eingang gestellt") |
| `/fdc reset` | alle Daten löschen |

## Was gesammelt wird

- **Quests:** XP- und Gold-Belohnung im Quest-Dialog (vor dem Annehmen und beim Abgeben), Ziele mit Mengen, XP bei Abgabe, Zeiten.
- **Kills:** Mob-Name, XP, Spielerlevel, Mob-Level (wenn anvisiert), Position, Abstand zum vorigen Kill.
- **Drops:** Was pro Leiche gelootet wurde (NPC-ID und Item-IDs).
- **Bewegung:** alle 2 Sekunden Position und Geschwindigkeit, solange du dich bewegst (prüft Kartengröße und Lauftempo).
- **XP-Kurve:** `UnitXPMax` pro Level.
- Es werden **keine** Charakternamen gespeichert, nur Klasse, Volk, Fraktion und Level.

## Zweck: passive Kalibrierung, keine Messaufgaben

Das Add-on soll **beim normalen Spielen mitlaufen**, damit niemand Strecken abstoppen oder Befehle wie `UnitXPMax` eintippen muss. Es ist ausdrücklich **nicht** dafür gedacht, die Datenlücken bei neuen Forever-Inhalten zu schließen (dafür deckt ein einzelner Spieler zu wenig ab).

Was sich daraus offline ableiten lässt:

| Daten | Ableitung |
|---|---|
| Position + Geschwindigkeit (alle 2 s) | tatsächliche Lauf- und Reittempo, Kartenmaßstab (Strecke aus Tempo × Zeit gegen Karten-Prozent), Anteil der Zeit ohne Bewegung |
| Kills mit XP, Spielerlevel, Mob-Level | Prüfung der Kill-XP-Formel (Level-Abhängigkeit) |
| Kampfdauer und Abstand zwischen Kills | Zeitanteile für Kampf, Wege und Pausen (bei einem übermächtigen Charakter nur eingeschränkt aussagekräftig) |
| XP-Bedarf pro Level (automatisch bei Level-Ups und Login) | XP-Kurve ohne Chat-Befehl |
| Quest-XP aus Dialogen, die du ohnehin öffnest | Stichproben zum Abgleich mit den Classic-Werten |
| Looten | grobe Drop-Stichproben |

Einfach spielen. Mit einem niedrigstufigen Charakter sind Kampf- und Pausen-Zeiten brauchbarer.

## Daten zurückholen

Beim Ausloggen (`/reload` oder Beenden) schreibt das Spiel `ForeverDataCollector.lua` nach
`WTF\Account\<ACCOUNT>\SavedVariables\ForeverDataCollector.lua`.
Diese Datei kopierst du in den Projektordner, z. B. nach `F:\Code\leveling-add-on\data\collected\`. Sie bleibt dort lokal (`data/` ist teilweise gitignoriert, die Datei nicht ins Repo legen, sie enthält Spiel-Zeitstempel).

## Entfernen

Ordner `ForeverDataCollector` aus `Interface\AddOns\` löschen und die SavedVariables-Datei bei Bedarf ebenfalls.
