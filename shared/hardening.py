"""Hardening shared by every web app in this project.

- request size limit (CVs are small; anything larger is refused with 413)
- bounded in-memory stores (a public demo must not grow without limit)
- security headers (CSP, no sniffing, no framing by other sites, no referrer leaks)
- error messages chosen from a fixed list, never echoed from the URL
"""
from __future__ import annotations

import os
from collections import OrderedDict

from flask import Flask, render_template, request

MAX_UPLOAD_BYTES = 512 * 1024
LEGAL_URL = os.environ.get("LEGAL_URL", "/legal")

CSP = ("default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; "
       "font-src 'self'; script-src 'self' 'unsafe-inline'; "
       "frame-ancestors 'self'; base-uri 'self'; form-action 'self'")


class BoundedStore(OrderedDict):
    """Dict that forgets its oldest entries beyond `limit` items."""

    def __init__(self, limit: int = 300):
        super().__init__()
        self.limit = limit

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        while len(self) > self.limit:
            self.popitem(last=False)


def harden(app: Flask, errors: dict[str, str] | None = None) -> None:
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_BYTES
    messages = errors or {}

    @app.after_request
    def headers(resp):
        resp.headers.setdefault("Content-Security-Policy", CSP)
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        resp.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        return resp

    @app.context_processor
    def inject():
        code = request.args.get("error", "")
        return {"error_message": messages.get(code), "legal_url": LEGAL_URL}

    def page(status: int, title: str, body: str):
        try:
            return render_template("error.html", status=status, title=title, body=body), status
        except Exception:  # noqa: BLE001 - fall back to plain text if the app has no error page
            return f"{status} {title}: {body}", status

    @app.errorhandler(404)
    def not_found(_):
        return page(404, "Not found", "That page doesn't exist, or the demo was restarted and forgot it.")

    @app.errorhandler(400)
    def bad_request(_):
        return page(400, "Bad request", "Something in that request wasn't valid. Please go back and try again.")

    @app.errorhandler(413)
    def too_large(_):
        return page(413, "File too large", "CVs must be under 512 KB. Plain text, PDF or Word files work best.")

    @app.errorhandler(500)
    def server_error(_):
        return page(500, "Something went wrong", "The server hit an error. Please try again in a moment.")
