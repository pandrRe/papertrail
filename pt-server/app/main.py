from sentence_transformers import SentenceTransformer
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from .sources.scholarly import global_search_stream, Streamable
from .internal.base_model import PtBaseModel
from .dependencies import lifespan, get_sentence_transformer_model


class StreamMessage(PtBaseModel):
    event: str
    data: Streamable | None


app = FastAPI(lifespan=lifespan)
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


@app.get("/search", operation_id="global_search")
def search(
    query: str, model: SentenceTransformer = Depends(get_sentence_transformer_model)
) -> EventSourceResponse:
    async def publisher():
        async for result in global_search_stream(query, model):
            # if result is None:
            #     yield {
            #         "event": "finish",
            #         "data": "",
            #     }
            #     return
            yield {
                "event": "message",
                "data": result.model_dump_json(by_alias=True),
            }
        yield {
            "event": "finish",
            "data": "",
        }

    # logger.debug("BEING CALLED")
    return EventSourceResponse(publisher())
