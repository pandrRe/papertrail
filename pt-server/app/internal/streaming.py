"""
Dynamic Streaming Iterator System

This module provides a framework for creating streaming iterators backed by a pool of async tasks.
Each task can produce streamable content and spawn additional tasks, creating a dynamic workflow.

Design Note: While Python has built-in task pool primitives (asyncio.TaskGroup, asyncio.gather(),
asyncio.as_completed(), asyncio.wait()), this custom implementation is needed because:

1. Built-ins work with fixed task sets, we need dynamic task addition during execution
2. We need individual timeout management per task with graceful degradation
3. Tasks must be processed immediately as they complete (streaming), not batch-collected
4. Each task result can spawn additional tasks, creating a self-expanding workflow
5. Resource limiting with pending queues and statistics tracking is required

The closest built-in is asyncio.as_completed(), but it doesn't support adding tasks
to the iteration set after creation, which is core to our dynamic workflow needs.
"""

import asyncio
import time
import weakref
from typing import AsyncGenerator, Awaitable, Callable, Generic, TypeVar, Union
from collections.abc import Coroutine
from .logger import logger
from .base_model import PtBaseModel


# Type variables for generic task handling
T = TypeVar("T")
TaskInput = TypeVar("TaskInput")


class TaskResult(PtBaseModel, Generic[T]):
    """Result returned by each task execution."""

    publishable: T | None = None
    next: list["StreamingTask"] = []


class StreamingTask(PtBaseModel):
    """Represents a task to be executed in the streaming pool."""

    id: str
    coroutine_factory: Callable[[], Coroutine]
    timeout: float = 30.0
    created_at: float = 0.0

    def __init__(self, **data):
        if "created_at" not in data:
            data["created_at"] = time.time()
        super().__init__(**data)

    def create_coroutine(self) -> Coroutine:
        """Create a fresh coroutine from the factory."""
        return self.coroutine_factory()

    model_config = {"arbitrary_types_allowed": True}


