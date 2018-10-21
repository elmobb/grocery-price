import json
import os
import stat
from urllib.parse import urlsplit

import paramiko


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


class SftpHandler(RepositoryHandler):
    """This class handles SFTP repository.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def get_spider_names(self):
        return [i.filename for i in self.sftp.listdir_attr(self.root_dir) if stat.S_ISDIR(i.st_mode)]

    def get_item_files(self, spider_name):
        return [i for i in self.sftp.listdir(_get_path(self.root_dir, spider_name)) if ".json" in i]

    def get_items_from_item_file(self, spider_name, filename):
        with self.sftp.open(filename=_get_path(self.root_dir, spider_name, filename)) as f:
            return json.load(f)

    def create_item_file(self, items, spider_name, filename):
        _dump_items_to_local_file(items=items, path=filename)  # Write items to local file first for better performance.
        self.sftp.put(localpath=filename, remotepath=_get_path(self.root_dir, spider_name, filename))
        os.remove(path=filename)  # Remove local file.

    def write_cleaned_item_file(self, items, spider_name, filename):
        _dump_items_to_local_file(items=items, path=filename)  # Write to local path first for better performance.
        self.sftp.put(localpath=filename, remotepath=_get_path(self.root_dir, spider_name, "clean", filename))
        os.remove(path=filename)

    def close(self):
        self.sftp.close()


def get_repository_handler(feed_uri):
    scheme = urlsplit(feed_uri).scheme

    if scheme == "file":
        return LocalHandler(feed_uri=feed_uri)

    if scheme == "sftp":
        return SftpHandler(feed_uri=feed_uri)

    raise NotImplementedError
