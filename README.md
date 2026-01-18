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
