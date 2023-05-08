from app.swipe_session.services.swipe_session import SwipeSessionService
from core.tasks.base_task import BaseTask
from datetime import datetime, timedelta
import asyncio


class Task(BaseTask):
    def __init__(self) -> None:
        name = "Cancel outdated swipe sessions"
        super().__init__(name=name)

    @property
    def countdown(self):
        # Everyday at 01:00:00
        # x = datetime.today()
        # y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0)
        # if x > y:
        #     y += timedelta(days=1)

        # delta_t = y - x
        # return delta_t.total_seconds()
        return 5

    def exec(self) -> None:

        async def func():
            await SwipeSessionService().update_all_outdated_to_cancelled()

        asyncio.run(func())
        