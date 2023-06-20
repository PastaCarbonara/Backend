from sqlalchemy import and_, or_, update
from core.db.enums import SwipeSessionEnum
from core.db.models import SwipeSession
from core.tasks.base_task import BaseTask
from datetime import datetime, timedelta


class Task(BaseTask):
    def __init__(self, session, capture_exceptions) -> None:
        name = "Cancel outdated swipe sessions"
        super().__init__(session, capture_exceptions, name)

    @property
    def countdown(self):
        return 60 * 20  # every 20 minutes
        # Everyday at 01:00:00
        x = datetime.today()
        y = x.replace(day=x.day, hour=1, minute=0, second=0, microsecond=0)
        if x > y:
            y += timedelta(days=1)

        delta_t = y - x
        return delta_t.total_seconds()

    def exec(self) -> None:
        print("EXECUTING TASK!")
        cur_date = datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
        query = (
            update(SwipeSession)
            .where(
                and_(
                    SwipeSession.session_date < cur_date,
                    or_(
                        SwipeSession.status == SwipeSessionEnum.READY,
                        SwipeSession.status == SwipeSessionEnum.IN_PROGRESS,
                    )
                )
            )
            .values(status=SwipeSessionEnum.CANCELLED)
        )
        self.session.execute(query)
        self.session.commit()
        print("END OF TASK")