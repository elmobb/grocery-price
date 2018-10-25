import json
import os
from urllib.parse import urlsplit


def _get_path(*args, **kwargs):
    """Handle os.path.join in Windows mixing up "/" and "\".
    """
    return os.path.join(*args, **kwargs).replace("\\", "/")


def _dump_items_to_local_file(items, path):
    with open(path, "w", encoding="utf8") as f:
        json.dump(items, f, ensure_ascii=False, default=str)


class RepositoryHandler(object):
    """Base class to handles interaction with item files repository.

    Feed repository must be of below structure.

    root_directory/
    |── spider_1/
    |   |── clean/
    |   |   |── 2018-01-01T12-00-01.json
    |   |   |── 2018-01-02T13-00-01.json
    |   |── 2018-01-01T12-00-01.json
    |   |── 2018-01-02T13-00-01.json
    |── spider_2/
    |   |── 2018-01-01T14-00-01.json

    """

    def __init__(self, feed_uri):
        feed = urlsplit(feed_uri)
        self.hostname = feed.hostname
        self.port = feed.port
        self.username = feed.username
        self.password = feed.password
        self.root_dir = os.path.split(os.path.split(feed.path)[0])[0][1:]  # Remove leading "/"

    def get_spider_names(self):
        raise NotImplementedError

    def get_item_files(self, spider_name):
        raise NotImplementedError

    def get_items_from_item_file(self, spider_name, filename):
        raise NotImplementedError

    def create_item_file(self, items, spider_name, filename):
        raise NotImplementedError

    def write_cleaned_item_file(self, items, spider_name, filename):
        raise NotImplementedError

    def close(self):
        raise NotImplementedError
