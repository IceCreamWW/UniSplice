from typing import Union
from pathlib import Path
from .shelve_storage import ShelveStorage

def dict_like_storage(storage: Union[Path, str]):
    storage = Path(storage)
    if storage.suffix == ".shelve":
        return ShelveStorage(storage)
    raise NotImplementedError("Only shelve storage is supported now.")


class Uttid2Candidates:
    def __init__(self, tokendb, min_ngram, max_ngram, max_combinations_per_iter=2, max_time_consumption=1):
        self.tokendb = tokendb
        self.min_ngram = min_ngram
        self.max_ngram = max_ngram
        self.max_combinations_per_iter = max_combinations_per_iter
        self.max_time_consumption = max_time_consumption

    def __get_best_segments_combinations(self, start, end, max_ngram, uttid=None):

        tokens_ = self.tokens[start:end]
        if len(tokens_) == 0:
            return [[]]

        # invalid segments are stored to reduce repeat computation
        # segments combinations are not stored to limit memory consumption
        if len(tokens_) < self.min_ngram or ((start, end) in self.segment2combinations and self.segment2combinations[(start, end)] is None):
            return []

        if (start, end) in self.segment2combinations:
            return self.segment2combinations[(start, end)]

        segments_combinations = []
        for n_token in range(max_ngram, self.min_ngram - 1, -1):
            if self.should_stop_iter:
                break
            for pos in range(0, len(tokens_) - n_token + 1):
                if self.should_stop_iter or len(segments_combinations) >= self.max_combinations_per_iter:
                    break
                token = tokens_[pos:pos+n_token]

                condition = token in self.tokendb[n_token]
                prev_segments_combinations = self.__get_best_segments_combinations(start, start + pos, n_token - 1)
                if len(prev_segments_combinations) == 0:
                    continue
                next_segments_combinations = self.__get_best_segments_combinations(start + pos + n_token, end, max_ngram)
                if len(next_segments_combinations) == 0:
                    continue

                for prev_segment in prev_segments_combinations:
                    for next_segment in next_segments_combinations:
                        segments_combinations.append(prev_segment + [token] + next_segment)
            if len(segments_combinations) != 0:
                break

        if len(segments_combinations) == 0:
            self.segment2combinations[(start, end)] = None
        else:
            self.segment2combinations[(start, end)] = segments_combinations

        return segments_combinations

    @property
    def should_stop_iter(self):
        return time.time() - self.start > self.max_time_consumption

    def __call__(self, tokens, uttid=None):
        self.tokens = tokens
        self.segment2combinations = dict()

        self.start = time.time()
        best_segments_combinations = self.__get_best_segments_combinations(0, len(tokens), self.max_ngram, uttid)
        if len(best_segments_combinations) == 0:
            return []

        best_segments_length = min([len(segments) for segments in best_segments_combinations])
        best_segments_combinations = [segments for segments in best_segments_combinations if len(segments) == best_segments_length]
        return best_segments_combinations


