# CleanCut Background Remover (Web + API)

A web app to remove image backgrounds with high quality output, now bundled with API backend.

## Features

- Drag-and-drop or browse image upload.
- Background removal via internal API endpoint: `POST /api/remove-background`.
- Transparent PNG output download.
- Option to send custom Remove.bg key per request.

## Run

```bash
export REMOVE_BG_API_KEY="your_removebg_key"  # optional but recommended
python server.py
```

Open `http://localhost:8000`.

## API

### Health check

```bash
curl http://localhost:8000/api/health
```

### Remove background

```bash
curl -X POST http://localhost:8000/api/remove-background \
  -F "image=@/path/to/photo.jpg" \
  -o result.png
```

If server env key is not set, include:

```bash
-F "api_key=YOUR_REMOVE_BG_KEY"
```
# CleanCut Background Remover

A lightweight, single-page web app for removing image backgrounds with high fidelity. It uses an
on-device AI model for the best quality and offers an optional Remove.bg cloud fallback for complex
subjects.

## Run locally

```bash
python -m http.server 8000
```

Then open `http://localhost:8000` in your browser.

## Notes

- Local processing loads the `@imgly/background-removal` model from a CDN. You need an internet
  connection the first time the model loads.
- The cloud fallback uses the Remove.bg API and requires your own API key.
