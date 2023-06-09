#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from sync.cli import Main

if __name__ == "__main__":
    root_folder = Path(__file__).resolve().parent.parent

    try:
        github_token = os.environ["GITHUB_TOKEN"]
    except KeyError:
        github_token = None

    Main.set_args(root_folder=root_folder,github_token=github_token)
    sys.exit(Main.exec())
