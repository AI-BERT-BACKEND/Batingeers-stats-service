#!/usr/bin/env python3
"""
Mock server that simulates task-service responses.
Uses only Python stdlib — no pip install needed.

Run:
    python mocks/mock_task_service.py

Listens on port 8083.

Endpoints (matching real TaskController paths):
    GET /api/tasks/student/{studentId}         header X-User-Id  -> List<TaskResponse>
    GET /api/tasks?view=calendar&subjectId={}  header X-User-Id  -> List<TaskResponse>

Field names match TaskResponse exactly:
    id, studentId, subjectId (camelCase), title, taskType, priority,
    status (TODO | IN_PROGRESS | PAUSED | COMPLETED),
    deadline (ISO datetime), completedAt (ISO datetime or null)
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

STUDENT_ID = "test-student-123"

# subjectId values match academic-service integer IDs serialised as strings
TASKS = [
    # ── Cálculo Diferencial (id=1) ────────────────────────────────────────────
    {
        "id": "task-1",
        "studentId": STUDENT_ID,
        "subjectId": "1",
        "title": "Taller Límites",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-03-01T23:59:00",
        "completedAt": "2026-03-01T20:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 90,
    },
    {
        "id": "task-2",
        "studentId": STUDENT_ID,
        "subjectId": "1",
        "title": "Taller Derivadas",
        "taskType": "TAREA",
        "priority": "HIGH",
        "status": "COMPLETED",
        "deadline": "2026-03-08T23:59:00",
        "completedAt": "2026-03-10T10:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 120,
    },
    {
        "id": "task-3",
        "studentId": STUDENT_ID,
        "subjectId": "1",
        "title": "Examen Corte 2",
        "taskType": "EXAMEN",
        "priority": "HIGH",
        "status": "COMPLETED",
        "deadline": "2026-04-15T23:59:00",
        "completedAt": "2026-04-15T18:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 60,
    },
    {
        "id": "task-4",
        "studentId": STUDENT_ID,
        "subjectId": "1",
        "title": "Proyecto Integrales",
        "taskType": "PROYECTO",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-04-22T23:59:00",
        "completedAt": "2026-04-20T16:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 180,
    },
    {
        "id": "task-5",
        "studentId": STUDENT_ID,
        "subjectId": "1",
        "title": "Preparación Corte Final",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "TODO",
        "deadline": "2026-05-25T23:59:00",
        "completedAt": None,
        "scheduledDate": None,
        "estimatedDurationMinutes": 150,
    },
    # ── Estructuras de Datos (id=2) ───────────────────────────────────────────
    {
        "id": "task-6",
        "studentId": STUDENT_ID,
        "subjectId": "2",
        "title": "Quiz Arreglos",
        "taskType": "QUIZ",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-02-20T23:59:00",
        "completedAt": "2026-02-20T15:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 45,
    },
    {
        "id": "task-7",
        "studentId": STUDENT_ID,
        "subjectId": "2",
        "title": "Práctica Listas",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-03-05T23:59:00",
        "completedAt": "2026-03-01T11:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 90,
    },
    {
        "id": "task-8",
        "studentId": STUDENT_ID,
        "subjectId": "2",
        "title": "Proyecto Árboles",
        "taskType": "PROYECTO",
        "priority": "HIGH",
        "status": "COMPLETED",
        "deadline": "2026-03-18T23:59:00",
        "completedAt": "2026-03-20T09:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 240,
    },
    {
        "id": "task-9",
        "studentId": STUDENT_ID,
        "subjectId": "2",
        "title": "Taller Grafos",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-04-12T23:59:00",
        "completedAt": "2026-04-10T14:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 120,
    },
    {
        "id": "task-10",
        "studentId": STUDENT_ID,
        "subjectId": "2",
        "title": "Examen Final Estructuras",
        "taskType": "EXAMEN",
        "priority": "HIGH",
        "status": "IN_PROGRESS",
        "deadline": "2026-05-30T23:59:00",
        "completedAt": None,
        "scheduledDate": "2026-05-28T09:00:00",
        "estimatedDurationMinutes": 60,
    },
    # ── Física I (id=3) ───────────────────────────────────────────────────────
    {
        "id": "task-11",
        "studentId": STUDENT_ID,
        "subjectId": "3",
        "title": "Laboratorio Cinemática",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "COMPLETED",
        "deadline": "2026-03-01T23:59:00",
        "completedAt": "2026-03-05T10:00:00",
        "scheduledDate": None,
        "estimatedDurationMinutes": 90,
    },
    {
        "id": "task-12",
        "studentId": STUDENT_ID,
        "subjectId": "3",
        "title": "Informe Dinámica",
        "taskType": "TAREA",
        "priority": "HIGH",
        "status": "PAUSED",
        "deadline": "2026-04-10T23:59:00",
        "completedAt": None,
        "scheduledDate": None,
        "estimatedDurationMinutes": 120,
    },
    {
        "id": "task-13",
        "studentId": STUDENT_ID,
        "subjectId": "3",
        "title": "Práctica Termodinámica",
        "taskType": "TAREA",
        "priority": "MEDIUM",
        "status": "TODO",
        "deadline": "2026-06-01T23:59:00",
        "completedAt": None,
        "scheduledDate": None,
        "estimatedDurationMinutes": 150,
    },
]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        user_id = self.headers.get("X-User-Id")

        # GET /api/tasks/student/{studentId}
        m = re.match(r"^/api/tasks/student/(.+)$", parsed.path)
        if m:
            path_student_id = m.group(1)
            if not user_id:
                self._json(400, {"message": "Missing X-User-Id header"})
                return
            if user_id != path_student_id:
                self._json(403, {"message": "No tienes permiso para ver las tareas de otro estudiante"})
                return
            result = [t for t in TASKS if t["studentId"] == path_student_id]
            self._json(200, result)
            return

        # GET /api/tasks?view=calendar&subjectId={subjectId}
        if parsed.path == "/api/tasks":
            if not user_id:
                self._json(400, {"message": "Missing X-User-Id header"})
                return
            view = params.get("view", [None])[0]
            subject_id = params.get("subjectId", [None])[0]
            student_tasks = [t for t in TASKS if t["studentId"] == user_id]

            if view == "calendar" and subject_id:
                result = [t for t in student_tasks if t.get("subjectId") == subject_id]
            else:
                result = student_tasks
            self._json(200, result)
            return

        self._json(404, {"message": "Not found"})

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