class StreamingTaskPool:
    """
    Manages a pool of async tasks with dynamic task addition and timeout handling.

    Note: While Python has built-in task pool primitives like asyncio.TaskGroup,
    asyncio.gather(), and asyncio.as_completed(), this custom implementation provides:

    - Dynamic task addition during execution (tasks can spawn more tasks)
    - Individual timeout management per task
    - Immediate result processing without waiting for all tasks
    - Resource limiting with pending task queues
    - Statistics tracking and pool management

    Built-in alternatives like asyncio.as_completed() work with fixed task sets,
    while we need a dynamic, self-expanding pool.
    """

    def __init__(self, max_concurrent_tasks: int = 10):
        self.max_concurrent_tasks = max_concurrent_tasks
        self.active_tasks: dict[str, asyncio.Task] = {}
        self.pending_tasks: list[StreamingTask] = []
        self.completed_count = 0
        self.failed_count = 0
        self.timeout_count = 0

    async def add_task(self, streaming_task: StreamingTask) -> None:
        """Add a new task to the pool."""
        if len(self.active_tasks) < self.max_concurrent_tasks:
            await self._start_task(streaming_task)
        else:
            self.pending_tasks.append(streaming_task)

    async def add_tasks(self, streaming_tasks: list[StreamingTask]) -> None:
        """Add multiple tasks to the pool."""
        for task in streaming_tasks:
            await self.add_task(task)

    async def _start_task(self, streaming_task: StreamingTask) -> None:
        """Start executing a streaming task."""
        if streaming_task.id in self.active_tasks:
            return

        try:
            coroutine = streaming_task.create_coroutine()
            task = asyncio.create_task(
                asyncio.wait_for(coroutine, timeout=streaming_task.timeout)
            )
            task.set_name(f"streaming_task_{streaming_task.id}")
            self.active_tasks[streaming_task.id] = task

            logger.debug(f"Started task {streaming_task.id}")

        except Exception as e:
            logger.error(f"Failed to start task {streaming_task.id}: {e}")
            self.failed_count += 1

    async def _start_pending_tasks(self) -> None:
        """Start pending tasks up to the concurrent limit."""
        while len(self.active_tasks) < self.max_concurrent_tasks and self.pending_tasks:
            task = self.pending_tasks.pop(0)
            await self._start_task(task)

    async def wait_for_next_completion(self) -> tuple[str, TaskResult | None]:
        """
        Wait for the next task to complete and return its result.

        Returns:
            Tuple of (task_id, result) where result is None if task failed/timed out
        """
        if not self.active_tasks:
            raise StopIteration("No active tasks")

        # Wait for any task to complete
        done, _ = await asyncio.wait(
            self.active_tasks.values(), return_when=asyncio.FIRST_COMPLETED
        )

        completed_task = next(iter(done))
        task_id = None

        # Find the task ID
        for tid, task in self.active_tasks.items():
            if task is completed_task:
                task_id = tid
                break

        if task_id is None:
            raise RuntimeError("Could not find completed task ID")

        # Remove from active tasks
        del self.active_tasks[task_id]

        # Get result
        result = None
        try:
            task_result = await completed_task
            result = task_result
            self.completed_count += 1
            logger.debug(f"Task {task_id} completed successfully")

        except asyncio.TimeoutError:
            logger.warning(f"Task {task_id} timed out")
            self.timeout_count += 1

        except Exception as e:
            logger.error(f"Task {task_id} failed: {e}")
            self.failed_count += 1

        # Start pending tasks
        await self._start_pending_tasks()

        return task_id, result

    def has_active_tasks(self) -> bool:
        """Check if there are any active or pending tasks."""
        return bool(self.active_tasks or self.pending_tasks)

    def get_stats(self) -> dict:
        """Get statistics about task execution."""
        return {
            "active_tasks": len(self.active_tasks),
            "pending_tasks": len(self.pending_tasks),
            "completed": self.completed_count,
            "failed": self.failed_count,
            "timeouts": self.timeout_count,
            "total_processed": self.completed_count
            + self.failed_count
            + self.timeout_count,
        }

    async def shutdown(self) -> None:
        """Cancel all active tasks and clear the pool."""
        # Cancel all active tasks and close their coroutines
        for task in self.active_tasks.values():
            if not task.done():
                task.cancel()

        # Wait for all tasks to finish (including cancellation)
        if self.active_tasks:
            # Use return_exceptions=True to suppress cancellation exceptions
            # and avoid warnings about unawaited coroutines
            results = await asyncio.gather(
                *self.active_tasks.values(), return_exceptions=True
            )

            # Log any unexpected exceptions (not cancellation)
            for i, result in enumerate(results):
                if isinstance(result, Exception) and not isinstance(
                    result, asyncio.CancelledError
                ):
                    logger.warning(
                        f"Task finished with exception during shutdown: {result}"
                    )

        # Clear all tasks and pending work
        self.active_tasks.clear()
        self.pending_tasks.clear()


class DynamicStreamingIterator(Generic[T]):
    """
    An async iterator that manages a dynamic pool of tasks, yielding results as they complete.

    Each task can produce publishable content and spawn additional tasks, creating a
    self-expanding workflow that continues until no more tasks are available.
    """

    def __init__(
        self,
        initial_tasks: list[StreamingTask],
        max_concurrent_tasks: int = 10,
        max_total_tasks: int = 1000,
    ):
        self.task_pool = StreamingTaskPool(max_concurrent_tasks)
        self.max_total_tasks = max_total_tasks
        self.total_tasks_created = 0
        self.initial_tasks = initial_tasks

    async def __aiter__(self) -> AsyncGenerator[T, None]:
        """Async iterator that yields streamable content from completed tasks."""
        try:
            # Add initial tasks
            await self.task_pool.add_tasks(self.initial_tasks)
            self.total_tasks_created += len(self.initial_tasks)

            logger.info(
                f"Started streaming iterator with {len(self.initial_tasks)} initial tasks"
            )

            # Process tasks until pool is empty
            while self.task_pool.has_active_tasks():
                try:
                    task_id, result = await self.task_pool.wait_for_next_completion()

                    if result is not None:
                        # Yield publishable content if available
                        if result.publishable is not None:
                            yield result.publishable

                        # Add new tasks if any (respecting limits)
                        if result.next:
                            tasks_to_add = []
                            for new_task in result.next:
                                logger.debug(f"NEW TASKS: {len(result.next)}")
                                if self.total_tasks_created < self.max_total_tasks:
                                    tasks_to_add.append(new_task)
                                    self.total_tasks_created += 1
                                else:
                                    logger.warning(
                                        f"Max tasks limit ({self.max_total_tasks}) reached, "
                                        f"skipping new task: {new_task.id}"
                                    )

                            if tasks_to_add:
                                await self.task_pool.add_tasks(tasks_to_add)
                                logger.debug(
                                    f"Added {len(tasks_to_add)} new tasks from {task_id}"
                                )

                except StopIteration:
                    break
                except Exception as e:
                    logger.error(f"Error in streaming iterator: {e}")
                    continue

            # Log final statistics
            stats = self.task_pool.get_stats()
            logger.info(f"Streaming completed. Stats: {stats}")

        finally:
            await self.task_pool.shutdown()


