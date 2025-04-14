from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import torch
from .internal.db import engine, Base

model: SentenceTransformer | None = None


def get_sentence_transformer_model() -> SentenceTransformer:
    if model is None:
        raise RuntimeError("Model not initialized.")
    return model


async def migrator():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global model
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("Model started.")

    await migrator()

    yield
    print("Model cleanup.")
    del model
    torch.cuda.empty_cache()
    print("Model cleaned.")
