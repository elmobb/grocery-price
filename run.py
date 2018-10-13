"""Run tasks."""
import sys

from utils import download_item_files, load_item_files

if __name__ == "__main__":
    args = sys.argv

    if args[1] == "download":
        download_item_files()

    elif args[1] == "load":
        args = dict(zip(["file_count"], sys.argv[2:]))
        load_item_files(file_count=int(args["file_count"]))

    else:
        raise NotImplementedError
