from datetime import timezone

from grocery_price.cli.utils.clean_items import *
from grocery_price.cli.utils.repository_handler import *
from grocery_price.cli.utils.update_product_price_records import *


def timestamp_to_date_string(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")
