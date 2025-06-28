# DroneGuru Bot

DroneGuru is a Telegram bot that provides VTOL drone information, Q\&A, and model comparisons using Mistral LLM and Whisper for voice input. (@DroneGuru_bot)

## Features

* ❓ Ask any question about VTOL drones via text or voice.
* 📊 Compare multiple drone models side by side.
* 🔍 Search and answer using an embedded drone database.
* 🎧 Voice responses generated in Russian, English, and Chinese.
* 🔄 Caching for faster repeated queries.
* 💾 Embedded drone database at \app\static_files\db.json

## Repo Structure

```
├── Dockerfile
├── docker-compose.yml
├── README.md
├── app/
│   ├── main.py          # Entry point
│   ├── ffmpeg-7.0.2-essentials_build.rar 
│   ├── handlers.py      # Bot logic
│   ├── config.py        # Tokens & keys
│   ├── keyboards/       # Inline keyboards
│   ├── static_files/    # Bot answer templates
│   ├── new_voice_handler.py
│   └── workTools/       # DB, TTS, LLM clients, cache
└── requirements.txt
```

## Prerequisites

* **ffmpeg**: Download and unzip the ffmpeg binaries (e.g., from [ffmpeg.org](https://ffmpeg.org/)), then add the `ffmpeg` executable directory to your system `PATH` so it can be invoked globally.
* **Docker & Docker Compose** installed
* Telegram bot token (`TG_TOKEN`)
* OpenRouter API key (`OPENROUTER_API_KEY`)
* (Optional) Ollama installed or using hosted LLM endpoint

## Building & Running

### 1. Build the Docker image

```bash
docker build -t droneguru .
```

### 2. Start with Docker Compose

```bash
docker-compose up -d
```

This will:

* Pull/build the `droneguru` service
* Install dependencies, Whisper, and Ollama client
* Launch the bot

### 3. Verify

Check logs:

```bash
docker-compose logs -f droneguru
```

You should see:

```
🚀 Bot is running...
```

## Usage

* Open your bot in Telegram.
* Select language.
* Use the menu to ask questions, view specs, or compare models.

## Development

To run locally without Docker:

```bash
pip install -r requirements.txt
export TG_TOKEN=...
export OPENROUTER_API_KEY=...
python app/main.py
```

## License

MIT
