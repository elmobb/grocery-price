import click
from scrapinghub import ScrapinghubClient

from grocery_price.cli.utils import get_repository_handler, timestamp_to_date_string


@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite existing file.")
@click.option("--feed-uri", envvar="FEED_URI", hidden=True)
@click.option("--scrapy-api-key", envvar="SCRAPY_API_KEY", hidden=True)
@click.option("--scrapy-project-id", envvar="SCRAPY_PROJECT_ID", hidden=True)
def download(feed_uri, scrapy_api_key, scrapy_project_id, overwrite=False):
    """Download item files from Scrapy Cloud.

    Default is to skip item files if existed.
    Item files is deemed identical if they have same filename.
    """
    repo = get_repository_handler(feed_uri=feed_uri)
    client = ScrapinghubClient(scrapy_api_key)
    project = client.get_project(scrapy_project_id)
    spiders = [project.spiders.get(i["id"]) for i in project.spiders.list()]

    for spider in spiders:

        existing_files = repo.get_item_files(spider_name=spider.name)

        # Assume Scrapy Cloud's api will return jobs in reverse chronological order.
        jobs = [client.get_job(i["key"]) for i in spider.jobs.list() if i["close_reason"] == "finished"]

        for job_counter, job in enumerate(jobs, start=1):

            filename = f"{timestamp_to_date_string(job.metadata.get('scrapystats')['start_time'])}.json"
            click.echo(f"Processing {spider.name}'s job {job_counter}/{len(jobs)} ({filename})", nl=False)

            if filename not in existing_files:
                repo.create_item_file(items=job.items.list(), spider_name=spider.name, filename=filename)
                click.echo(" - create")

            elif overwrite:
                repo.create_item_file(items=job.items.list(), spider_name=spider.name, filename=filename)
                click.echo(" - overwrite")

            else:
                click.echo(" - skip")
