import shelve
import numpy as np
from typing import Union, List
from pathlib import Path
import random

class ShelveP2S:
    """
    A phonemes-to-speech converter that uses a shelve database.

    """

    def __init__(self, database: Union[Path, str],
                 uttid2phonemes: Union[Path, str] = None):
        self.database = shelve.open(database)
        self.uttid2phonemes = shelve.open(uttid2phonemes) if uttid2phonemes else None

    def phonemes2speech(self, phonemes: List, sample_speech_by_confidence: bool = False):
        raise NotImplementedError


    def uttid2speech(self, uttid: str, sample_speech_by_confidence: bool = False):
        assert self.uttid2phonemes is not None, f"precomputed uttid2phonemes does not exist"
        assert uttid in self.uttid2phonemes, f"combination for uttid {uttid} has not been computed"

        segment_combination = random.choice(self.uttid2combinations[uttid])
        synthesis_segments = []
        for token in segment_combination:
            segment = random.choice(self.token2segments[str(token)])
            uttid, start, end = segment
            rate, wave = self.load_audio(self.uttid2audio[uttid])
            synthesis_segment = wave[int(start * rate) : int(end * rate)]
            if synthesis_segment.max() > 1e-4:
                synthesis_segment = synthesis_segment / synthesis_segment.max() * 0.9
            synthesis_segments.append(synthesis_segment)

        synthesis_wave = np.concatenate(synthesis_segments)
        return synthesis_wave

    def __del__(self):
        self.database.close()
        if self.uttid2phonemes:
            self.uttid2phonemes.close()
