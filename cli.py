#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import sys
from pathlib import Path
from sync.cli import Main

if __name__ == "__main__":
    cwd_folder = Path(__name__).resolve().parent

    try:
        github_token = os.environ["GITHUB_TOKEN"]
    except KeyError:
        github_token = None

    Main.set_default_args(root_folder=cwd_folder, github_token=github_token)
    sys.exit(Main.exec())
