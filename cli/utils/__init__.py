from datetime import datetime, timezone

from cli.utils.repository_handler import *


def timestamp_to_date_string(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
