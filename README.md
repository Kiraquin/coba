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
