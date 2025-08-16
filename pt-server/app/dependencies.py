from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import torch
import threading
import atexit
from scholarly import ProxyGenerator, scholarly
from .internal.db import engine, Base
from .internal.logger import logger


class ModelManager:
    """Thread-safe singleton for managing SentenceTransformer lifecycle"""

    _instance = None
    _lock = threading.Lock()
    _model: SentenceTransformer | None = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self) -> None:
        """Initialize the model if not already done"""
        if self._initialized:
            return

        with self._lock:
            if self._initialized:
                return

            try:
                # Configure torch multiprocessing for GPU
                if not torch.multiprocessing.get_start_method(allow_none=True):
                    torch.multiprocessing.set_start_method("spawn", force=True)

                # Set sharing strategy to avoid semaphore issues
                torch.multiprocessing.set_sharing_strategy("file_system")

                logger.info("Loading SentenceTransformer model...")
                device = "cuda" if torch.cuda.is_available() else "cpu"
                logger.info(f"Using device: {device}")

                self._model = SentenceTransformer("all-MiniLM-L6-v2")
                # Move to GPU after initialization to avoid init issues
                if torch.cuda.is_available():
                    self._model = self._model.to(device)

                self._initialized = True
                logger.info("SentenceTransformer model loaded successfully")

                # Register cleanup on exit
                atexit.register(self.cleanup)

            except Exception as e:
                logger.error(f"Failed to initialize model: {e}")
                raise

    def get_model(self) -> SentenceTransformer:
        """Get the model instance, initializing if needed"""
        if not self._initialized:
            self.initialize()

        if self._model is None:
            raise RuntimeError("Model failed to initialize")

        return self._model

    def cleanup(self) -> None:
        """Clean up model resources"""
        if not self._initialized:
            return

        with self._lock:
            if self._model is not None:
                logger.info("Cleaning up SentenceTransformer model...")
                try:
                    # Clear model from memory
                    del self._model
                    self._model = None

                    # Clear GPU cache if available
                    if torch.cuda.is_available():
                        torch.cuda.empty_cache()
                        torch.cuda.synchronize()

                    # Clear CPU cache
                    if hasattr(torch, "clear_autocast_cache"):
                        torch.clear_autocast_cache()

                    logger.info("Model cleanup completed")
                except Exception as e:
                    logger.error(f"Error during model cleanup: {e}")
                finally:
                    self._initialized = False


# Global instance
model_manager = ModelManager()


def get_sentence_transformer_model() -> SentenceTransformer:
    """Dependency injection function for FastAPI"""
    return model_manager.get_model()


async def migrator():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize proxies
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)

    # Initialize model and database
    model_manager.initialize()
    await migrator()

    yield

    # Cleanup
    model_manager.cleanup()
