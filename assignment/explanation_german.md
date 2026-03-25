# Ergebnis

## 1. Datenmodell mit Begründung

### Tabelle `customer_contacts`

| Feld | Typ |
| --- | --- |
| `id` | uuid |
| `source_channel` | string |
| `customer_name` | string |
| `customer_email` | string |
| `customer_phone` | string |
| `subject` | string |
| `text` | string |
| `summary` | string |
| `sentiment` | string |
| `open_todo` | boolean |
| `is_critical` | boolean |

### Begründung

- Es enthält sowohl Rohdaten als auch Ergebnise der Analyse in einem Datensatz.
- Es funktioniert für alle drei Kanäle ohne separates Tabellenschema.

## 2. Modellwahl

### Modell 1: `faster-whisper` mit Modell `small`

Einsatz:

- Lokale Transkription im Service `audio-processing-api`
- Endpoint: `POST /api/transcribe`

Warum dieses Modell:

- `faster-whisper` ist eine effizientere Implementierung von OpanAi's [whisper](https://github.com/openai/whisper)
- Kleines Modell das gut lokal auf der CPU läuft und gut für Demo-Zwecke geeignet ist.
- Größere Whisper-Modelle liefern bessere Genauigkeit, benötigen aber mehr CPU/RAM und erhöhen die Laufzeit deutlich.

### Modell 2: AssemblyAI Speaker Diarization

Einsatz:

- Transkription und Speaker Diarization per AssemblyAI API im Service `audio-processing-api`
- Endpoint: `POST /api/diarize`

Warum dieses Modell:

- Speaker Diarization ist deutlich aufwendiger.
- Für die Demo war eine API praktischer, da dadurch der aufwendige lokale Aufbau mit PyTorch, CUDA und zusätzlicher Modellinstallation vermieden werden konnte.

OpenSource Alternativen:

- [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- [WhisperX](https://github.com/m-bain/whisperx)

### Modell 3: `llama3.2:3b` über Ollama

Einsatz:

- Zusammenfassung
- Sentiment-Klassifikation
- Erkennung von `open_todo`

Warum dieses Modell:

- Lokal betreibbar und dadurch ohne direkte Tokenkosten pro Request.
- Einfache Integration über den n8n-Ollama-Node.

Nachteile:

- Für produktive Qualitätsanforderungen ist `llama3.2:3b` nicht ausreichend.
- Das Modell ist für zuverlässig strukturierten Output zu schwach.

## 3. Kostenanalyse

### Annahmen

- Webhook- und E-Mail-Anfragen verursachen in der aktuellen Architektur keine direkten externen Modellkosten.
- Die lokale Transkription mit `faster-whisper` und die LLM-Auswertung mit Ollama erzeugen keine nutzungsbasierten API-Kosten.
- Variable Fremdkosten entstehen im Wesentlichen bei Audioanfragen durch AssemblyAI.
- Grundlage für AssemblyAI: offizielle Pricing-Seite, Pre-recorded Speech-to-Text ab `0.15 USD / Stunde`.
- Die Berechnung unten betrachtet nur variable Request-Kosten, nicht Server-, Storage- oder Betriebsaufwand.

### Formel für Audio-Requests

`Kosten pro Request = Audiolänge in Stunden * 0.15 USD`

Beispiele:

| Audio pro Request | Kosten pro Request | Kosten bei 1.000/Monat | Kosten bei 10.000/Monat |
| --- | --- | --- | --- |
| Text/E-Mail ohne Audio | ca. `0.00 USD` | ca. `0 USD` | ca. `0 USD` |
| 1 Minute Audio | `0.0025 USD` | `2.50 USD` | `25.00 USD` |
| 5 Minuten Audio | `0.0125 USD` | `12.50 USD` | `125.00 USD` |
| 10 Minuten Audio | `0.0250 USD` | `25.00 USD` | `250.00 USD` |

### Anmerkungen

- Die externen Kosten steigen nahezu linear mit dem Audioanteil.
- In der Praxis kommen noch Infrastrukturkosten für Docker-Host, n8n, Datenhaltung und lokale Modellinferenz hinzu.

## 4. Erklärung der Speaker-Diarization-Lösung

Die Speaker-Diarization wird nicht in n8n selbst umgesetzt, sondern in einem separaten FastAPI-Service unter `audio-processing-api`.

### Ablauf

1. Ein Audio-Upload trifft im n8n-Webhook ein.
2. n8n sendet die Datei an `POST /api/diarize`.
3. Der Service lädt die Datei zu AssemblyAI hoch.
4. Dort wird eine Transkription mit aktivierten `speaker_labels` gestartet.
5. Die API liefert Wortobjekte inklusive Sprecher-ID zurück.
6. Der lokale Service gruppiert aufeinanderfolgende Wörter desselben Sprechers zu Segmenten.
7. Aus diesen Segmenten entsteht ein sprechergetrennter Text im Format `Speaker A: ...`.
8. Dieser normalisierte Text wird anschließend im n8n-Flow weiterverarbeitet.
