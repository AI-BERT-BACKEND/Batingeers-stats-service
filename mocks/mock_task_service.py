#!/usr/bin/env python3
"""
Mock server that simulates task-service responses.
Uses only Python stdlib — no pip install needed.

Run:
    python mocks/mock_task_service.py

Listens on port 8083.
Endpoints:
    GET /api/tasks/user/{userId}                   -> all tasks
    GET /api/tasks/user/{userId}?subjectId={id}    -> tasks filtered by subject
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# Tasks contain both subject_id (for dashboard filtering) and
# completedAt/dueDate (for gamification points).
TASKS = [
    # ── Cálculo Diferencial ───────────────────────────────────────────────────
    {
        "id": "task-1",
        "subject_id": "sub-calculo",
        "status": "COMPLETED",
        "completedAt": "2026-03-01",
        "dueDate": "2026-03-01",
    },
    {
        "id": "task-2",
        "subject_id": "sub-calculo",
        "status": "COMPLETED",
        "completedAt": "2026-03-10",
        "dueDate": "2026-03-08",  # late → +3 pts
    },
    {
        "id": "task-3",
        "subject_id": "sub-calculo",
        "status": "COMPLETED",
        "completedAt": "2026-04-15",
        "dueDate": "2026-04-15",
    },
    {
        "id": "task-4",
        "subject_id": "sub-calculo",
        "status": "COMPLETED",
        "completedAt": "2026-04-20",
        "dueDate": "2026-04-22",
    },
    {
        "id": "task-5",
        "subject_id": "sub-calculo",
        "status": "PENDING",
        "completedAt": None,
        "dueDate": "2026-05-25",
    },
    # ── Estructuras de Datos ──────────────────────────────────────────────────
    {
        "id": "task-6",
        "subject_id": "sub-estructuras",
        "status": "COMPLETED",
        "completedAt": "2026-02-20",
        "dueDate": "2026-02-20",
    },
    {
        "id": "task-7",
        "subject_id": "sub-estructuras",
        "status": "COMPLETED",
        "completedAt": "2026-03-01",
        "dueDate": "2026-03-05",
    },
    {
        "id": "task-8",
        "subject_id": "sub-estructuras",
        "status": "COMPLETED",
        "completedAt": "2026-03-20",
        "dueDate": "2026-03-18",  # late → +3 pts
    },
    {
        "id": "task-9",
        "subject_id": "sub-estructuras",
        "status": "COMPLETED",
        "completedAt": "2026-04-10",
        "dueDate": "2026-04-12",
    },
    {
        "id": "task-10",
        "subject_id": "sub-estructuras",
        "status": "IN_PROGRESS",
        "completedAt": None,
        "dueDate": "2026-05-30",
    },
    # ── Física I ──────────────────────────────────────────────────────────────
    {
        "id": "task-11",
        "subject_id": "sub-fisica",
        "status": "COMPLETED",
        "completedAt": "2026-03-05",
        "dueDate": "2026-03-01",  # late → +3 pts
    },
    {
        "id": "task-12",
        "subject_id": "sub-fisica",
        "status": "OVERDUE",
        "completedAt": None,
        "dueDate": "2026-04-10",
    },
    {
        "id": "task-13",
        "subject_id": "sub-fisica",
        "status": "PENDING",
        "completedAt": None,
        "dueDate": "2026-06-01",
    },
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        if re.match(r"^/api/tasks/user/.+$", parsed.path):
            subject_id = params.get("subjectId", [None])[0]
            result = (
                [t for t in TASKS if t.get("subject_id") == subject_id]
                if subject_id
                else TASKS
            )
            self._json(200, result)
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
        print(f"[task-mock] {fmt % args}")


if __name__ == "__main__":
    port = 8083
    server = HTTPServer(("0.0.0.0", port), Handler)
    print(f"Mock task-service -> http://localhost:{port}")
    print(
        f"Tasks: {len(TASKS)} total "
        f"({sum(1 for t in TASKS if t['status'] == 'COMPLETED')} completed)"
    )
    server.serve_forever()
