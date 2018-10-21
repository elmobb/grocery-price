from cli.load import load
from tests.test_cli import test_cli
from models import Product, Price


class Test(test_cli.TestCase):
    def test_spider_name_must_be_provided(self):
        result = self.runner.invoke(load, [], catch_exceptions=False)
        self.assertEqual(2, result.exit_code)

    def test_load_items_and_upload_to_database(self):
        result = self.runner.invoke(load, ["test_spider_1", "test_file_1.json"], catch_exceptions=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("\n".join([
            "(1/1) test_file_1.json: Loading items...1 items found...Uploading...",
            ""
        ]), result.output)
        self.assertEqual(1, self.session.query(Product).count())
        self.assertEqual(1, self.session.query(Price).count())

    def test_load_all_files_of_spider(self):
        result = self.runner.invoke(load, ["test_spider_1"], catch_exceptions=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("\n".join([
            "(1/2) test_file_2.json: Loading items...1 items found...Uploading...",
            "(2/2) test_file_1.json: Loading items...1 items found...Uploading...",
            ""
        ]), result.output)
        self.assertEqual(1, self.session.query(Product).count())
        self.assertEqual(1, self.session.query(Price).count())

    def test_load_1_file_of_spider(self):
        result = self.runner.invoke(load, ["--file-count", 1, "test_spider_1"], catch_exceptions=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("\n".join([
            "(1/1) test_file_2.json: Loading items...1 items found...Uploading...",
            ""
        ]), result.output)
        self.assertEqual(1, self.session.query(Product).count())
        self.assertEqual(1, self.session.query(Price).count())
