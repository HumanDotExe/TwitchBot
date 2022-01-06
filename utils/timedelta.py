import datetime
from typing import Dict


def format_timedelta(timedelta: datetime.timedelta) -> Dict[str, str]:
    delta = {"days": str(timedelta.days)}
    delta['hours'], rem = divmod(timedelta.seconds, 3600)
    delta['minutes'], delta['seconds'] = divmod(rem, 60)
    delta['hours'] = str(delta['hours']).zfill(2)
    delta['minutes'] = str(delta['minutes']).zfill(2)
    delta['seconds'] = str(delta['seconds']).zfill(2)
    return delta
