import asyncio
from datetime import datetime, timedelta
import threading
import time

from core.helpers import bcolors


class BaseTask:
    """
    A base class for defining recurring tasks.

    Args:
        name (str, optional): The name of the task. Defaults to "Unnamed Task".

    Attributes:
        name (str): The name of the task.
        _timer (threading.Timer): The timer object used for scheduling task runs.
        _running (bool): A flag indicating whether the task is currently running.

    Methods:
        start(): Starts the task.
        stop(): Stops the task.
        run(): Runs the task.
        exec(): Placeholder method for defining task behavior.
        countdown(): Property method that returns the time interval between task runs.
    """
    
    def __init__(self, name: str = "Unnamed Task") -> None:
        """
        Initializes a new BaseTask instance.

        Args:
            name (str, optional): The name of the task. Defaults to "Unnamed Task".
        """
        self.name = name
        self._running = True

    @property
    def countdown(self):
        """
        Returns the time interval between task runs.
        """
        return None
    
    async def start(self) -> None:
        """
        Starts the task.
        """
        self._running = True
        await asyncio.sleep(self.countdown)
        await self.run()

    async def stop(self):
        """
        Stops the task.
        """
        self._running = False

    async def run(self) -> None:
        """
        Runs the task and prints task status and execution time.
        """
        if not self._running:
            return

        try:
            start = time.time()
            await self.exec()

            end = time.time()
            time_spent = end - start

            next_iteration = datetime.today() + timedelta(seconds=round(self.countdown, 2))
            next_iteration = next_iteration.replace(microsecond=0)

            success_message = (
                f"{bcolors.OKGREEN}TASK SUCCESSFUL{bcolors.ENDC}"
                f"{bcolors.BOLD}: {self.name}{bcolors.ENDC}"
                f" - Time spent: {bcolors.BOLD}{str(round(time_spent, 2))}{bcolors.ENDC}s"
                f" - Next iteration: {bcolors.BOLD}{next_iteration}{bcolors.ENDC}s"
            )
            print(success_message)

        except Exception as e:
            # Log this
            end = time.time()
            time_spent = end - start

            failure_message = (
                f"{bcolors.FAIL}{bcolors.BOLD}{bcolors.UNDERLINE}TASK FAILED{bcolors.ENDC}"
                f"{bcolors.ENDC}{bcolors.BOLD}: {self.name}{bcolors.ENDC}"
                f" - Time spent: {bcolors.BOLD}{str(round(time_spent, 2))}{bcolors.ENDC}s"
                f" - Error: {e}"
            )
            print(failure_message)
            await self.stop()
            raise e

        else:
            await asyncio.sleep(self.countdown)
            if self._running:
                await self.run()

    async def exec(self) -> None:
        """
        Placeholder method for defining task behavior.
        """
        pass
