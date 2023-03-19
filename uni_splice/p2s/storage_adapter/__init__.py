from typing import Union
from pathlib import Path

def adapt(storage: Union[Path, str]):
    storage = Path(storage) if isinstance(storage, str) else storage
    return storage
