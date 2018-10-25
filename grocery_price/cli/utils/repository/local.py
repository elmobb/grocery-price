import json
import os

from grocery_price.cli.utils.repository.utils import RepositoryHandler, _dump_items_to_local_file, _get_path


class LocalHandler(RepositoryHandler):
    """This class handles local file system repository.
    """

    def get_spider_names(self):
        return [i for i in os.listdir(self.root_dir) if os.path.isdir(_get_path(self.root_dir, i))]

    def get_item_files(self, spider_name):
        return [i for i in os.listdir(_get_path(self.root_dir, spider_name)) if
                not os.path.isdir(_get_path(self.root_dir, spider_name, i))]

    def get_items_from_item_file(self, spider_name, filename):
        with open(_get_path(self.root_dir, spider_name, filename), encoding="utf8") as f:
            return json.load(f)

    def create_item_file(self, items, spider_name, filename):
        _dump_items_to_local_file(items=items, path=_get_path(self.root_dir, spider_name, filename))

    def write_cleaned_item_file(self, items, spider_name, filename):
        _dump_items_to_local_file(items=items, path=_get_path(self.root_dir, spider_name, "clean", filename))

    def close(self):
        return
