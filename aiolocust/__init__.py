import asyncio
import os
from collections import defaultdict

os.environ["LOCUST_SKIP_MONKEY_PATCH"] = "1"
import logging

from locust.env import Environment

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s:%(message)s",
)
logger = logging.getLogger(__name__)


class AIOUser:
    tasks = []
    weight = 1

    def __init__(self, environment: Environment):
        self.environment = environment

    def start(self) -> None:
        self._running = True
        self._task: asyncio.Task = asyncio.create_task(self._run_tasks())

    async def _run_tasks(self) -> None:
        if not self.tasks:
            logger.error("You forgot to define any tasks :(")
            raise Exception("You forgot to define any tasks :(")
        try:
            while self._running:
                for t in self.tasks:
                    await t(self)
                    await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.debug("cancelled")
        finally:
            logger.debug("stopped")

    async def stop(self) -> None:
        self._running = False
        self._task.cancel()


class AIOWorkerRunner:
    def __init__(self, environment: Environment) -> None:
        self.environment = environment
        self.users: dict[str, list[AIOUser]] = defaultdict(list)

    def spawn_users(self, user_classes_spawn_count, wait: bool = False):  # type: ignore
        def spawn(user_class: str, spawn_count: int) -> list[AIOUser]:
            n = 0
            new_users: list[AIOUser] = []
            while n < spawn_count:
                new_user: AIOUser = self.environment.user_classes_by_name[user_class](self.environment)  # type: ignore
                assert hasattr(
                    new_user, "environment"
                ), f"Attribute 'environment' is missing on user {user_class}. Perhaps you defined your own __init__ and forgot to call the base constructor? (super().__init__(*args, **kwargs))"
                new_user.start()
                new_users.append(new_user)
                self.users[user_class].append(new_user)
                n += 1
                if n % 10 == 0 or n == spawn_count:
                    logger.debug(f"{n} new users spawned")
            logger.debug(f"All users of class {user_class} spawned")
            return new_users

        new_users: list[AIOUser] = []
        for user_class, spawn_count in user_classes_spawn_count.items():
            new_users += spawn(user_class, spawn_count)

        return new_users

    async def stop_users(self, user_classes_stop_count: dict[str, int]) -> None:
        to_stop = []
        for user_class, stop_count in user_classes_stop_count.items():
            for i in range(stop_count):
                user = self.users[user_class].pop()
                to_stop.append(user.stop())
        for coro in to_stop:
            await coro

    async def stop(self):
        to_stop = []
        for user_class, user_list in self.users.items():
            while user_list:
                user = user_list.pop()
                to_stop.append(user.stop())
        for coro in to_stop:
            await coro


class MyUser(AIOUser):
    async def task_1(self) -> None:
        logger.debug("inside task")
        await asyncio.sleep(1)

    tasks = [task_1]


async def async_main() -> None:
    runner = AIOWorkerRunner(Environment(user_classes=[MyUser]))
    logger.info("spawning")
    runner.spawn_users({MyUser.__name__: 10})
    logger.info("sleeping")
    await asyncio.sleep(2)
    logger.info("stopping some")
    await runner.stop_users({MyUser.__name__: 1})
    logger.info("sleeping again")
    await asyncio.sleep(2)
    logger.info("done!")


def main():
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
