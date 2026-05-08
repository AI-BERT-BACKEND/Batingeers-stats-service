class ServiceUnavailableError(Exception):
    def __init__(self, service_name: str):
        self.service_name = service_name
        super().__init__(f"El servicio '{service_name}' no está disponible")


class SubjectNotFoundError(Exception):
    def __init__(self, subject_id: str):
        self.subject_id = subject_id
        super().__init__(f"Materia con id '{subject_id}' no encontrada")


class UnauthorizedError(Exception):
    def __init__(self):
        super().__init__("No autorizado para acceder a este recurso")
