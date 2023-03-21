import shelve
from typing import List, Union
from pathlib import Path
from .istorage import IStorage

class ShelveStorage(IStorage):
    def __init__(self, path: Union[Path, str]):
        self.mapping = shelve.open(path)

    def __getitem__(self, key)->List:
        return self.mapping[key]

    def __len__(self):
        return len(self.mapping)

    def close(self):
        self.mapping.close()
