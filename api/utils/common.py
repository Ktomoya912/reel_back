from datetime import datetime, timedelta


def get_jst_now():
    return datetime.utcnow() + timedelta(hours=9)
