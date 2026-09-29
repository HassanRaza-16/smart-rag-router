# SmartRAG Router

A production-style RAG application that combines **semantic response caching, incremental document embeddings, RAG retrieval, cost-aware model routing, retry/fallback handling, and observability**.

The project is built with **FastAPI, Gemini, SQLite, NumPy, and Streamlit**.

---

## Features

* 🔎 Semantic response caching
* 🧠 Gemini embeddings
* 📚 Retrieval-Augmented Generation (RAG)
* ⚡ Incremental document embedding
* 🔀 Cost-aware model routing
* 🔄 Retry and fallback model handling
* 📊 Request-level observability
* 💾 SQLite persistence
* 📈 Streamlit monitoring dashboard
* 🧪 Automated tests with pytest
* 🔐 Environment-based API key configuration

---

## Architecture

```text
                         User Query
                              │
                              ▼
                     Query Embedding
                              │
                              ▼
                    Semantic Cache Search
                       │              │
                    HIT              MISS
                     │                │
                     ▼                ▼
               Cached Answer      RAG Retrieval
                                      │
                                      ▼
                              Model Router
                              │         │
                           Small       Large
                              │         │
                              └────┬────┘
                                   ▼
                              Gemini LLM
                                   │
                                   ▼
                              Save Cache
                                   │
                                   ▼
                                Metrics
                                   │
                                   ▼
                              API Response
```

---

## Incremental Document Embedding

Documents are stored in:

```text
data/documents.txt
```

The application calculates a SHA-256 hash for each document chunk.

```text
New document
     │
     ▼
Create embedding
     │
     ▼
Store in SQLite
```

For an existing document:

```text
Document changed?
      │
   ┌──┴──┐
  No     Yes
  │       │
Reuse   Re-embed
```

Unchanged documents reuse their existing embeddings, preventing unnecessary embedding API calls.

Document embeddings are stored in the SQLite database.

---

## Semantic Cache

The semantic cache stores:

* Original question
* Query embedding
* Generated answer
* Model used

When a new query arrives, its embedding is compared with cached query embeddings.

If the similarity exceeds the configured threshold, the cached answer is returned.

```text
New Query
   │
   ▼
Embedding
   │
   ▼
Similarity Search
   │
   ├── Similar → Cached Answer
   │
   └── Not Similar → RAG + LLM
```

---

## Model Routing

The router analyzes the query and selects a model based on its complexity.

Simple questions can use the smaller model.

More complex questions containing concepts such as:

* compare
* analyze
* architecture
* tradeoffs
* implementation
* evaluate

can be routed to the larger model.

This demonstrates the basic concept of **cost-aware LLM routing**.

---

## Retry and Fallback

If the selected Gemini model fails, the application retries the request.

```text
Selected Model
      │
      ▼
   Request
      │
   Failure?
   ┌──┴──┐
  No    Yes
  │      │
Answer  Retry
          │
       Failure
          │
          ▼
    Fallback Model
```

---

## Observability

Request metrics are stored in SQLite.

Tracked metrics include:

* Request timestamp
* Query
* Selected/actual model
* Cache hit
* Latency
* Estimated cost

The Streamlit dashboard displays:

* Total requests
* Cache hit rate
* Average latency
* P95 latency
* Model usage
* Request latency
* Estimated cost
* Request logs

---

## Project Structure

```text
smart-rag-router/
│
├── app/
│   ├── core/
│   │   └── config.py
│   │
│   ├── models/
│   │   └── schemas.py
│   │
│   ├── services/
│   │   ├── cache_service.py
│   │   ├── embedding_service.py
│   │   ├── gemini_service.py
│   │   ├── metrics_service.py
│   │   ├── rag_service.py
│   │   └── routing_service.py
│   │
│   └── main.py
│
├── data/
│   └── documents.txt
│
├── tests/
│   ├── test_cache.py
│   └── test_router.py
│
├── dashboard.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

## Installation

Clone the repository:

```bash
git clone YOUR_REPOSITORY_URL
cd smart-rag-router
```

Create a virtual environment:

### Windows

```powershell
python -m venv venv
venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
GEMINI_API_KEY=your_gemini_api_key

SMALL_MODEL=your_small_model
LARGE_MODEL=your_large_model
FALLBACK_MODEL=your_fallback_model

EMBEDDING_MODEL=your_embedding_model

CACHE_THRESHOLD=0.80
```

Never commit your real `.env` file or API key.

---

## Run the API

```powershell
uvicorn app.main:app --reload
```

API:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Example Request

```json
{
  "query": "What is RAG?"
}
```

Example response:

```json
{
  "answer": "RAG combines information retrieval with language generation...",
  "model": "your_small_model",
  "cache_hit": false,
  "similarity": null,
  "latency_ms": 2500.0,
  "estimated_cost": 0.001
}
```

A repeated or semantically similar question can return:

```json
{
  "answer": "RAG combines information retrieval with language generation...",
  "model": "your_small_model",
  "cache_hit": true,
  "similarity": 0.96,
  "latency_ms": 900.0,
  "estimated_cost": 0.0
}
```

---

## Run Dashboard

In another terminal:

```powershell
streamlit run dashboard.py
```

The dashboard provides a visual overview of request performance and model usage.

---

## Run Tests

```powershell
pytest -q
```

---

## Technology Stack

| Technology | Purpose                       |
| ---------- | ----------------------------- |
| Python     | Application development       |
| FastAPI    | REST API                      |
| Gemini     | Embeddings and LLM generation |
| NumPy      | Vector similarity             |
| SQLite     | Cache, embeddings and metrics |
| Streamlit  | Monitoring dashboard          |
| Pydantic   | Request/response validation   |
| Pytest     | Testing                       |

---

## Key Engineering Concepts Demonstrated

This project demonstrates practical implementation of:

* RAG
* Semantic caching
* Embedding generation
* Cosine similarity
* Incremental embedding
* Content hashing
* LLM model routing
* Retry and fallback
* API development
* SQLite persistence
* Observability
* Latency tracking
* Cost estimation
* Automated testing

---

## Future Improvements

Possible future improvements include:

* Vector database integration
* Better document ingestion pipeline
* Background embedding jobs
* More advanced model routing
* Token-level cost calculation
* Authentication and rate limiting
* Distributed caching
* Production tracing
* RAG evaluation
* Automated CI/CD evaluation

---

## License

This project is intended as an educational and portfolio project.
