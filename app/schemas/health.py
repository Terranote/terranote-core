from pydantic import BaseModel


class NoteMetrics(BaseModel):
    attempts: int
    successes: int
    http_errors: int
    network_errors: int
    invalid_responses: int
    retries: int


class HealthStatus(BaseModel):
    status: str
    metrics: NoteMetrics


