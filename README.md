# Customer Contact n8n Workflow

A centralized `n8n` workflow for processing customer interactions from multiple channels, including webhooks, audio uploads, and inbound email. The system uses `n8n` to turn raw customer communication into structured, reviewable records. It supports transcription, speaker diarization, summarization, sentiment analysis, and follow-up classification.

## Features

- Accepts customer input from:
  - JSON webhooks
  - audio uploads for calls or voicemail
  - inbound email via IMAP
- Transcribes and diarizes audio input
- Normalizes incoming data into a consistent schema
- Generates German summaries using an LLM
- Classifies sentiment as `good`, `neutral`, or `bad`
- Flags follow-up items with `open_todo=true`
- Flags critical cases with `is_critical=true`
- Stores processed contacts in the `customer_contacts` table

## Repository Structure

- `docker-compose.yml` — local stack for all services
- `n8n/customer-contact_n8n_workflow.json` — exported n8n workflow
- `webapp/` — browser UI for sending test text and audio payloads
- `audio-processing-api/` — FastAPI service for transcription and diarization

## Architecture

### Services

- `n8n`: `http://localhost:5678`
- `webapp`: `http://localhost:8000`
- `audio-processing-api`: `http://localhost:8001`
- `ollama`: `http://localhost:11434`

## Requirements

Before starting, make sure you have:

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- an [AssemblyAI](https://www.assemblyai.com/) API key for diarization

Optional:

- IMAP credentials for inbound email processing
- SMTP or other email credentials for notification steps in `n8n`

## Quickstart

### 1. Configure environment variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then update the values in `.env` to match your local setup.

### 2. Start the services

Start the default stack:

```bash
docker compose up --build -d
```

Stop the stack:

```bash
docker compose stop
```

### 3. Enable Ollama locally (optional)

If you want to run Ollama locally, start the full profile and pull the model:

```bash
docker compose --profile full up --build -d
docker exec -it ollama ollama pull llama3.2:3b
```

Notes:

* The model download may take some time.
* It requires roughly 10 GB of disk space.

### 4. Initialize n8n

Open:

```text
http://localhost:5678
```

Complete the first-time owner setup, then:

1. Open `n8n`.
2. Import `n8n/customer-contact_n8n_workflow.json`.
3. Run the `Manual Trigger` once to create the `customer_contacts` data table.
4. Configure the credentials referenced by the workflow.
5. Activate the workflow.

#### Ollama note

If you use the local `ollama` service, set the base URL of the model credentials to:

```text
http://ollama:11434
```

If you do not want to use Ollama, replace the LLM node with another supported model provider.

### 5. Test the setup

Open the test UI:

```text
http://localhost:8000
```

The UI allows you to:

* send text messages to `/webhook-test/...` or `/webhook/...`
* upload audio files to test or production webhook endpoints

## Development

### Audio Processing API

The audio service exposes:

* `POST /api/transcribe`
  Uses `faster-whisper` with the `small` model on CPU
* `POST /api/diarize`
  Uses AssemblyAI and returns speaker-grouped transcript segments

### Web App

The web app is a lightweight FastAPI application that serves a single HTML page for manual testing.

It includes:

* an audio upload form with a phone number field
* a message form with name, email, phone, subject, and message
* a sample-message selector for quickly sending predefined customer requests

## Known Limitations

* The demo setup does not include authentication for the UI, webhooks, or `n8n`.
* The workflow is currently built for German contacts and summaries.
* The bundled `llama3.2:3b` model may be too weak for reliable structured output.
* Diarization depends on AssemblyAI and requires outbound network access.
* Critical-case detection currently relies on simple rules rather than a more robust decision model.

## Testing

There is currently no automated test suite.

For now, validation is manual:

1. Start the stack with Docker Compose.
2. Open the web UI at `http://localhost:8000`.
3. Submit sample text messages and audio files to the test webhooks.
4. Confirm that contacts are processed and written to the `customer_contacts` table in `n8n`.
