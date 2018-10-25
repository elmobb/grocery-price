import time
from datetime import datetime

import click
from scrapinghub import ScrapinghubClient
from scrapinghub.client.exceptions import DuplicateJobError


@click.command()
@click.argument("spider_name")
@click.option("--wait", is_flag=True, help="Wait for the job finishes")
@click.option("--scrapy-api-key", envvar="SCRAPY_API_KEY", hidden=True)
@click.option("--scrapy-project-id", envvar="SCRAPY_PROJECT_ID", hidden=True)
def crawl(scrapy_api_key, scrapy_project_id, spider_name, wait):
    """Start a crawl job on Scrapy Cloud.

    Default is to return job ID after job starts.
    """
    client = ScrapinghubClient(scrapy_api_key)
    project = client.get_project(scrapy_project_id)

    try:
        job = project.jobs.run(spider=spider_name)

    except DuplicateJobError:
        # No repeated job for a spider.
        click.echo(f"{spider_name} already scheduled")
        return

    # Do not wait for job finished.
    if not wait:
        click.echo(job.key)
        return

    # Wait for job finished.
    while job.metadata.get("state") == "running":
        stats = job.metadata.get("scrapystats")
        t = datetime.now().strftime("%H:%M:%S")

        if stats is None:
            click.echo(f"{t}: Stats is not available yet...")
        else:
            click.echo(f"{t}: Items scraped: {stats.get('item_scraped_count',0)}...")

        time.sleep(10)

    click.echo("")
    click.echo(job.metadata.list())
    click.echo("")
    click.echo(f"Job '{job.key}' ended.")
