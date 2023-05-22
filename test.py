from datetime import datetime, date


def lmao(session_date = None):
    now = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    if isinstance(session_date, date):
        session_date = datetime.combine(session_date, datetime.min.time())

        session_date = session_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        )

    if not session_date:
        return now

    return max(session_date, now)

x = datetime.date(datetime.now())
# print(x)
print(lmao(None))

x = datetime.now().replace(year=3002, day=29, hour=0, minute=0, second=0, microsecond=0)
print(lmao(x))
