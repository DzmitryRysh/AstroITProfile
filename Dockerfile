FROM python:3.12-slim-bookworm

# Build tools needed for native wheels such as pyswisseph / cffi.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -c "import swisseph; import fastapi; import uvicorn"

COPY app ./app
COPY data ./data

RUN mkdir -p /data

ENV PORT=8000
ENV ASTROIT_WORKSPACE_STORE_PATH=/data/workspaces.json

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=25s --retries=3 \
  CMD python -c "import os,urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT','8000'), timeout=3)"

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
