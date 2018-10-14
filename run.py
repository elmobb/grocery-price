import click

from utils import download_item_files, load_item_files


@click.group()
def cli():
    pass


# Download item files from Scrapy Cloud.
@click.command()
@click.option("--overwrite", is_flag=True, help="Overwrite existing files")
def download(overwrite):
    download_item_files(overwrite=overwrite)


# Load items in item files to database.
@click.command()
@click.option("--file-count", type=click.IntRange(), help="Number of files to load")
@click.option("--demo", is_flag=True, default=True, help="Run demo to convert item files data to items")
def load(file_count, demo):
    load_item_files(file_count=file_count, demo=demo)


cli.add_command(download)
cli.add_command(load)

if __name__ == "__main__":
    cli()
