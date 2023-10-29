# Magisk Modules Repo Util
[![python](https://img.shields.io/badge/3.10+-blue.svg?label=python)](https://github.com/MRepoApp/magisk-modules-repo-util) [![release](https://img.shields.io/github/v/release/MRepoApp/magisk-modules-repo-util?label=release&color=green)](https://github.com/MRepoApp/magisk-modules-repo-util/releases/latest) [![license](https://img.shields.io/github/license/MRepoApp/magisk-modules-repo-util)](LICENSE)

- This util is to build module repository for [MRepo](https://github.com/MRepoApp/MRepo)
- `sync` is a python package
- `cli.py` is a cli tool

## Getting Started
### Install dependencies
```shell
pip3 install -r util/requirements.txt
```

### New config.json
You can write it to `your-repo/json/config.json` by yourself, or
```shell
cli.py config --stdin << EOF
{
  "name": "Your Magisk Repo",
  "base_url": "https://you.github.io/magisk-modules-repo/",
  "max_num": 3,
  "enable_log": true,
  "log_dir": "log"
}
EOF
```
or 
```shell
cli.py config --write name="Your Magisk Repo" base_url="https://you.github.io/magisk-modules-repo/" max_num=3 enable_log=true log_dir="log"
```

### New track.json
You can write it to `your-repo/modules/{id}/track.json` by yourself, or
```shell
cli.py track --stdin << EOF
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0"
}
EOF
```
or
```shell
cli.py track --add id="zygisk_lsposed" update_to="https://lsposed.github.io/LSPosed/release/zygisk.json" license="GPL-3.0"
```
If you want to generate `track.json`s from repositories on github
```shell
cli.py github --token <github-token> -u <user-name> -r <repo-name ...> 
```
> **_TIP_**: [click here to create a new api token](https://github.com/settings/personal-access-tokens/new).

### Sync
```shell
cli.py sync 
```

## How to update by GitHub Actions?
- You can refer to [demo](https://github.com/MRepoApp/demo-modules-repo) or [MRepoApp/magisk-modules-alt-repo](https://github.com/MRepoApp/magisk-modules-alt-repo).


## cli.py
```
cli.py --help
usage: cli.py [-h] [-v] [-V] command ...

Magisk Modules Repo Util

positional arguments:
  command
    config            Modify config of repository.
    track             Module tracks utility.
    github            Generate tracks from GitHub.
    sync              Sync modules in repository.
    index             Generate modules.json from local.
    check             Content check and migrate.

options:
  -h, --help          Show this help message and exit.
  -v, --version       Show util version and exit.
  -V, --version-code  Show util version code and exit.
```

## config.json
```json
{
  "name": "str",
  "base_url": "str",
  "max_num": "int",
  "enable_log": "bool",
  "log_dir": "str"
}
```
| Key | Attribute | Description |
|:-:|:-:|:-:|
| name | required | Name of your module repository |
| base_url | required | Need to end with `/` |
| max_num | optional | Max num of versions for modules, default is `3` |
| enable_log | optional | default is `true` |
| log_dir | optional | default is `null` |

## track.json
```json
{
  "id": "str",
  "enable": "bool",
  "update_to": "str",
  "changelog": "str",
  "license": "str",
  "homepage": "str",
  "source": "str",
  "support": "str",
  "donate": "str",
  "max_num": "int"
}
```
| Key | Attribute | Description |
|:-:|:-:|:-:|
| id | required | Id of Module (_in `module.prop`_) |
| enable | required | Whether to enable |
| update_to | required | Follow examples below |
| changelog | optional | Markdown or Simple Text (**_no HTML_**) |
| license | optional | SPDX ID |
| homepage | optional | Url |
| source | optional | Url |
| support | optional | Url |
| donate | optional | Url |
| max_num | optional | Overload `MAX_NUM` in config.json |

### Update from updateJson
> For those modules that provide [updateJson](https://topjohnwu.github.io/Magisk/guides.html#moduleprop). 

```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0"
}
```

### Update from local updateJson
> *update_to* requires a relative directory of *local*.
```json
{
  "id": "zygisk_lsposed",
  "update_to": "zygisk.json",
  "license": "GPL-3.0"
}
```

### Update from url
> For those have a same url to release new modules.
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://github.com/LSPosed/LSPosed/releases/download/v1.8.6/LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0",
  "changelog": "https://lsposed.github.io/LSPosed/release/changelog.md"
}
```

### Update from git
> For those we can get module by packaging all files in the repository, such as [Magisk-Modules-Repo](https://github.com/Magisk-Modules-Repo) and [Magisk-Modules-Alt-Repo](https://github.com/Magisk-Modules-Alt-Repo).

```json
{
  "id": "busybox-ndk",
  "update_to": "https://github.com/Magisk-Modules-Repo/busybox-ndk.git"
}
```

### Update from local zip
> *update_to* and *changelog* requires a relative directory of *local*.

```json
{
  "id": "zygisk_lsposed",
  "update_to": "LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0",
  "changelog": "changelog.md"
}
```

## For developer
```
your-repo
├── json
│   ├── config.json
│   └── modules.json
│
├── local
│   ├── ...
│   └── ...
│
├── log
│   ├── sync_2023-03-18.log
│   ├── ...
│   └── ...
│
├── modules
│   ├── zygisk_lsposed
│   │   ├── track.json
│   │   ├── update.json
│   │   ├── v1.8.6_6712.md
│   │   ├── v1.8.6_6712.zip
│   │   ├── ...
│   │   └── ...
│   │
│   ├── another_module
│   │   ├── ...
│   │   └── ...
│   └── .
│
└── util
```

### update.json
```json
{
  "id": "zygisk_lsposed",
  "timestamp": 1673882223.0,
  "versions": [
    {
      "timestamp": 1673882223.0,
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "zipUrl": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
      "changelog": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
    }
  ]
}
```

### track.json
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0",
  "homepage": "https://lsposed.org/",
  "source": "https://github.com/LSPosed/LSPosed.git",
  "support": "https://github.com/LSPosed/LSPosed/issues",
  "added": 1679025505.129431,
  "last_update": 1673882223.0,
  "versions": 1
}
```

## modules.json
### version 1
```json
{
  "name": "{name}",
  "metadata": {
    "version": 1,
    "timestamp": 1692439764.10608
  },
  "modules": [
    {
      "id": "zygisk_lsposed",
      "name": "Zygisk - LSPosed",
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "author": "LSPosed Developers",
      "description": "Another enhanced implementation of Xposed Framework. Supports Android 8.1 ~ 13. Requires Magisk 24.0+ and Zygisk enabled.",
      "track": {
        "type": "ONLINE_JSON",
        "added": 1679025505.129431,
        "license": "GPL-3.0",
        "homepage": "https://lsposed.org/",
        "source": "https://github.com/LSPosed/LSPosed.git",
        "support": "https://github.com/LSPosed/LSPosed/issues",
        "donate": ""
      },
      "versions": [
        {
          "timestamp": 1673882223.0,
          "version": "v1.8.6 (6712)",
          "versionCode": 6712,
          "zipUrl": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
          "changelog": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
        }
      ]
    }
  ]
}
```

### version 0
```json
{
  "name": "{name}",
  "timestamp": 1692439602.46997,
  "modules": [
    {
      "id": "zygisk_lsposed",
      "name": "Zygisk - LSPosed",
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "author": "LSPosed Developers",
      "description": "Another enhanced implementation of Xposed Framework. Supports Android 8.1 ~ 13. Requires Magisk 24.0+ and Zygisk enabled.",
      "license": "GPL-3.0",
      "states": {
        "zipUrl": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
        "changelog": "{base_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
      }
    }
  ]
}
```
