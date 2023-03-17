# Magisk Modules Repo Util

- This util is to build module repository for [MRepo](https://github.com/ya0211/MRepo)
- `sync` is a python package

## cli.py
``` 
usage: cli.py [-h] [-r root folder] [-k api token] [-m max file size]
                  [-n username] [-s] [--new-config] [--no-push] [-d]

options:
  -h, --help        show this help message and exit
  -r root folder    default: ../magisk-modules-repo
  -k api token      default: None
  -m max file size  default: 50.0
  -n username       github username or organization name
  -s, --sync        sync update
  --new-config      create a new config.json
  --no-push         no push to repository
  -d, --debug       debug mode
```

## [config.json](template/config.json)
```json
{
  "repo_name": "required",
  "repo_url": "required",
  "repo_branch": "required for git",
  "sync_mode": "required",
  "max_num_module": "optional",
  "show_log": "optional",
  "log_dir": "optional"
}
```
- `repo_name`: the name of your magisk module repository
- `repo_url`: this field need to end with `/`
- `repo_branch`: this field is defined for the git
- `sync_mode`: `git` or `rsync`
- `max_num_module`: the maximum number of keeping old version modules, the default value is `3`
- `show_log`: the default value is `true`. If this field is `false`, the log will never be stored.
- `log_dir`: the default value is `None`. If this field is defined, the log file will be stored in this directory.

## [hosts.json](template/hosts.json)
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
- `id`: the id of the module itself
- `update_to`: the url of [updateJson](https://topjohnwu.github.io/Magisk/guides.html) or zipFile, or the name of zipFile, or the url of a git repository (end with `.git`)
- `license`: the license is this module under
- `changelog`: this field will no be uesed on `updateJson`

### Upload from updateJson
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://lsposed.github.io/LSPosed/release/zygisk.json",
  "license": "GPL-3.0-only"
}
```

### Upload from url
```json
{
  "id": "zygisk_lsposed",
  "update_to": "https://github.com/LSPosed/LSPosed/releases/download/v1.8.6/LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0-only",
  "changelog": "https://lsposed.github.io/LSPosed/release/changelog.md"
}
```

### Upload from local
1. Create a new folder named `local` in `your-repo`
2. Put the zip file (and changelog.md) into `local` 
```json
{
  "id": "zygisk_lsposed",
  "update_to": "LSPosed-v1.8.6-6712-zygisk-release.zip",
  "license": "GPL-3.0-only",
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

## Example
### modules.json
```json
{
  "name": "{repo_name}",
  "timestamp": 1675253784.868081,
  "modules": [
    {
      "id": "zygisk_lsposed",
      "license": "GPL-3.0-only",
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
  "timestamp": 1675253784.868081,
  "versions": [
    {
      "timestamp": 1675253784.868081,
      "version": "v1.8.6 (6712)",
      "versionCode": 6712,
      "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.zip",
      "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.6_(6712)_6712.md"
    }
  ]
}
```
