# Magisk Modules Repo Util

- This util is to build module repository for [MRepo](https://github.com/ya0211/MRepo)
- `sync` is a python package

## Setup
**Please check out the examples below before you start.**
 
1. Create a folder (or a git repository and clone it), for example *your-repo*, clone [util](https://github.com/ya0211/magisk-modules-repo-util.git) into *your-repo* (or add it as a submodule of the git repository).

2. Create a **config.json** in *your-repo/config* by the following two ways: 
    - Write it by yourself
    - Run `cli.py config --new-config`

3. Create **track.json** in *your-repo/modules/{id}* by the following four ways: 
    - Write it by yourself
    - Run `cli.py config --add-module <id update_to license changelog>`
    - Run `cli.py config --module-manager`
    - Run `cli.py github -u <username>`

4. Run `cli.py sync` to sync (or `cli.py sync -p` to sync and push)

## cli.py
``` 
usage: cli.py [-h] [-d] [-r root folder] {sync,config,github} ...

Magisk Modules Repo Util

options:
  -h, --help            show this help message and exit
  -d, --debug           debug mode, unknown errors will be thrown
  -r root folder        default: ../magisk-modules-repo

sub-command:
  {sync,config,github}  sub-command help
    sync                sync modules and push to repository
    config              manage modules and repository metadata
    github              generate track.json(s) from github
```

### cli.py sync
- Sync modules and push to repository
```
usage: cli.py sync [-h] [-r] [-p] [-b branch] [-m max file size]

options:
  -h, --help           show this help message and exit
  -r, --remove-unused  remove unused modules
  -f, --force-update   clear all versions and update modules

git:
  -p, --push           push to git repository
  -b branch            branch for 'git push', default: main
  -m max file size     default: 50.0
```

### cli.py config
- Manage modules and repository metadata
```
usage: cli.py config [-h] [-c] [-m] [-a id update_to license changelog] [-r id [id ...]]

options:
  -h, --help            show this help message and exit
  -c, --new-config      create a new config.json
  -m, --module-manager  interactive module manager
  -a id update_to license changelog, --add-module id update_to license changelog
  -r id [id ...], --remove-module id [id ...]
```

### cli.py github
- Generate track.json(s) from github
- Dependencies: [PyGithub](https://github.com/PyGithub/PyGithub),  [GITHUB_TOKEN](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
```
usage: cli.py github [-h] [-k api token] [-m max file size] -u username

options:
  -h, --help        show this help message and exit
  -k api token      defined in env as 'GITHUB_TOKEN', default: None
  -m max file size  default: 50.0
  -u username       username or organization name
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
│   ├── sync_2023-03-18_16:59:45.038227.log
│   ├── ...
│   └── ...
│
├── modules
│   ├── zygisk_lsposed
│   │   ├── track.json
│   │   ├── update.json
│   │   ├── v1.8.6_(6712)_6712.md
│   │   ├── v1.8.6_(6712)_6712.zip
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
