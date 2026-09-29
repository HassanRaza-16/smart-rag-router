from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
    )


class QueryResponse(BaseModel):
    answer: str
    model: str
    cache_hit: bool
    similarity: float | None = None
    latency_ms: float
    estimated_cost: float


class HealthResponse(BaseModel):
    status: str