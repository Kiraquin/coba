#!/usr/bin/env python3
"""Simple web server + API proxy for background removal."""

from __future__ import annotations

import io
import json
import mimetypes
import os
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib import error, request
import cgi

ROOT = Path(__file__).resolve().parent
MAX_IMAGE_SIZE = 12 * 1024 * 1024
REMOVE_BG_URL = "https://api.remove.bg/v1.0/removebg"


def json_response(handler: BaseHTTPRequestHandler, status: int, payload: dict) -> None:
    body = json.dumps(payload).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


class AppHandler(BaseHTTPRequestHandler):
    server_version = "CleanCutServer/1.0"

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/api/health":
            json_response(self, HTTPStatus.OK, {"status": "ok"})
            return

        target = "index.html" if self.path in ("/", "") else self.path.lstrip("/")
        file_path = (ROOT / target).resolve()

        if ROOT not in file_path.parents and file_path != ROOT:
            self.send_error(HTTPStatus.FORBIDDEN, "Forbidden")
            return

        if not file_path.exists() or not file_path.is_file():
            self.send_error(HTTPStatus.NOT_FOUND, "File not found")
            return

        content_type = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/api/remove-background":
            self.send_error(HTTPStatus.NOT_FOUND, "Not Found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {"error": "Request must be multipart/form-data with an image field."},
            )
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
            },
        )

        if "image" not in form:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Field 'image' is required."})
            return

        image_item = form["image"]
        image_bytes = image_item.file.read() if image_item.file else b""
        if not image_bytes:
            json_response(self, HTTPStatus.BAD_REQUEST, {"error": "Uploaded image is empty."})
            return

        if len(image_bytes) > MAX_IMAGE_SIZE:
            json_response(self, HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "Image too large (max 12MB)."})
            return

        filename = image_item.filename or "upload.png"
        api_key = os.getenv("REMOVE_BG_API_KEY")
        request_key = form.getfirst("api_key", "").strip()
        final_key = request_key or api_key

        if not final_key:
            json_response(
                self,
                HTTPStatus.BAD_REQUEST,
                {
                    "error": "API key missing. Set REMOVE_BG_API_KEY on server or send api_key field.",
                },
            )
            return

        boundary = "----CleanCutBoundary"
        payload = io.BytesIO()
        payload.write(f"--{boundary}\r\n".encode())
        payload.write(
            f'Content-Disposition: form-data; name="image_file"; filename="{filename}"\r\n'.encode()
        )
        mime = image_item.type or "application/octet-stream"
        payload.write(f"Content-Type: {mime}\r\n\r\n".encode())
        payload.write(image_bytes)
        payload.write(b"\r\n")
        payload.write(f"--{boundary}\r\n".encode())
        payload.write(b'Content-Disposition: form-data; name="size"\r\n\r\nauto\r\n')
        payload.write(f"--{boundary}--\r\n".encode())
        body = payload.getvalue()

        req = request.Request(
            REMOVE_BG_URL,
            method="POST",
            data=body,
            headers={
                "X-Api-Key": final_key,
                "Content-Type": f"multipart/form-data; boundary={boundary}",
            },
        )

        try:
            with request.urlopen(req, timeout=120) as response:
                output = response.read()
                status = response.status
                out_type = response.headers.get("Content-Type", "image/png")
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            json_response(self, exc.code, {"error": "remove.bg request failed", "details": details})
            return
        except Exception as exc:  # noqa: BLE001
            json_response(self, HTTPStatus.BAD_GATEWAY, {"error": f"Proxy error: {exc}"})
            return

        if status != HTTPStatus.OK:
            json_response(self, status, {"error": "Unexpected response from remove.bg"})
            return

        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", out_type)
        self.send_header("Content-Length", str(len(output)))
        self.end_headers()
        self.wfile.write(output)


def main() -> None:
    port = int(os.getenv("PORT", "8000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), AppHandler)
    print(f"Server running on http://0.0.0.0:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
