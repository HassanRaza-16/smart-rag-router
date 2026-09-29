import time

from fastapi import FastAPI

from app.core.config import get_settings
from app.models.schemas import (
    HealthResponse,
    QueryRequest,
    QueryResponse,
)
from app.services.cache_service import CacheService
from app.services.embedding_service import EmbeddingService
from app.services.gemini_service import GeminiService
from app.services.metrics_service import MetricsService
from app.services.rag_service import RAGService
from app.services.routing_service import RoutingService


settings = get_settings()


# -----------------------------------------
# Services
# -----------------------------------------

gemini_service = GeminiService(
    settings
)

embedding_service = EmbeddingService(
    settings,
    gemini_service,
)

cache_service = CacheService(
    settings,
    embedding_service,
)

routing_service = RoutingService(
    settings
)

rag_service = RAGService(
    settings,
    embedding_service,
)

metrics_service = MetricsService(
    settings
)


# -----------------------------------------
# FastAPI
# -----------------------------------------

app = FastAPI(
    title="SmartRAG Router",
    version="1.0.0",
)


# -----------------------------------------
# Health
# -----------------------------------------

@app.get(
    "/health",
    response_model=HealthResponse,
)
def health():

    return {
        "status": "healthy"
    }


# -----------------------------------------
# Query
# -----------------------------------------

@app.post(
    "/query",
    response_model=QueryResponse,
)
def query(
    request: QueryRequest,
):

    start = time.perf_counter()

    query_text = request.query.strip()

    # -------------------------------------
    # 1. Embed query ONCE
    # -------------------------------------

    embedding_start = time.perf_counter()

    query_embedding = (
        embedding_service.embed(
            query_text
        )
    )

    embedding_latency = (
        time.perf_counter() - embedding_start
    ) * 1000

    print(
        f"Embedding latency: "
        f"{embedding_latency:.2f} ms"
    )

    # -------------------------------------
    # 2. Semantic cache
    # -------------------------------------

    cached = cache_service.search(
        query_embedding
    )

    if cached:

        latency = (
            time.perf_counter() - start
        ) * 1000

        metrics_service.record(
            query=query_text,
            model=cached["model"],
            cache_hit=True,
            latency_ms=latency,
            estimated_cost=0.0,
        )

        return QueryResponse(
            answer=cached["answer"],
            model=cached["model"],
            cache_hit=True,
            similarity=round(
                cached["similarity"],
                4,
            ),
            latency_ms=round(
                latency,
                2,
            ),
            estimated_cost=0.0,
        )

    # -------------------------------------
    # 3. RAG retrieval
    # -------------------------------------

    documents = rag_service.retrieve(
        query_embedding=query_embedding,
        top_k=3,
    )

    context = "\n\n".join(
        documents
    )

    # -------------------------------------
    # 4. Model routing
    # -------------------------------------

    selected_model = (
        routing_service.select_model(
            query_text
        )
    )

    # -------------------------------------
    # 5. Prompt
    # -------------------------------------

    prompt = f"""
You are a RAG assistant.

Answer the user's question using ONLY
the provided context.

If the context does not contain enough
information, clearly say that the
information is not available in the
provided context.

Context:
{context}

Question:
{query_text}

Give a concise and accurate answer.
"""

    # -------------------------------------
    # 6. Gemini + retry + fallback
    # -------------------------------------

    generation_start = time.perf_counter()

    try:

        answer, actual_model = (
            gemini_service.generate(
                prompt=prompt,
                model=selected_model,
            )
        )

    finally:

        generation_latency = (
            time.perf_counter() - generation_start
        ) * 1000

        print(
            f"Generation latency: "
            f"{generation_latency:.2f} ms"
        )

    # -------------------------------------
    # 7. Save cache
    # -------------------------------------

    cache_service.save(
        query=query_text,
        query_embedding=query_embedding,
        answer=answer,
        model=actual_model,
    )

    # -------------------------------------
    # 8. Metrics
    # -------------------------------------

    latency = (
        time.perf_counter() - start
    ) * 1000

    if actual_model == settings.small_model:

        estimated_cost = 0.001

    elif actual_model == settings.large_model:

        estimated_cost = 0.005

    else:

        estimated_cost = 0.003

    metrics_service.record(
        query=query_text,
        model=actual_model,
        cache_hit=False,
        latency_ms=latency,
        estimated_cost=estimated_cost,
    )

    # -------------------------------------
    # 9. Response
    # -------------------------------------

    return QueryResponse(
        answer=answer,
        model=actual_model,
        cache_hit=False,
        similarity=None,
        latency_ms=round(
            latency,
            2,
        ),
        estimated_cost=estimated_cost,
    )