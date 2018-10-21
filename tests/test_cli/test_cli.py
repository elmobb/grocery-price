import os
import unittest
from datetime import datetime

from click.testing import CliRunner

from models import get_session


class TestCase(unittest.TestCase):
    DATABASE_URI = f"sqlite:///tmp_{datetime.now().strftime('%s')}.db"
    FEED_URI = "file:///tests/test_repo/%(name)s/%(time)s.json"

    def setUp(self):
        self.runner = CliRunner(env={
            "DATABASE_URI": self.DATABASE_URI,
            "FEED_URI":     self.FEED_URI
        })
        self.session = get_session(uri=self.DATABASE_URI)

    def tearDown(self):
        self.session.close()
        os.remove(self.DATABASE_URI.replace("sqlite:///", ""))
