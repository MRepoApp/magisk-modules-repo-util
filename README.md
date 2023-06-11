# Magisk Modules Repo Util

- This util is to build module repository for [MRepo](https://github.com/ya0211/MRepo)
- `sync` is a python package

## Getting Started
### Initialize repository
You should create a folder, or a git repository and clone it, for example `your-repo`, and clone util by running
```shell
$ git clone -b main https://github.com/ya0211/magisk-modules-repo-util.git util
```
or add it as a submodule of the git repository, use
```shell
$ git submodule add https://github.com/ya0211/magisk-modules-repo-util.git util
```

### Create config.json
You can write it to `your-repo/config/config.json` by yourself, or use
```shell
$ cli.py config --stdin << EOF
{
  "repo_name": "Your Magisk Repo",
  "repo_url": "https://you.github.io/magisk-modules-repo/",
  "max_num": 3,
  "show_log": true,
  "log_dir": "log"
}
EOF
```
or 
```shell
$ cli.py config --write repo_name="Your Magisk Repo" repo_url="https://you.github.io/magisk-modules-repo/" max_num=3 show_log=true log_dir="log"
```

### Create track.json
You can write it to `your-repo/modules/{id}/track.json` by yourself, or use
```shell
$ cli.py module --stdin << EOF
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0"
}
EOF
```
or
```shell
$ cli.py module --add id="zygisk_lsposed" update_to="https://lsposed.github.io/LSPosed/release/zygisk.json" license="GPL-3.0"
```
If you want to generate track.json from github repositories, use
```shell
$ cli.py github --user-name <github-user-name> --api-token=<github-api-token>
```
> About how to create an api token, you can refer to [Managing your personal access tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

### Start Sync
```shell
$ cli.py sync 
```

## cli.py
```
$ cli.py --help
usage: cli.py [-h] [-v] [-V] command ...

Magisk Modules Repo Util

positional arguments:
  command
    config            Modify config values of repository.
    module            Magisk module tracks utility.
    github            Generate track(s) from github.
    sync              Sync modules and push to repository.
    index             Generate modules.json from local.

options:
  -h, --help          Show this help message and exit.
  -v, --version       Show util version and exit.
  -V, --version-code  Show util version code and exit.
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

## track.json
```json
{
  "id": "required",
  "update_to": "required",
  "license": "optional",
  "changelog": "optional"
}
```
| Key | Attribute | Description |
|:-:|:-:|:-:|
| id | required | Id of the module itself |
| update_to | required | Url of updateJson or zipFile, or file name of zipFile, or url of a git repository (end with `.git`) |
| license | optional | SPDX ID |
| changelog | optional | Url of changelog.md or file name of changelog.md (markdown is the best, simple text is also ok, **no html**) |

### Update from updateJson
This is for those modules that provide [updateJson](https://topjohnwu.github.io/Magisk/guides.html#moduleprop). 

```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0"
}
```

### Update from local updateJson
The `update_to` requires a relative directory of *local*.
1. Create a new folder named *local* in *your-repo*
2. Put the update.json into *local*

```json
{
  "id": "zygisk_lsposed",
  "update_to": "zygisk.json",
  "license": "GPL-3.0"
}
```

### Update from url
This is for those have a same url to release new modules.
- If url has changed, you have to edit it.

```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://github.com/LSPosed/LSPosed/releases/download/v1.8.6/LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0",
  "changelog": "https://lsposed.github.io/LSPosed/release/changelog.md"
}
```

### Update from git
This is for those you can **get the module by packaging all files** in the repository, such as [Magisk-Modules-Repo](https://github.com/Magisk-Modules-Repo) and [Magisk-Modules-Alt-Repo](https://github.com/Magisk-Modules-Alt-Repo). 
- If you are looking how to add *Magisk-Modules-Alt-Repo* to *MRepo*, you can refer to [ya0211/magisk-modules-alt-repo](https://github.com/ya0211/magisk-modules-alt-repo).

```json
{
  "id": "busybox-ndk",
  "update_to": "https://github.com/Magisk-Modules-Repo/busybox-ndk.git",
  "license": "",
  "changelog": ""
}
```

### Update from local zip
The `update_to` requires a relative directory of *local*.
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

## For developer
```
your-repo
├── config
│   └── config.json
│
├── json
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
        "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.6_6712.zip",
        "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.6_6712.md"
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
      "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.6_6712.zip",
      "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.6_6712.md"
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
