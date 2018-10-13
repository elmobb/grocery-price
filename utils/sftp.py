from urllib.parse import urlsplit

import paramiko

from config import Config


def get_session():
    o = urlsplit(Config().FEED_URI)
    transport = paramiko.Transport((o.hostname, o.port))
    transport.connect(username=o.username, password=o.password)
    return paramiko.SFTPClient.from_transport(transport)
