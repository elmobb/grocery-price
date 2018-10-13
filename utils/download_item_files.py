"""Download items as JSON files from Scrapy Cloud."""
import json
import logging
import os
from datetime import datetime, timezone
from urllib.parse import urlsplit

from scrapinghub import ScrapinghubClient

from config import Config
from utils.sftp import get_session as get_sftp_session

logging.getLogger().setLevel(logging.INFO)
config = Config()


def timestamp_to_date_string(timestamp):
    return datetime.fromtimestamp(timestamp / 1000, timezone.utc).strftime("%Y-%m-%dT%H-%M-%S")


def main():
    feed_uri = config.FEED_URI  # Destination to put item files to.
    client = ScrapinghubClient(config.SCRAPY_API_KEY)
    project = client.get_project(config.SCRAPY_PROJECT_ID)
    spiders = [project.spiders.get(i["id"]) for i in project.spiders.list()]

    for spider in spiders:

        logging.info(f"Processing spider '{spider.name}'.")

        jobs = [client.get_job(i["key"]) for i in spider.jobs.list() if i["close_reason"] == "finished"]

        for job_counter, job in enumerate(jobs, start=1):

            # Files are named using job start time.
            job_start_time = timestamp_to_date_string(job.metadata.get("scrapystats")["start_time"])

            logging.info(f"Processing job {job_counter}/{len(jobs)} (start_time: {job_start_time})")

            # URI to put JSON file to.
            remote_path = urlsplit(feed_uri.replace("%(name)s", spider.name).replace("%(time)s", job_start_time)).path

            # Write items to local file first for better performance.
            local_path = remote_path.split("/")[-1]
            with open(local_path, "w", encoding="utf8") as f:
                json.dump(job.items.list(), f, ensure_ascii=False)

            # Upload items file to target location.
            with get_sftp_session() as sftp:
                sftp.put(localpath=local_path, remotepath=remote_path)

            # Delete local file.
            os.remove(local_path)


if __name__ == "__main__":
    main()
