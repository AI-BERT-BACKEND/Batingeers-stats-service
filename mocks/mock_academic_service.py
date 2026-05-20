#!/usr/bin/env python3
"""
Mock server that simulates academic-service responses.
Uses only Python stdlib — no pip install needed.

Run:
    python mocks/mock_academic_service.py

Listens on port 8082.

Endpoints (matching real SubjectController paths):
    GET /api/v1/subjects              header X-Student-Id  -> ApiResponse<List<SubjectResponseDTO>>
    GET /api/v1/subjects/{subjectId}  header X-Student-Id  -> ApiResponse<SubjectResponseDTO>

Response envelope (ApiResponse):
    { "success": true, "data": <payload>, "message": "ok" }

Field names match SubjectResponseDTO / EvaluationCutResponseDTO exactly:
    subjectName, credits, teacherName, semester, schedule,
    overallAverage, evaluationCuts[ { cutName, cutPercentage (0-100), grade } ]
"""

import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer

SUBJECTS = [
    {
        "id": 1,
        "studentId": "test-student-123",
        "subjectName": "Cálculo Diferencial",
        "credits": 4,
        "teacherName": "Prof. Ramírez",
        "semester": "2025-1",
        "schedule": "LUNES 08:00-10:00",
        "overallAverage": 4.0,
        "evaluationCuts": [
            {"id": 1, "cutName": "Corte 1", "cutPercentage": 30, "grade": 4.2},
            {"id": 2, "cutName": "Corte 2", "cutPercentage": 30, "grade": 3.8},
            {"id": 3, "cutName": "Corte Final", "cutPercentage": 40, "grade": None},
        ],
    },
    {
        "id": 2,
        "studentId": "test-student-123",
        "subjectName": "Estructuras de Datos",
        "credits": 3,
        "teacherName": "Prof. Gómez",
        "semester": "2025-1",
        "schedule": "MARTES 10:00-12:00",
        "overallAverage": 3.9,
        "evaluationCuts": [
            {"id": 4, "cutName": "Quiz 1", "cutPercentage": 20, "grade": 4.5},
            {"id": 5, "cutName": "Proyecto", "cutPercentage": 40, "grade": 3.5},
            {"id": 6, "cutName": "Examen Final", "cutPercentage": 40, "grade": None},
        ],
    },
    {
        "id": 3,
        "studentId": "test-student-123",
        "subjectName": "Física I",
        "credits": 3,
        "teacherName": "Prof. Torres",
        "semester": "2025-1",
        "schedule": "MIERCOLES 14:00-16:00",
        "overallAverage": 2.8,
        "evaluationCuts": [
            {"id": 7, "cutName": "Corte 1", "cutPercentage": 30, "grade": 2.8},
            {"id": 8, "cutName": "Corte 2", "cutPercentage": 30, "grade": None},
            {"id": 9, "cutName": "Corte Final", "cutPercentage": 40, "grade": None},
        ],
    },
]

_BY_ID = {str(s["id"]): s for s in SUBJECTS}


def _api_response(data, message: str = "ok") -> dict:
    return {"success": True, "data": data, "message": message}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        student_id = self.headers.get("X-Student-Id")

        # GET /api/v1/subjects — list all subjects for the student
        if path == "/api/v1/subjects":
            if not student_id:
                self._json(
                    400,
                    {
                        "success": False,
                        "error": "Missing X-Student-Id header",
                        "code": 400,
                    },
                )
                return
            result = [s for s in SUBJECTS if s["studentId"] == student_id]
            self._json(200, _api_response(result))
            return

        # GET /api/v1/subjects/{subjectId}
        m = re.match(r"^/api/v1/subjects/(\d+)$", path)
        if m:
            if not student_id:
                self._json(
                    400,
                    {
                        "success": False,
                        "error": "Missing X-Student-Id header",
                        "code": 400,
                    },
                )
                return
            subject = _BY_ID.get(m.group(1))
            if subject and subject["studentId"] == student_id:
                self._json(200, _api_response(subject))
            else:
                self._json(
                    403,
                    {
                        "success": False,
                        "error": "Subject not found or does not belong to the student",
                        "code": 403,
                    },
                )
            return

        self._json(404, {"success": False, "error": "Not found", "code": 404})

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
