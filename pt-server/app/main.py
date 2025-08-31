from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
import time
from .sources.scholarly import global_search_stream
from .sources import open_alex_api
from .internal.streamable import Streamable
from .internal.base_model import PtBaseModel
from .internal.logger import logger, generate_request_id, set_request_id
from .dependencies import (
    get_duckdb_connection,
    lifespan,
    get_sentence_transformer_model,
)


class StreamMessage(PtBaseModel):
    event: str
    data: Streamable | None


app = FastAPI(lifespan=lifespan)


@app.middleware("http")
async def request_id_middleware(request: Request, call_next):
    """Add request ID to all requests for tracing"""
    request_id = generate_request_id()
    set_request_id(request_id)

    # Add request ID to request state for access in endpoints
    request.state.request_id = request_id

    start_time = time.time()
    logger.info(
        "Request started",
        method=request.method,
        url=str(request.url),
        user_agent=request.headers.get("user-agent"),
    )

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        "Request completed",
        status_code=response.status_code,
        process_time_ms=round(process_time * 1000, 2),
    )

    # Add request ID to response headers for client debugging
    response.headers["X-Request-ID"] = request_id

    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/cache/{scope}/{key}", operation_id="cache_get")
async def cache_get(scope: str, key: str) -> Streamable | None:
    return None


@app.get("/expose-stream-message", operation_id="expose_stream_message")
def expose_stream_message() -> StreamMessage | None:
    return None


@app.get("/search-v2", operation_id="global_query")
async def search_v2(query: str, duckdb_conn=Depends(get_duckdb_connection)):
    return await open_alex_api.search_author(query, duckdb_conn=duckdb_conn)


@app.get("/search", operation_id="global_search")
def search(
    query: str,
    request: Request,
    model: SentenceTransformer = Depends(get_sentence_transformer_model),
) -> EventSourceResponse:
    # Get request ID from middleware
    request_id = getattr(request.state, "request_id", "unknown")

    logger.info("Search started", query=query, query_length=len(query))

    async def publisher():
        try:
            # Ensure request ID context is available in the generator
            set_request_id(request_id)

            result_count = 0
            async for result in global_search_stream(query, model):
                result_count += 1
                logger.debug(
                    "Streaming result",
                    result_type=result.type,
                    result_number=result_count,
                )

                yield {
                    "event": "message",
                    "data": result.model_dump_json(by_alias=True),
                }

            logger.info("Search completed", total_results=result_count)

            yield {
                "event": "finish",
                "data": "",
            }

        except Exception as e:
            logger.error("Search failed", error=str(e), error_type=type(e).__name__)
            yield {
                "event": "error",
                "data": f"Search failed: {str(e)}",
            }

    return EventSourceResponse(publisher())