def create_streaming_task(
    task_id: str,
    coroutine_or_factory: Union[Coroutine, Callable[[], Coroutine]],
    timeout: float = 30.0,
) -> StreamingTask:
    """
    Convenience function to create a StreamingTask from a coroutine or factory function.

    Args:
        task_id: Unique identifier for the task
        coroutine_or_factory: Either a coroutine or a function that returns a coroutine
        timeout: Maximum time to wait for task completion

    Returns:
        StreamingTask instance
    """
    if asyncio.iscoroutine(coroutine_or_factory):
        # If it's already a coroutine, we need to create a factory
        # Note: This approach recreates the coroutine, so the original logic should be in a function
        raise ValueError(
            "Cannot create StreamingTask from an already-created coroutine. "
            "Please provide a factory function that returns a fresh coroutine."
        )

    if callable(coroutine_or_factory):
        return StreamingTask(
            id=task_id, coroutine_factory=coroutine_or_factory, timeout=timeout
        )

    raise ValueError("coroutine_or_factory must be a callable that returns a coroutine")


U = TypeVar("U")


# Convenience function for creating iterators
def create_dynamic_iterator(
    initial_task_factories: list[
        tuple[str, Callable[[], Awaitable[TaskResult[U]]], float]
    ],
    max_concurrent_tasks: int = 10,
    max_total_tasks: int = 1000,
) -> DynamicStreamingIterator[U]:
    """
    Create a DynamicStreamingIterator from a list of task factory specifications.

    Args:
        initial_task_factories: List of (task_id, factory_function, timeout) tuples
        max_concurrent_tasks: Maximum number of concurrent tasks
        max_total_tasks: Maximum total tasks that can be created

    Returns:
        DynamicStreamingIterator instance

    Example:
        ```python
        # Define task factories for data processing
        async def process_batch_task(batch_id: str) -> TaskResult[dict]:
            # Process a batch of data
            result_data = {"batch_id": batch_id, "status": "processed"}

            # Create follow-up tasks
            next_tasks = []
            for i in range(3):  # Create 3 follow-up tasks
                next_tasks.append(
                    create_streaming_task(
                        f"followup_{batch_id}_{i}",
                        lambda: followup_task(f"{batch_id}_{i}"),
                        timeout=10.0
                    )
                )

            return TaskResult[dict](
                publishable=result_data,
                next=next_tasks
            )

        async def followup_task(task_id: str) -> TaskResult[dict]:
            # Process follow-up work
            await asyncio.sleep(0.1)
            return TaskResult[dict](
                publishable={"task_id": task_id, "result": "completed"},
                next=[]
            )

        # Create the iterator with explicit type
        iterator = create_dynamic_iterator(
            initial_task_factories=[
                ("batch_1", lambda: process_batch_task("batch_1"), 30.0),
                ("batch_2", lambda: process_batch_task("batch_2"), 30.0),
            ],
            max_concurrent_tasks=5,
            max_total_tasks=50
        )

        # Use the iterator
        async def process_results():
            async for result in iterator:
                print(f"Processed: {result}")
        ```
    """
    initial_tasks = [
        create_streaming_task(task_id, factory, timeout)
        for task_id, factory, timeout in initial_task_factories
    ]

    return DynamicStreamingIterator[U](
        initial_tasks=initial_tasks,
        max_concurrent_tasks=max_concurrent_tasks,
        max_total_tasks=max_total_tasks,
    )
