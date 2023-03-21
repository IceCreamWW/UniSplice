import random
from pathlib import Path
from typing import List, Union

import numpy as np
from uni_splice.utils import Phones2Candidates, load_audio

from .storage import dict_like_storage


class P2S:
    """
    Provided a database path template, e.g. /path/to/database/{i}.shelve, \
            and a range of n for phone ngram [min_ngram, max_ngram],
    this class will load the phone_ngram2speech_segments mapping \
            from /path/to/database/{i}.shelve, where i is in [min_ngram, max_ngram].

    Example usage:
        >>> p2s = P2S("/path/to/database/{i}.shelve")
        >>> speech = p2s(['HH', 'AA1', 'HH', 'AH0']) # data splicing with phones
        alternatively, you can use:
        >>> p2s = P2S("/path/to/database/{i}.shelve", uttid2candidates="/path/to/uttid2candidates.shelve")
        >>> speech = p2s.uttid2speech('100-121669-0001') # data splicing with precomputed candidates of phone ngrams

    """

    def __init__(
        self,
        database: str,
        min_ngram: int = 1,
        max_ngram: int = 10,
        uttid2candidates: Union[Path, str] = None,
    ):
        """
        Args:
            database: path template to the database, e.g. /path/to/database/{i}.shelve
            min_ngram: minimum n for phone ngrams used for splicing
            max_ngram: maximum n for phone ngrams used for splicing
            uttid2candidates: path to the precomputed uttid2candidates, which is \
                    a mapping from uttid to a list of phone ngrams
        """

        self.min_ngram, self.max_ngram = min_ngram, max_ngram
        self.phone_ngram2speech_segments = {
            n: dict_like_storage(database.format(i=n))
            for n in range(min_ngram, max_ngram + 1)
        }
        self.audio_roots = {
            n: Path(self.phone_ngram2speech_segments[n]["__root__"])
            for n in range(min_ngram, max_ngram + 1)
        }
        self.uttid2candidates = (
            dict_like_storage(self.uttid2candidates)
            if uttid2candidates is not None
            else None
        )
        self.phones2candidates = Phones2Candidates(
            self.phone_ngram2speech_segments, min_ngram, max_ngram
        )

    @property
    def support_confidence_sampling(self):
        return all(
            next(iter(self.phone_ngram2speech_segments[n].values())) > 4
            for n in range(self.min_ngram, self.max_ngram + 1)
        )

    def __call__(
        self, phones: List, sample_speech_by_confidence: bool = False
    ) -> np.ndarray:
        phone_ngrams = random.choice(self.phones2candidates(phones))
        return self.phone_ngrams2speech(phone_ngrams, sample_speech_by_confidence)

    def uttid2speech(
        self, uttid: str, sample_speech_by_confidence: bool = False
    ) -> np.ndarray:

        # sanity check
        assert (
            self.uttid2candidates is not None
        ), "precomputed uttid2candidates does not exist"
        assert (
            uttid in self.uttid2candidates
        ), f"combination for uttid {uttid} has not been computed"

        phone_ngrams = random.choice(self.uttid2candidates[uttid])
        return self.phone_ngrams2speech(phone_ngrams, sample_speech_by_confidence)

    def phone_ngrams2speech(self, phone_ngrams, sample_speech_by_confidence):
        if sample_speech_by_confidence and not self.support_confidence_sampling:
            raise RuntimeError(
                "sample_speech_by_confidence is not supported with the provided database"
            )
        speech_segments = []
        for ngram in phone_ngrams:
            n = len(eval(ngram))
            segments = self.phone_ngram2speech_segments[n][ngram]
            if not sample_speech_by_confidence:
                segment = random.choice(segments)
            else:
                segment = random.choices(segments, weights=[s[3] for s in segments])[0]
            audio_path, start, end = segment[:3]
            rate, wave = load_audio(self.audio_roots[n] / Path(audio_path))
            speech_segment = wave[int(start * rate) : int(end * rate)]
            if speech_segment.max() > 1e-4:
                speech_segment = speech_segment / speech_segment.max() * 0.9
            speech_segments.append(speech_segment)

        synthesis_wave = np.concatenate(speech_segments)
        return synthesis_wave

    def __del__(self):
        for n in range(self.min_ngram, self.max_ngram + 1):
            self.phone_ngram2speech_segments[n].close()
        if self.uttid2candidates is not None:
            self.uttid2candidates.close()
