import json
import os
import stat

import paramiko
from paramiko.ssh_exception import SSHException
from grocery_price.cli.utils.repository.utils import RepositoryHandler, _dump_items_to_local_file, _get_path


class SftpHandler(RepositoryHandler):
    """This class handles SFTP repository.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup_session()

    def _setup_session(self):
        transport = paramiko.Transport((self.hostname, self.port))
        transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(transport)

    def get_spider_names(self):
        return [i.filename for i in self.sftp.listdir_attr(self.root_dir) if stat.S_ISDIR(i.st_mode)]

    def get_item_files(self, spider_name):
        return [i for i in self.sftp.listdir(_get_path(self.root_dir, spider_name)) if ".json" in i]

    def get_items_from_item_file(self, spider_name, filename, retries=10):
        try:
            with self.sftp.open(filename=_get_path(self.root_dir, spider_name, filename)) as f:
                return json.load(f)

        except SSHException:
            self._setup_session()  # Reset sftp session.
            if retries > 0:
                return self.get_items_from_item_file(spider_name=spider_name, filename=filename, retries=retries - 1)
            else:
                return None

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
