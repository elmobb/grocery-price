import json
import logging
import os
from datetime import datetime, timezone
from time import sleep
from urllib.parse import urlsplit

import paramiko
import scrapinghub

logging.getLogger().setLevel(logging.INFO)


class SpidersMaster(object):
    """Master of spiders. Can instruct spiders to perform actions.
    """
    _time_between_checking_state = 15

    def __init__(self, api_key=None, project_id=None, spiders=None, uri=None):
        self.client = scrapinghub.ScrapinghubClient(api_key or os.environ.get("SCRAPY_API_KEY"))
        project = self.client.get_project(project_id or os.environ.get("SCRAPY_PROJECT_ID"))
        self.spiders = spiders or [project.spiders.get(i["id"]) for i in project.spiders.list()]
        self.uri = uri or os.environ.get("FEED_URI")

    def start_crawl(self):
        """Start a Scrapy job and export items to destination.

        Jobs are run sequentially, assuming that under free tier there is only 1 scraping unit.
        Files are named using finished time.
        """
        for spider in self.spiders:

            # Start a job.
            try:
                job = spider.jobs.run()
            except scrapinghub.client.exceptions.BadRequest:
                # Spider is already running.
                logging.debug(f"spider '{spider.name}' is already running.")
                continue

            # Wait for job finished.
            while job.metadata.get("state").lower() in ["pending", "running"]:
                logging.info(f"spider '{spider.name}' is running.")
                sleep(self._time_between_checking_state)

            # Job ends with invalid state.
            if job.metadata.get("state").lower() != "finished":
                logging.debug(f"job '{job.key}' ends with invalid state. {job.metadata.list()}")
                continue

            # Get items from job.
            items = job.items.list()

            # URI to put JSON file to.
            finish_time = self._timestamp_to_date_string(job.metadata.get("finished_time"))
            uri = self.uri.replace("%(name)s", spider.name).replace("%(time)s", finish_time)
            o = urlsplit(uri)

            # JSON file name.
            file_name = o.path.split("/")[-1]

            # Write items to local file first for better performance.
            with open(file_name, "w", encoding="utf8") as f:
                json.dump(items, f, ensure_ascii=False)

            # Upload items file to target location.
            transport = paramiko.Transport((o.hostname, o.port))
            transport.connect(username=o.username, password=o.password)
            sftp = paramiko.SFTPClient.from_transport(transport)
            sftp.put(file_name, o.path)
            sftp.close()

            # Delete local file.
            os.remove(file_name)

    @staticmethod
    def _timestamp_to_date_string(timestamp, format_="%Y-%m-%dT%H-%M-%S"):
        return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime(format_)


if __name__ == "__main__":
    instructor = SpidersMaster()
    instructor.start_crawl()
