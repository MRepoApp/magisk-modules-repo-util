# Magisk Modules Repo Util

- This is util for [ya0211/magisk-modules-repo](https://github.com/ya0211/magisk-modules-repo)
- `Sync` is a python package

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
- `repo_url`: this field need to end with `/`, it will be used to generate the url for the [modules.json](#modules-json) and [update.json](#update-json)
- `repo_branch`: this field defines which branch all files will be committed to
- `sync_mode`: `git` or `rsync`
- `max_num_module`: the maximum number of keeping old version modules, the default value is `3`
- `show_log`: the default value is `true`. If this field is `false`, the log will never be stored
- `log_dir`: the default value is `None`. If this field is defined, the log file will be stored in this directory

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
- `update_to`: the url of [updateJson](https://topjohnwu.github.io/Magisk/guides.html) or zipFile, or the name of zipFile
- `license`: the license is this module under
- `changelog`: this field has no effect on `updateJson`

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
  "update_to": "https://github.com/LSPosed/LSPosed/releases/download/v1.8.5/LSPosed-v1.8.5-6649-zygisk-release.zip",
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
  "update_to": "LSPosed-v1.8.5-6649-zygisk-release.zip",
  "license": "GPL-3.0-only",
  "changelog": "changelog.md"
}
```

## Example
### modules.json
```json
{
  "name": "{repo_name}",
  "timestamp": "2023-01-15 18:47:58.707099",
  "modules": [
    {
      "id": "zygisk_lsposed",
      "license": "GPL-3.0-only",
      "name": "Zygisk - LSPosed",
      "version": "v1.8.5 (6649)",
      "versionCode": 6649,
      "author": "LSPosed Developers",
      "description": "Another enhanced implementation of Xposed Framework. Supports Android 8.1 ~ 13. Requires Magisk 24.0+ and Zygisk enabled.",
      "updateJson": "{repo_url}modules/zygisk_lsposed/update.json",
      "states": {
        "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.5_(6649)_6649.zip",
        "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.5_(6649)_6649.md"
      }
    }
  ]
}
```

### update.json
```json
{
  "id": "zygisk_lsposed",
  "lastUpdate": "2023-01-15 18:47:58.707099",
  "versions": [
    {
      "timestamp": "2023-01-15 18:47:58.707099",
      "version": "v1.8.5 (6649)",
      "versionCode": 6649,
      "zipUrl": "{repo_url}modules/zygisk_lsposed/v1.8.5_(6649)_6649.zip",
      "changelog": "{repo_url}modules/zygisk_lsposed/v1.8.5_(6649)_6649.md"
    }
  ]
}
```
