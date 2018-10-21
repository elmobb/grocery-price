from cli.list import list
from tests.test_cli import test_cli


class Test(test_cli.TestCase):
    def test_list_spiders(self):
        result = self.runner.invoke(list, [], catch_exceptions=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("test_spider_1\ntest_spider_2\n", result.output)

    def test_list_spider_files(self):
        result = self.runner.invoke(list, ["test_spider_1"], catch_exceptions=False)
        self.assertEqual(0, result.exit_code)
        self.assertEqual("Found 2 files.\ntest_file_2.json\ntest_file_1.json\n", result.output)
