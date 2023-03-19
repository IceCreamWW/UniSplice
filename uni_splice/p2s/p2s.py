from pathlib import Path
from typing import Union, List
import numpy as np
from .storage_adapter import adapt

class P2S:
    """

    """
    def __init__(self, database: Union[Path, str],
                 uttid2phonemes: Union[Path, str] = None):

        self.database = adapt(database)
        self.uttid2phonemes = adapt(self.uttid2phonemes)


    def phonemes2speech(self, phonemes: List, sample_speech_by_confidence: bool = False)->np.ndarray:
        pass

    def uttid2speech(self, uttid: str, sample_speech_by_confidence: bool = False)->np.ndarray:
        pass

    def __del__(self):
        self.database.close()
        self.uttid2phonemes.close()
