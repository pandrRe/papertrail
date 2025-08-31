"""
Tests for the dynamic streaming iterator system.
"""

import pytest
import asyncio
from typing import Any
from app.internal.streaming import (
    DynamicStreamingIterator,
    StreamingTaskPool,
    StreamingTask,
    TaskResult,
    create_streaming_task,
    create_dynamic_iterator,
)
from app.internal.base_model import PtBaseModel


# Fake models for testing
class FakeResultModel(PtBaseModel):
    """Fake model for testing streaming."""

    id: str
    content: str
    processed: bool = False


class FakeListModel(PtBaseModel):
    """Fake list model for testing."""

    items: list[FakeResultModel]
    count: int


class TestStreamingTask:
    """Test the StreamingTask class."""

    def test_create_streaming_task_with_factory(self):
        """Test creating a streaming task with a coroutine factory."""

        async def sample_coroutine():
            return TaskResult(publishable=None, next=[])

        task = create_streaming_task("test_task", sample_coroutine, timeout=15.0)

        assert task.id == "test_task"
        assert task.timeout == 15.0
        assert callable(task.coroutine_factory)
        assert task.created_at > 0

    def test_create_streaming_task_rejects_coroutine(self):
        """Test that creating a task with an existing coroutine raises an error."""

        async def sample_coroutine():
            return TaskResult(publishable=None, next=[])

        # Create the coroutine instance
        coro = sample_coroutine()

        with pytest.raises(
            ValueError,
            match="Cannot create StreamingTask from an already-created coroutine",
        ):
            create_streaming_task("test_task", coro)

        # Clean up
        coro.close()

    def test_streaming_task_create_coroutine(self):
        """Test creating a coroutine from the factory."""

        async def sample_coroutine():
            return TaskResult(publishable=None, next=[])

        task = StreamingTask(
            id="test", coroutine_factory=sample_coroutine, timeout=10.0
        )

        coro = task.create_coroutine()
        assert asyncio.iscoroutine(coro)

        # Clean up
        coro.close()


class TestStreamingTaskPool:
    """Test the StreamingTaskPool class."""

    @pytest.mark.asyncio
    async def test_task_pool_initialization(self):
        """Test task pool initialization."""
        pool = StreamingTaskPool(max_concurrent_tasks=5)

        assert pool.max_concurrent_tasks == 5
        assert len(pool.active_tasks) == 0
        assert len(pool.pending_tasks) == 0
        assert pool.completed_count == 0
        assert pool.failed_count == 0
        assert pool.timeout_count == 0

    @pytest.mark.asyncio
    async def test_add_task_within_limit(self):
        """Test adding a task when under the concurrent limit."""
        pool = StreamingTaskPool(max_concurrent_tasks=2)

        async def quick_task():
            await asyncio.sleep(0.1)
            return TaskResult(
                publishable=FakeResultModel(id="test1", content="result1"), next=[]
            )

        task = StreamingTask(id="quick_task", coroutine_factory=quick_task, timeout=5.0)

        await pool.add_task(task)

        assert len(pool.active_tasks) == 1
        assert len(pool.pending_tasks) == 0
        assert "quick_task" in pool.active_tasks

        # Clean up
        await pool.shutdown()

    @pytest.mark.asyncio
    async def test_add_task_exceeds_limit(self):
        """Test adding tasks that exceed the concurrent limit."""
        pool = StreamingTaskPool(max_concurrent_tasks=1)

        async def slow_task():
            await asyncio.sleep(10)  # Long task to test queuing
            return TaskResult(publishable=None, next=[])

        task1 = StreamingTask(id="task1", coroutine_factory=slow_task)
        task2 = StreamingTask(id="task2", coroutine_factory=slow_task)

        await pool.add_task(task1)
        await pool.add_task(task2)

        assert len(pool.active_tasks) == 1
        assert len(pool.pending_tasks) == 1

        # Clean up
        await pool.shutdown()

    @pytest.mark.asyncio
    async def test_task_completion_and_stats(self):
        """Test task completion and statistics tracking."""
        pool = StreamingTaskPool(max_concurrent_tasks=2)

        async def successful_task():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(id="success", content="completed"), next=[]
            )

        async def failing_task():
            await asyncio.sleep(0.05)
            raise Exception("Task failed")

        task1 = StreamingTask(id="success", coroutine_factory=successful_task)
        task2 = StreamingTask(id="failure", coroutine_factory=failing_task)

        await pool.add_task(task1)
        await pool.add_task(task2)

        # Wait for first completion
        task_id, result = await pool.wait_for_next_completion()

        if task_id == "success":
            assert result is not None
            assert isinstance(result.publishable, FakeResultModel)
            assert result.publishable.content == "completed"
        else:
            assert result is None  # Failed task

        # Wait for second completion
        task_id, result = await pool.wait_for_next_completion()

        stats = pool.get_stats()
        assert stats["completed"] >= 1
        assert stats["failed"] >= 1
        assert stats["total_processed"] == 2

        # Clean up
        await pool.shutdown()

    @pytest.mark.asyncio
    async def test_task_timeout(self):
        """Test task timeout handling."""
        pool = StreamingTaskPool(max_concurrent_tasks=1)

        async def timeout_task():
            await asyncio.sleep(10)  # Will timeout
            return TaskResult(publishable=None, next=[])

        task = StreamingTask(
            id="timeout_test",
            coroutine_factory=timeout_task,
            timeout=0.1,  # Very short timeout
        )

        await pool.add_task(task)

        task_id, result = await pool.wait_for_next_completion()

        assert task_id == "timeout_test"
        assert result is None  # Timeout results in None
        assert pool.timeout_count == 1

        # Clean up
        await pool.shutdown()


