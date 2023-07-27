import json
import re

from .AttrDict import AttrDict


class JsonIO:
    def write(self, file):
        file.parent.mkdir(parents=True, exist_ok=True)

        with open(file, 'w') as f:
            json.dump(self, f, indent=2)

    @classmethod
    def filter(cls, text):
        return re.sub(r",(?=\s*?[}\]])", "", text)

    @classmethod
    def load(cls, file):
        with open(file, encoding="utf-8", mode="r") as f:
            text = cls.filter(f.read())
            obj = json.loads(text)

        return AttrDict(obj)
