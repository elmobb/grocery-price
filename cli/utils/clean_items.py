def get_cleaned_items(items, spider_name, filename):
    cleaned_items = []

    for i in items:

        # Incorrect year in update_time. (e.g. '14-01-16 14:00:21').
        if isinstance(i["update_time"], str) and i["update_time"][2] == "-":
            i["update_time"] = (filename[:4] + i["update_time"][2:])

        cleaned_items.append(i)

    return cleaned_items
