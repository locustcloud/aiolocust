import asyncio
import os

import pytest

os.environ["LOCUST_SKIP_MONKEY_PATCH"] = "1"

from locust.env import Environment

from aiolocust import AIOUser, AIOWorkerRunner


@pytest.mark.asyncio
async def test_stuff():
    has_run = False

    class MyUser(AIOUser):
        async def task_1(self) -> None:
            nonlocal has_run
            has_run = True
            await asyncio.sleep(1)

        tasks = [task_1]

    runner = AIOWorkerRunner(Environment(user_classes=[MyUser]))  # type: ignore # maybe adjust Environment class to allow AIOUsers

    runner.spawn_users({MyUser.__name__: 10})
    await asyncio.sleep(2)
    assert has_run
    await runner.stop()
