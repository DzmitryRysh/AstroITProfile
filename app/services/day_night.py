from datetime import datetime


def is_day_chart(local_dt: datetime) -> bool:
    hour = local_dt.hour
    return 6 <= hour < 18
