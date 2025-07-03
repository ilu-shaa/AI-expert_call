FROM python:3.10.10-slim

# system deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
       ffmpeg git curl unzip \
 && rm -rf /var/lib/apt/lists/*

# 1) Copy over everything
COPY . .


# 3) Python deps
RUN pip install --no-cache-dir --upgrade pip \
 && pip install --no-cache-dir \
      torch==2.0.0 \
      torchvision==0.15.1 \
      torchaudio==2.0.0 \
      git+https://github.com/openai/whisper.git \
 && pip install --no-cache-dir \
      aiogram==3.4.1 \
      aiofiles==23.2.1 \
      aiohttp==3.9.5 \
      httpx==0.27.0 \
      openai-whisper==20240930 \
      pydub==0.25.1 \
      transformers==4.52.4 \
      "numpy<2.0" \
      python-dotenv==1.0.0 \
      gTTS==2.3.2 \
 && pip install --no-deps --no-cache-dir ollama==0.5.1

WORKDIR /app

COPY . .

CMD ["python", "main.py"]
