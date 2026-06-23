# HEPARA Docker Image Overview

HEPARA is a High Energy Physics AI Research Assistant that helps researchers search and analyze papers, track citations, recommend recent arXiv papers, retrieve particle properties and decays from PDG, and answer general HEP questions using downloaded-paper context or Google Search. This Docker image packages the local Streamlit app together with Ollama, so users can run the assistant locally with one container.

Source code and documentation are available in the GitHub repository: [zjzhao1002/HEP-AI-Assistant](https://github.com/zjzhao1002/HEP-AI-Assistant).

The image includes:

-   The HEPARA Streamlit web app
-   Specialized arXiv, INSPIRE-HEP, FAQ, and PDG agents
-   Python dependencies managed by `uv`
-   Ollama for local keyword extraction and trend recommendations
-   Persistent storage support for user configuration, citation records, downloaded papers, the Chroma index, and Ollama models

## Quick Start

Pull the image:

```bash
docker pull zjzhao1002/hepara:latest
```

Run the app:

```bash
docker run --rm -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  zjzhao1002/hepara:latest
```

Open the app at:

```text
http://localhost:8501
```

In the Streamlit sidebar, enter your `GOOGLE_API_KEY`, `AUTHOR`, `CATEGORIES`, and model settings, then click **Save configuration**.

## Persistent Data

The container uses two recommended Docker volumes:

-   `hepara-data`: stores saved configuration, citation records, downloaded PDFs, generated Markdown sidecars, and the Chroma index.
-   `hepara-ollama`: stores downloaded Ollama models.

Downloaded PDFs are saved inside the container at:

```text
/app/data/pdf
```

The saved Streamlit configuration is persisted through:

```text
/app/data/.env
```

Citation tracking records are also stored under `/app/data`, so citation updates remain available after restarting the container.

Downloaded-paper retrieval data is stored under `/app/data/pdf/chroma_db` and therefore persists in the `hepara-data` volume as well.

## Ollama Model

By default, the container uses:

```text
llama3
```

On first startup, the container starts Ollama and pulls the configured model if it is not already available in the `hepara-ollama` volume. This can take a while depending on the model size and network speed.

To use a different Ollama model:

```bash
docker run --rm -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  -e OLLAMA_MODEL=qwen2.5 \
  zjzhao1002/hepara:latest
```

## Required Configuration

Most users should configure these values from the Streamlit sidebar:

-   `GOOGLE_API_KEY`: Google Gemini API key
-   `AUTHOR`: author name or INSPIRE-HEP author identifier
-   `CATEGORIES`: arXiv categories of interest, such as `hep-ph, hep-th`
-   `GOOGLE_MODEL`: Gemini model for the main assistant
-   `OLLAMA_MODEL`: Ollama model for local arXivFlow keyword extraction

The local Docker app sets:

```text
ARXIVFLOW_KEYWORD_BACKEND=ollama
PDF_PATH=/app/data/pdf
```

## Ports

The container exposes:

-   `8501`: Streamlit web app
-   `11434`: Ollama API

## Build and Redeploy

Run these commands from the repository root.

Build the image locally:

```bash
docker build -t hepara-local .
```

Test the local image before publishing it:

```bash
docker run --rm --name hepara-test \
  -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  hepara-local
```

Open <http://localhost:8501> and verify the updated agent behavior. Stop the test container with `Ctrl+C`.

Log in to Docker Hub, then publish versioned and `latest` multi-platform images. Set `VERSION` to the release tag you want to publish:

```bash
docker login

IMAGE=zjzhao1002/hepara
VERSION=v0.1.1

docker buildx build \
  --platform linux/amd64,linux/arm64 \
  -t "$IMAGE:$VERSION" \
  -t "$IMAGE:latest" \
  --push .
```

On the deployment host, pull the new image and replace the running container:

```bash
docker pull zjzhao1002/hepara:latest
docker stop hepara 2>/dev/null || true
docker rm hepara 2>/dev/null || true

docker run -d \
  --name hepara \
  --restart unless-stopped \
  -p 8501:8501 -p 11434:11434 \
  -v hepara-data:/app/data \
  -v hepara-ollama:/root/.ollama \
  zjzhao1002/hepara:latest
```

Follow the startup logs:

```bash
docker logs -f hepara
```

The named volumes are reused during replacement, so saved settings, citation records, downloaded papers, the Chroma index, and Ollama models are preserved.

## Notes

-   The image is intended for local use.
-   The first run may be slower because Ollama needs to download the selected model.
-   Keep the recommended volumes if you want saved configuration, citation history, PDFs, and Ollama models to survive container restarts.
-   The container runs Ollama and Streamlit together for convenience.
