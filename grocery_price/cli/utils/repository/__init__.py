from urllib.parse import urlsplit

from grocery_price.cli.utils.repository.local import LocalHandler
from grocery_price.cli.utils.repository.sftp import SftpHandler


def get_repository_handler(feed_uri):
    scheme = urlsplit(feed_uri).scheme

    if scheme == "file":
        return LocalHandler(feed_uri=feed_uri)

    if scheme == "sftp":
        return SftpHandler(feed_uri=feed_uri)

    raise NotImplementedError