class TestDynamicStreamingIterator:
    """Test the DynamicStreamingIterator class."""

    @pytest.mark.asyncio
    async def test_simple_iteration(self):
        """Test basic iteration with initial tasks."""

        async def result_task_1():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(id="result1", content="data1"), next=[]
            )

        async def result_task_2():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(id="result2", content="data2"), next=[]
            )

        initial_tasks = [
            StreamingTask(id="task1", coroutine_factory=result_task_1),
            StreamingTask(id="task2", coroutine_factory=result_task_2),
        ]

        iterator = DynamicStreamingIterator[FakeResultModel](
            initial_tasks=initial_tasks, max_concurrent_tasks=2
        )

        results = []
        async for result in iterator:
            results.append(result)

        assert len(results) == 2

        # Check that we got both results
        result_ids = {r.id for r in results}
        assert result_ids == {"result1", "result2"}

        result_contents = {r.content for r in results}
        assert result_contents == {"data1", "data2"}

    @pytest.mark.asyncio
    async def test_dynamic_task_spawning(self):
        """Test tasks that spawn additional tasks."""

        async def spawning_task(task_id: str):
            await asyncio.sleep(0.05)

            next_tasks = []
            for i in range(3):  # Spawn 3 additional tasks
                next_tasks.append(
                    StreamingTask(
                        id=f"spawned_{i}",
                        coroutine_factory=lambda: spawned_task(f"spawned_{i}"),
                    )
                )

            return TaskResult(
                publishable=FakeResultModel(id=task_id, content=f"content_{task_id}"),
                next=next_tasks,
            )

        async def spawned_task(task_id: str):
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(
                    id=task_id, content=f"spawned_content_{task_id}"
                ),
                next=[],
            )

        initial_tasks = [
            StreamingTask(
                id="initial", coroutine_factory=lambda: spawning_task("initial")
            )
        ]

        iterator = DynamicStreamingIterator[FakeResultModel](
            initial_tasks=initial_tasks, max_concurrent_tasks=5, max_total_tasks=10
        )

        results = []
        async for result in iterator:
            results.append(result)

        # Should have initial task + 3 spawned tasks = 4 results
        assert len(results) == 4
        assert all(isinstance(r, FakeResultModel) for r in results)

        # Check that we got the initial and spawned results
        result_ids = {r.id for r in results}
        assert "initial" in result_ids
        assert any("spawned" in rid for rid in result_ids)

    @pytest.mark.asyncio
    async def test_max_task_limit(self):
        """Test that max_total_tasks limit is respected."""
        spawn_attempts = 0

        async def greedy_spawning_task():
            nonlocal spawn_attempts
            await asyncio.sleep(0.01)

            # Try to spawn many tasks
            next_tasks = []
            for i in range(10):
                spawn_attempts += 1
                next_tasks.append(
                    StreamingTask(
                        id=f"spawn_{spawn_attempts}",
                        coroutine_factory=lambda: simple_task(
                            f"spawn_{spawn_attempts}"
                        ),
                    )
                )

            return TaskResult(
                publishable=FakeResultModel(id="greedy", content="greedy_result"),
                next=next_tasks,
            )

        async def simple_task(task_id: str):
            await asyncio.sleep(0.01)
            return TaskResult(
                publishable=FakeResultModel(id=task_id, content=f"content_{task_id}"),
                next=[],
            )

        initial_tasks = [
            StreamingTask(id="greedy", coroutine_factory=greedy_spawning_task)
        ]

        iterator = DynamicStreamingIterator[FakeResultModel](
            initial_tasks=initial_tasks,
            max_concurrent_tasks=5,
            max_total_tasks=5,  # Low limit to test
        )

        results = []
        async for result in iterator:
            results.append(result)

        # Should be limited by max_total_tasks
        assert len(results) <= 5

    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in the iterator."""

        async def successful_task():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(id="success", content="success_data"),
                next=[],
            )

        async def failing_task():
            await asyncio.sleep(0.05)
            raise Exception("Task failed")

        initial_tasks = [
            StreamingTask(id="success", coroutine_factory=successful_task),
            StreamingTask(id="failure", coroutine_factory=failing_task),
        ]

        iterator = DynamicStreamingIterator[FakeResultModel](
            initial_tasks=initial_tasks, max_concurrent_tasks=2
        )

        results = []
        async for result in iterator:
            results.append(result)

        # Should get result from successful task, failing task should be ignored
        assert len(results) == 1
        assert isinstance(results[0], FakeResultModel)
        assert results[0].id == "success"
        assert results[0].content == "success_data"

    @pytest.mark.asyncio
    async def test_mixed_result_types(self):
        """Test iterator with mixed result types using Any."""

        async def string_task():
            await asyncio.sleep(0.05)
            return TaskResult(publishable="string result", next=[])

        async def dict_task():
            await asyncio.sleep(0.05)
            return TaskResult(publishable={"key": "value", "number": 42}, next=[])

        async def model_task():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeResultModel(id="model", content="model_data"), next=[]
            )

        initial_tasks = [
            StreamingTask(id="str", coroutine_factory=string_task),
            StreamingTask(id="dict", coroutine_factory=dict_task),
            StreamingTask(id="model", coroutine_factory=model_task),
        ]

        iterator = DynamicStreamingIterator[Any](
            initial_tasks=initial_tasks, max_concurrent_tasks=3
        )

        results = []
        async for result in iterator:
            results.append(result)

        assert len(results) == 3

        # Check that we got all different types
        result_types = {type(r).__name__ for r in results}
        expected_types = {"str", "dict", "FakeResultModel"}
        assert result_types == expected_types


class TestDynamicIteratorConvenience:
    """Test the convenience functions for creating iterators."""

    @pytest.mark.asyncio
    async def test_create_dynamic_iterator(self):
        """Test the create_dynamic_iterator convenience function."""

        async def task_factory_1():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeListModel(
                    items=[
                        FakeResultModel(id="item1", content="content1"),
                        FakeResultModel(id="item2", content="content2"),
                    ],
                    count=2,
                ),
                next=[],
            )

        async def task_factory_2():
            await asyncio.sleep(0.05)
            return TaskResult(
                publishable=FakeListModel(
                    items=[
                        FakeResultModel(id="item3", content="content3"),
                        FakeResultModel(id="item4", content="content4"),
                    ],
                    count=2,
                ),
                next=[],
            )

        iterator = create_dynamic_iterator(
            initial_task_factories=[
                ("task1", task_factory_1, 10.0),
                ("task2", task_factory_2, 15.0),
            ],
            max_concurrent_tasks=2,
            max_total_tasks=10,
        )

        results = []
        async for result in iterator:
            results.append(result)

        assert len(results) == 2
        assert all(isinstance(r, FakeListModel) for r in results)

        # Check that we got the expected items
        total_items = []
        for result in results:
            total_items.extend(result.items)

        assert len(total_items) == 4
        item_ids = {item.id for item in total_items}
        assert item_ids == {"item1", "item2", "item3", "item4"}

    @pytest.mark.asyncio
    async def test_complex_spawning_workflow(self):
        """Test a complex workflow with multiple levels of task spawning."""

        async def root_task():
            await asyncio.sleep(0.02)

            # Spawn 2 child tasks
            child_tasks = [
                StreamingTask(
                    id=f"child_{i}", coroutine_factory=lambda i=i: child_task(i)
                )
                for i in range(2)
            ]

            return TaskResult(
                publishable=FakeResultModel(id="root", content="root_data"),
                next=child_tasks,
            )

        async def child_task(child_id: int):
            await asyncio.sleep(0.02)

            # Each child spawns 2 grandchild tasks
            grandchild_tasks = [
                StreamingTask(
                    id=f"grandchild_{child_id}_{j}",
                    coroutine_factory=lambda child_id=child_id, j=j: grandchild_task(
                        child_id, j
                    ),
                )
                for j in range(2)
            ]

            return TaskResult(
                publishable=FakeResultModel(
                    id=f"child_{child_id}", content=f"child_data_{child_id}"
                ),
                next=grandchild_tasks,
            )

        async def grandchild_task(child_id: int, grandchild_id: int):
            await asyncio.sleep(0.02)
            return TaskResult(
                publishable=FakeResultModel(
                    id=f"grandchild_{child_id}_{grandchild_id}",
                    content=f"grandchild_data_{child_id}_{grandchild_id}",
                ),
                next=[],
            )

        initial_tasks = [StreamingTask(id="root", coroutine_factory=root_task)]

        iterator = DynamicStreamingIterator[FakeResultModel](
            initial_tasks=initial_tasks, max_concurrent_tasks=10, max_total_tasks=20
        )

        results = []
        async for result in iterator:
            results.append(result)

        # Should have: 1 root + 2 children + 4 grandchildren = 7 results
        assert len(results) == 7

        # Check hierarchy
        root_results = [r for r in results if r.id == "root"]
        child_results = [
            r
            for r in results
            if r.id.startswith("child_") and not r.id.startswith("child_child")
        ]
        grandchild_results = [r for r in results if r.id.startswith("grandchild_")]

        assert len(root_results) == 1
        assert len(child_results) == 2
        assert len(grandchild_results) == 4

        # Check that all results are processed
        assert all(isinstance(r, FakeResultModel) for r in results)

    def test_typed_create_dynamic_iterator(self):
        """Test that create_dynamic_iterator maintains proper typing."""

        async def string_task_factory():
            return TaskResult(publishable="test string", next=[])

        async def dict_task_factory():
            return TaskResult(publishable={"key": "value"}, next=[])

        # Test with string type
        string_iterator = create_dynamic_iterator(
            initial_task_factories=[("string_task", string_task_factory, 10.0)],
            max_concurrent_tasks=1,
            max_total_tasks=5,
        )

        # Test with dict type
        dict_iterator = create_dynamic_iterator(
            initial_task_factories=[("dict_task", dict_task_factory, 10.0)],
            max_concurrent_tasks=1,
            max_total_tasks=5,
        )

        # Test with custom model type
        async def model_task_factory():
            return TaskResult(
                publishable=FakeResultModel(id="test", content="test"), next=[]
            )

        model_iterator = create_dynamic_iterator(
            initial_task_factories=[("model_task", model_task_factory, 10.0)],
            max_concurrent_tasks=1,
            max_total_tasks=5,
        )

        # Verify the types are correctly inferred
        assert isinstance(string_iterator, DynamicStreamingIterator)
        assert isinstance(dict_iterator, DynamicStreamingIterator)
        assert isinstance(model_iterator, DynamicStreamingIterator)
