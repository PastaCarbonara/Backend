from datetime import datetime, timedelta


cur_date = datetime.today()
cur_date_2 = datetime.today().replace(hour=0, microsecond=0, minute=0, second=0)

print(cur_date, cur_date_2)
print(cur_date < cur_date_2)
