from pydantic import BaseModel


class NoteMetrics(BaseModel):
    attempts: int
    successes: int
    http_errors: int
    network_errors: int
    invalid_responses: int
    retries: int


class DependencyHealth(BaseModel):
    status: str
    message: str | None = None


class HealthStatus(BaseModel):
    status: str
    uptime: int
    version: str
    environment: str
    dependencies: dict[str, DependencyHealth]
    metrics: NoteMetrics | None = None
