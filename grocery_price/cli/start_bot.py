import subprocess
import sys
import time

import click
from watchdog.events import PatternMatchingEventHandler
from watchdog.observers import Observer


class CodeUpdateHandler(PatternMatchingEventHandler):
    """This class monitors code updated, and restart bot server after that.

    A restarting flag is used to indicate if the handler is restarting.
    Multiple file changes in short duration will trigger one restart only.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.process = None
        self.restarting = False
        self.start_server()

    def start_server(self):
        self.process = subprocess.Popen([sys.executable, "-m", "grocery_price.bot"])

    def terminate_server(self):
        self.process.terminate()

    def on_modified(self, event):
        if not self.restarting:
            self.restarting = True
            click.echo("File changes detected, restarting server...", nl=False)
            self.terminate_server()
            self.start_server()
            click.echo("Done.")
            self.restarting = False


@click.command()
def start_bot():
    """Start Telegram bot. Will restart server if any file changes is detected.
    """
    observer = Observer()
    handler = CodeUpdateHandler(patterns=["*.py"])
    observer.schedule(handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        handler.terminate_server()
        observer.stop()
    observer.join()
