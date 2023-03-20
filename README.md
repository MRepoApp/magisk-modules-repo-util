# Magisk Modules Repo Util

- This util is to build module repository for [MRepo](https://github.com/ya0211/MRepo)
- `sync` is a python package

## Setup
**Please check out the examples below before you start.**
 
1. Create a folder (or a git repository and clone it), for example *your-repo*, clone this repository into *your-repo* (or add it as a submodule of the git repository).

2. Create a **config.json** in *your-repo/config* : 
    - Write it by yourself
    - Run `cli.py --new-config`

3. Create a **hosts.json** in *your-repo/config* : 
    - Write it by yourself
    - Run `cli.py --add-module`
    - Run `cli.py -u {username} --no-sync`

4. Run `cli.py` to sync (or `cli.py -p` to sync and push)

## cli.py
 If you want to generate **hosts.json** from github username or organization name, you need to install [pygithub](https://github.com/PyGithub/PyGithub) and define [GIT_TOKEN](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token), otherwise you don't need them.
``` 
usage: cli.py [-h] [-r root folder] [-k api token] [-m max file size] [-u username] [-p] [-b branch] [--new-config] [--add-module] [-d]

options:
  -h, --help        show this help message and exit
  -r root folder    default: ../your-repo
  -k api token      defined in env as 'GIT_TOKEN', default: None
  -m max file size  default: 50.0
  -u username       github username or organization name
  -p, --push        push to git repository
  -b branch         branch for 'git push', default: main
  --new-config      create a new config.json
  --add-module      add a new module to hosts.json
  --no-sync         no sync modules
  -d, --debug       debug mode
```

## config.json
```json
{
  "repo_name": "required",
  "repo_url": "required",
  "max_num": "optional",
  "show_log": "optional",
  "log_dir": "optional"
}
```
| Key | Attribute | Description |
|:-:|:-:|:-:|
| repo_name | required | Name of your module repository |
| repo_url | required | Need to end with `/` |
| max_num | optional | Max number of keeping old version modules, default value is 3 |
| show_log | optional | If false, the log will never be showed and stored,  default value is true |
| log_dir | optional | If defined, the log file will be stored in this directory |

## hosts.json
```json
[
  {
    "id": "required",
    "update_to": "required",
    "license": "optional",
    "changelog": "optional"
  }
]
```
| Key | Attribute | Description |
|:-:|:-:|:-:|
| id | required | Id of the module itself |
| update_to | required | Url of updateJson or zipFile, or the name of zipFile, or the url of a git repository (end with `.git`) |
| license | optional | SPDX ID |
| changelog | optional | No be uesed on updateJson |

### Upload from updateJson
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0"
}
```

### Upload from url
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://github.com/LSPosed/LSPosed/releases/download/v1.8.6/LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0",
  "changelog": "https://lsposed.github.io/LSPosed/release/changelog.md"
}
```

### Upload from local
1. Create a new folder named *local* in *your-repo*
2. Put the zip file (and changelog.md) into *local*
```json
{
  "id": "zygisk_lsposed",
  "update_to": "LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0",
  "changelog": "changelog.md"
}
```

### Upload from git
```json
{
  "id": "busybox-ndk",
  "update_to": "https://github.com/Magisk-Modules-Repo/busybox-ndk.git",
  "license": "",
  "changelog": ""
}
```

## For developer
```
├── config
│   ├── hosts.json
│   └── config.json
├── json
│   └── modules.json
├── log
│   └── sync_2023-03-18_16:59:45.038227.log
├── modules
│   └── zygisk_lsposed
│       ├── track.json
│       ├── update.json
│       ├── v1.8.6_(6712)_6712.md
│       └── v1.8.6_(6712)_6712.zip
└── util
```
### modules.json
```json
{
  "name": "{repo_name}",
  "timestamp": 1679036889.233794,
  "modules": [
    {
      "id": "zygisk_lsposed",
      "license": "GPL-3.0",
      "name": "Zygisk - LSPosed",
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "author": "LSPosed Developers",
      "description": "Another enhanced implementation of Xposed Framework. Supports Android 8.1 ~ 13. Requires Magisk 24.0+ and Zygisk enabled.",
      "states": {
        "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
        "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
      }
    }
  ]
}
```

### update.json
```json
{
  "id": "zygisk_lsposed",
  "timestamp": 1679025505.129431,
  "versions": [
    {
      "timestamp": 1679025505.129431,
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
      "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
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
  "added": 1679025505.129431,
  "last_update": 1679025505.129431,
  "versions": 1
}
```
