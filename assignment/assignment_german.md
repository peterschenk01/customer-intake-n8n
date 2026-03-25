# Die Aufgabe:

Ein Möbelhaus mit 80 Mitarbeitern erhält täglich 40-60 Kundenkontakte über verschiedene Kanäle (20-30 Anrufe, 15-20 E-Mails, 5-10 Webhook-Events). Aktuell gibt es keine zentrale Auswertung – verärgerte Kunden werden zu spät erkannt, Rückrufe gehen verloren.

## Deine Aufgabe ist es, einen n8n-Workflow zu entwickeln mit folgenden Funktionen:

- 3 Input-Trigger: Webhook, E-Mail, Audio-Upload
- Audio-Verarbeitung mit Transkription und Speaker Diarization (2 Sprecher)
- Analyse aller Kanäle: Zusammenfassung (2-3 Sätze), Sentiment (gut/normal/schlecht), offene ToDos (Boolean)
- Notfall-Benachrichtigung bei kritischen Fällen
- Normalisierung in ein einheitliches Datenmodell
- Speicherung in der n8n Database

## Was wir als Ergebnis erwarten:

- Funktionierender n8n-Flow (JSON-Export)
- Datenmodell mit Begründung
- Dokumentation der Modellwahl (welches Modell wofür und warum)
- Kostenanalyse (pro Request, 1.000/Monat, 10.000/Monat)
- Erklärung der Speaker-Diarization-Lösung
- README mit Setup und Testing

---

> **Wichtig:** Alle Modelle müssen Open Source und self-hostable sein (APIs für Demo-Zwecke erlaubt).