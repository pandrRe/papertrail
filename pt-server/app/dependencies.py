from contextlib import asynccontextmanager
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer
import torch
import threading
import atexit
import duckdb
import os
from scholarly import ProxyGenerator, scholarly
from .internal.db import engine, Base
from .internal.logger import logger
from .internal.duckdb import setup_prepared_statements


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


class DuckDBManager:
    """Singleton for managing DuckDB connection lifecycle"""

    _instance = None
    _connection: duckdb.DuckDBPyConnection | None = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def initialize(self, model_manager: ModelManager) -> None:
        """Initialize the DuckDB connection if not already done"""
        if self._initialized:
            return

        try:
            # Get DuckDB path from environment variable
            duckdb_path = os.getenv("DUCKDB_PATH", "db/duckdb.db")
            logger.info(f"Initializing DuckDB connection to: {duckdb_path}")

            # Ensure directory exists
            os.makedirs(os.path.dirname(duckdb_path), exist_ok=True)

            self._connection = duckdb.connect(duckdb_path)

            # Install and load extensions
            logger.info("Installing FTS extension...")
            self._connection.execute("INSTALL fts")
            self._connection.execute("LOAD fts")

            logger.info("Installing VSS extension...")
            self._connection.execute("INSTALL vss")
            self._connection.execute("LOAD vss")

            # Setup embedding function
            model = model_manager.get_model()

            def get_text_embedding_list(text_list: list[str]):
                """Generate embeddings for a list of texts"""
                embeddings = model.encode(text_list, normalize_embeddings=True)
                return embeddings

            self._connection.create_function(
                "get_text_embedding_list",
                get_text_embedding_list,
                return_type="FLOAT[384][]",
            )

            # Setup prepared statements
            setup_prepared_statements(self._connection)

            self._initialized = True
            logger.info(
                "DuckDB connection initialized successfully with FTS and VSS extensions"
            )

            # Register cleanup on exit
            atexit.register(self.cleanup)

        except Exception as e:
            logger.error(f"Failed to initialize DuckDB connection: {e}")
            raise

    def get_connection(self) -> duckdb.DuckDBPyConnection:
        """Get the connection instance, initializing if needed"""
        if not self._initialized:
            self.initialize()

        if self._connection is None:
            raise RuntimeError("DuckDB connection failed to initialize")

        return self._connection

    def cleanup(self) -> None:
        """Clean up DuckDB connection resources"""
        if not self._initialized:
            return

        if self._connection is not None:
            logger.info("Cleaning up DuckDB connection...")
            try:
                self._connection.close()
                self._connection = None
                logger.info("DuckDB connection cleanup completed")
            except Exception as e:
                logger.error(f"Error during DuckDB connection cleanup: {e}")
            finally:
                self._initialized = False


# Global instances
duckdb_manager = DuckDBManager()


def get_sentence_transformer_model() -> SentenceTransformer:
    """Dependency injection function for FastAPI"""
    return model_manager.get_model()


def get_duckdb_connection() -> duckdb.DuckDBPyConnection:
    """Dependency injection function for FastAPI"""
    return duckdb_manager.get_connection()


async def migrator():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize proxies
    pg = ProxyGenerator()
    pg.FreeProxies()
    scholarly.use_proxy(pg)

    # Initialize model, DuckDB, and database
    model_manager.initialize()
    duckdb_manager.initialize(model_manager)
    await migrator()

    yield

    # Cleanup
    model_manager.cleanup()
    duckdb_manager.cleanup()
