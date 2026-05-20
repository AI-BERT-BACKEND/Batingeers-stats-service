class ServiceUnavailableError(Exception):
    def __init__(self, service_name: str):
        self.service_name = service_name
        super().__init__(f"Service '{service_name}' is currently unavailable")


class SubjectNotFoundError(Exception):
    def __init__(self, subject_id: str):
        self.subject_id = subject_id
        super().__init__(f"Subject with id '{subject_id}' was not found")


class UnauthorizedError(Exception):
    def __init__(self):
        super().__init__("Not authorized to access this resource")
