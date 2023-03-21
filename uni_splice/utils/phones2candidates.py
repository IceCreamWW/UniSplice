from typing import Dict
import time

class Phones2Candidates:
    def __init__(
        self,
        phone_ngrams_set,
        min_ngram: int,
        max_ngram: int,
        stop_after_n_results: int = 2,
        max_time_consumption: int = 120,
    ):
        self.phone_ngrams_set = phone_ngrams_set
        self.min_ngram, self.max_ngram = min_ngram, max_ngram
        self.stop_after_n_results = stop_after_n_results
        self.max_time_consumption = max_time_consumption

    def phones2phone_ngrams(self, phones, start, end, max_ngram):

        phones_ = phones
        phones = phones[start: end]
        if len(phones) == 0:
            return [[]]

        # computed ranges are stored for efficiency
        if len(phones) < self.min_ngram or (
            (start, end) in self.range2ngrams
            and self.range2ngrams[(start, end)] is None
        ):
            return []

        if (start, end) in self.range2ngrams:
            return self.range2ngrams[(start, end)]

        phone_ngrams_list = []
        for n in range(max_ngram, self.min_ngram - 1, -1):
            if self.should_stop_iter:
                break
            for pos in range(0, len(phones) - n + 1):
                if (
                    self.should_stop_iter
                    or len(phone_ngrams_list) >= self.stop_after_n_results
                ):
                    break
                phone_ngram = phones[pos : pos + n]

                if str(tuple(phone_ngram)) in self.phone_ngrams_set[n]:
                    prev_phone_ngrams_list = self.phones2phone_ngrams(
                        phones_, start, start + pos, n - 1
                    )
                    if len(prev_phone_ngrams_list) == 0:
                        continue
                    next_phone_ngrams_list = self.phones2phone_ngrams(
                        phones_, start + pos + n, end, max_ngram
                    )
                    if len(next_phone_ngrams_list) == 0:
                        continue

                    for prev_phone_ngrams in prev_phone_ngrams_list:
                        for next_phone_ngrams in next_phone_ngrams_list:
                            phone_ngrams_list.append(
                                prev_phone_ngrams + [phone_ngram] + next_phone_ngrams
                            )
            if len(phone_ngrams_list) != 0:
                break

        if len(phone_ngrams_list) == 0:
            self.range2ngrams[(start, end)] = None
        else:
            self.range2ngrams[(start, end)] = phone_ngrams_list

        return phone_ngrams_list

    @property
    def should_stop_iter(self):
        return time.time() - self.start > self.max_time_consumption

    def __call__(self, phones):
        self.range2ngrams = dict()
        self.start = time.time()
        phone_ngrams_list = self.phones2phone_ngrams(
            0, len(phones), self.max_ngram, uttid
        )
        return phone_ngrams_list

#         if len(phone_ngrams_list) == 0:
#             return []
#         best_segments_length = min(
#             [len(phone_ngrams) for phone_ngrams in phone_ngrams_list]
#         )
#         best_segments_combinations = [
#             segments
#             for segments in best_segments_combinations
#             if len(segments) == best_segments_length
#         ]
#         return best_segments_combinations
