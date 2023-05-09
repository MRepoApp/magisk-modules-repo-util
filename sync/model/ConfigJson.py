from .AttrDict import AttrDict
from .JsonIO import JsonIO


class ConfigJson(AttrDict, JsonIO):
    def _set_default(self):
        default = self.default()
        self.repo_name = self.repo_name or default.repo_name
        self.repo_url = self.repo_url or default.repo_url
        self.max_num = self.max_num or default.max_num
        self.show_log = self.show_log or default.show_log
        self.log_dir = self.log_dir or default.log_dir

    def _set_max_num(self):
        try:
            self.max_num = int(self.max_num)
        except ValueError:
            pass

    def _set_show_log(self):
        if isinstance(self.show_log, str):
            self.show_log = self.show_log.lower() == "true"

    def _set_log_dir(self):
        pass

    @classmethod
    def load(cls, file):
        obj = JsonIO.load(file)
        return ConfigJson(obj)

    @classmethod
    def default(cls):
        return ConfigJson(
            repo_name="Unknown Magisk Repo",
            repo_url="",
            max_num=3,
            show_log=True,
            log_dir=None
        )

    @classmethod
    def filename(cls):
        return "config.json"
