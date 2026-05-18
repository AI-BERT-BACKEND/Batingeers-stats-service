#!/usr/bin/env python3
"""
Mock server that simulates academic-service responses.
Uses only Python stdlib — no pip install needed.

Run:
    python mocks/mock_academic_service.py

Listens on port 8082.
Endpoints:
    GET /api/academic/subjects/user/{userId}  -> list of all subjects
    GET /api/academic/subjects/{subjectId}    -> single subject or 404
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

SUBJECTS = [
    {
        "id": "sub-calculo",
        "name": "Cálculo Diferencial",
        "code": "MAT201",
        "credits": 4,
        "evaluations": [
            {
                "id": "eval-1",
                "name": "Corte 1",
                "weight": 0.30,
                "grade": 4.2,
                "date": "2026-03-01",
            },
            {
                "id": "eval-2",
                "name": "Corte 2",
                "weight": 0.30,
                "grade": 3.8,
                "date": "2026-04-15",
            },
            {
                "id": "eval-3",
                "name": "Corte Final",
                "weight": 0.40,
                "grade": None,
                "date": None,
            },
        ],
    },
    {
        "id": "sub-estructuras",
        "name": "Estructuras de Datos",
        "code": "SIS301",
        "credits": 3,
        "evaluations": [
            {
                "id": "eval-4",
                "name": "Quiz 1",
                "weight": 0.20,
                "grade": 4.5,
                "date": "2026-02-20",
            },
            {
                "id": "eval-5",
                "name": "Proyecto",
                "weight": 0.40,
                "grade": 3.5,
                "date": "2026-03-20",
            },
            {
                "id": "eval-6",
                "name": "Examen Final",
                "weight": 0.40,
                "grade": None,
                "date": None,
            },
        ],
    },
    {
        "id": "sub-fisica",
        "name": "Física I",
        "code": "FIS101",
        "credits": 3,
        "evaluations": [
            {
                "id": "eval-7",
                "name": "Corte 1",
                "weight": 0.30,
                "grade": 2.8,
                "date": "2026-03-05",
            },
            {
                "id": "eval-8",
                "name": "Corte 2",
                "weight": 0.30,
                "grade": None,
                "date": None,
            },
            {
                "id": "eval-9",
                "name": "Corte Final",
                "weight": 0.40,
                "grade": None,
                "date": None,
            },
        ],
    },
]

_BY_ID = {s["id"]: s for s in SUBJECTS}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]

        if re.match(r"^/api/academic/subjects/user/.+$", path):
            self._json(200, SUBJECTS)
            return

        m = re.match(r"^/api/academic/subjects/(.+)$", path)
        if m:
            subject = _BY_ID.get(m.group(1))
            if subject:
                self._json(200, subject)
            else:
                self._json(404, {"detail": "Subject not found"})
            return

        self._json(404, {"detail": "Not found"})

    def _json(self, status: int, data):
        body = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(f"[academic-mock] {fmt % args}")


if __name__ == "__main__":
    port = 8082
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Mock academic-service -> http://localhost:{port}")
    print(f"Subjects: {list(_BY_ID.keys())}")
    server.serve_forever()
